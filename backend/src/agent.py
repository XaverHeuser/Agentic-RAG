import logging

import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)

from .config import Config


# Initialize logger
logger = logging.getLogger(__name__)


class Agent:
    """Orchestrates the LLM reasoning loop and tool execution."""

    def __init__(self, config: Config, search_func):
        """Sets up Vertex AI, tools, and the generative model."""
        self.config = config
        self.search_func = search_func

        vertexai.init(project=self.config.PROJECT_ID, location=self.config.LOCATION)

        search_tool = Tool(
            function_declarations=[
                FunctionDeclaration(
                    name='search_docs',
                    description='Sucht in Universitätsdokumenten. Nutze prägnante, akademische Suchbegriffe. '
                    'Variiere die Begriffe (z.B. "Syntax", "Datentypen", "Grundlagen"), um bessere Ergebnisse zu erzielen.',
                    parameters={
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string', 'description': 'Search term'}
                        },
                        'required': ['query'],
                    },
                )
            ]
        )
        generation_config = {
            'temperature': 0.1,  # Low -> Strict, less creativity
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 4096,
        }

        self.model = GenerativeModel(
            model_name=self.config.AGENT_MODEL,
            generation_config=generation_config,
            tools=[search_tool],
            system_instruction=(
                'Du bist der ScholarAgent, ein präziser akademischer Assistent. Deine Aufgabe ist es, Fachfragen ausschließlich auf Basis der bereitgestellten Dokumente zu beantworten.\n\n'
                'VERHALTENSREGELN:\n'
                '1. GRÜNDLICHKEIT: Analysiere JEDEN bereitgestellten Text-Chunk (Source) intensiv. Wenn ein Begriff oder Konzept in den Chunks vorkommt, erkläre ihn mit allen verfügbaren Details, Beispielen und Definitionen aus dem Text.\n'
                "2. KEINE ABKÜRZUNGEN: Antworte niemals nur mit 'Das Thema wird erwähnt'. Wenn Informationen vorhanden sind, musst du sie inhaltlich wiedergeben.\n"
                '3. STRUKTUR: Nutze Bulletpoints und fettgedruckte Begriffe für eine bessere Lesbarkeit von Konzepten.\n'
                '4. EHRLICHKEIT: Nur wenn die bereitgestellten Chunks absolut keine inhaltliche Definition bieten (z.B. nur ein Inhaltsverzeichnis ohne Text), gib an, dass die Details fehlen.\n\n'
                'REGLER FÜR ZITATE:\n'
                "1. Jede faktische Aussage MUSS direkt im Text mit einer IEEE-Zitation belegt werden, z.B.: 'JavaScript ist asynchron [1, S. 14].'\n"
                "2. Erstelle am Ende eine Liste 'Verwendete Quellen' im Format: [Nummer] Dateiname, Seitenzahl.\n"
                'Zusätzlich: Beziehe dich auf den bisherigen Chat-Verlauf, falls der Nutzer Folgefragen stellt.'
            ),
        )

        # Initialize a persistent chat session
        self.chat_session = self.model.start_chat(history=[], response_validation=False)
        logger.info('Agent initialized with persistent ChatSession.')

    def _log_usage(self, response):
        """Debug logs for token counting."""
        usage = response.usage_metadata
        logger.debug(
            f'Token Usage -> Prompt: {usage.prompt_token_count}, '
            f'Response: {usage.candidates_token_count}, '
            f'Total: {usage.total_token_count}'
        )

    def _summarize_history(self):
        """Reduces the token load by compressing older parts of the conversation."""
        history = self.chat_session.history
        if not history:
            logger.debug('No chat history')
            return

        token_count = self.model.count_tokens(history).total_tokens
        logger.debug(f'History Check: {len(history)} items, {token_count} tokens.')

        if token_count > self.config.MAX_HISTORY_TOKENS:
            logger.debug(f'Threshold reached ({token_count} tokens). Summarizing...')

            # Split history: parts to summarize and parts to keep raw
            split_idx = max(0, len(history) - self.config.MIN_RAW_TURNS_TO_KEEP)
            to_summarize = history[:split_idx]
            keep_raw = history[split_idx:]

            # Request summary from the model
            summary_response = self.model.generate_content([
                *to_summarize,
                Content(
                    role='user', parts=[Part.from_text(self.config.SUMMARY_PROMPT)]
                ),
            ])

            # Rebuild history: [Summary Marker] + [Summary Text] + [Raw Context]
            new_history = [
                Content(
                    role='user',
                    parts=[
                        Part.from_text('Bisheriger Gesprächskontext (Zusammenfassung):')
                    ],
                ),
                Content(role='model', parts=[Part.from_text(summary_response.text)]),
                *keep_raw,
            ]

            self.chat_session.history[:] = new_history
            logger.debug('Chat history has been successfully summarized.')

    def ask(self, question: str) -> str:
        """Sends a question to the LLM and handles potential tool calls recursively."""
        logger.info(f'Processing user question: {question}')

        try:
            self._summarize_history()

            response = self.chat_session.send_message(question)
            if not response.candidates or not response.candidates[0].content.parts:
                return 'Entschuldigung, ich konnte keine Antwort generieren. Bitte formuliere die Frage präziser.'
            self._log_usage(response)

            # Tool execution loop (Recursive)
            while response.candidates[0].content.parts[0].function_call:
                # Collect all calls for the query
                function_calls = [
                    part.function_call
                    for part in response.candidates[0].content.parts
                    if part.function_call
                ]

                responses_parts = []
                for call in function_calls:
                    if call.name == 'search_docs':
                        query_args = call.args['query']

                        # Execute the actual search
                        result_context = self.search_func(query_args)

                        # Feed the search results back to the LLM
                        responses_parts.append(
                            Part.from_function_response(
                                name=call.name, response={'content': result_context}
                            )
                        )
                # Send tool results back to the SAME session
                response = self.chat_session.send_message(responses_parts)
                self._log_usage(response)

            logger.debug('Final answer generated by the agent')
            return response.text

        except Exception as e:
            logger.error(f'Error calling LLM: {str(e)}')
            return 'Es gab ein technisches Problem bei der Verarbeitung.'

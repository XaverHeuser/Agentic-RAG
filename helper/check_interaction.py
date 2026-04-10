import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. SETUP & KONFIGURATION
load_dotenv()
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = 'us-central1'
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 2. DAS RETRIEVAL-SYSTEM (Dein Motor)
def execute_retrieval(query: str):
    """Dies ist die Brücke: Gemini ruft diese Funktion auf."""
    
    # Die Embeddings müssen exakt die gleichen sein wie beim Ingest!
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        version="v1beta",
        project=PROJECT_ID,
        location=LOCATION,
        vertexai=True,
    )

    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="uni_docs"
    )

    print(f"   [RETRIEVAL ACTIVE] Suche Chunks für: '{query}'...")
    results = db.similarity_search(query, k=3)
    
    # Wir bereiten den Text für Gemini vor
    context = ""
    for doc in results:
        page = doc.metadata.get('page', 'unbekannt')
        context += f"\n--- Seite {page} ---\n{doc.page_content}\n"
    
    return context

# 3. TOOL & MODEL DEFINITION
search_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="search_university_docs",
            description="Durchsucht die Uni-Skripte nach Informationen zu einem Thema.",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Suchbegriff"}},
                "required": ["query"],
            },
        )
    ]
)

model = GenerativeModel(
    "gemini-2.5-flash",
    tools=[search_tool],
    system_instruction="Du bist der ScholarAgent. Nutze das Tool für jede Fachfrage. Nenne Seitenzahlen."
)

# 4. DER AGENTEN-LOOP
def ask_agent(question: str):
    chat = model.start_chat()
    response = chat.send_message(question)

    # ReAct-Logik: Falls Gemini ein Tool will...
    if response.candidates[0].content.parts[0].function_call:
        call = response.candidates[0].content.parts[0].function_call
        
        if call.name == "search_university_docs":
            # Hier bauen wir dein Retrieval ein!
            retrieved_text = execute_retrieval(call.args["query"])
            
            # Ergebnis zurückgeben
            response = chat.send_message(
                Part.from_function_response(
                    name=call.name,
                    response={"content": retrieved_text}
                )
            )
    
    print(f"\n🤖 ScholarAgent:\n{response.text}")

if __name__ == "__main__":
    ask_agent("Was muss ich über die Android Platform wissen?")

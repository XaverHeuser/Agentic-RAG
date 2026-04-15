from dataclasses import dataclass
import logging
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    """Central configuration for the Agent Application."""

    PROJECT_ID: str = os.getenv('GCP_PROJECT_ID', 'scholaragentrag')
    LOCATION: str = 'us-central1'
    DB_DIR: str = './chroma_db'
    COLLECTION_NAME: str = 'uni_docs'
    EMBEDDING_MODEL: str = 'models/gemini-embedding-001'
    AGENT_MODEL: str = 'gemini-2.5-flash'

    MAX_HISTORY_TOKENS: int = 10000
    MIN_RAW_TURNS_TO_KEEP: int = 6
    SUMMARY_PROMPT: str = (
        'Fasse den bisherigen Gesprächsverlauf kurz und prägnant als Stichpunkte zusammen.'
        'Bewahre alle akademischen Fakten, Definitionen und bereits genannten Quellen.'
    )

    LOG_FILE: str = 'agent.log'
    LOG_LEVEL: int = logging.INFO

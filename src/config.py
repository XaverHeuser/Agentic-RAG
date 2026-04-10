from dataclasses import dataclass  # TODO: Check out
import logging
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)  # TODO: Check out
class Config:
    """Central configuration for the Agent Application."""

    PROJECT_ID: str = os.getenv('GCP_PROJECT_ID', 'scholaragentrag')
    LOCATION: str = 'us-central1'
    DB_DIR: str = './chroma_db'
    COLLECTION_NAME: str = 'uni_docs'
    EMBEDDING_MODEL: str = 'models/gemini-embedding-2-preview'
    AGENT_MODEL: str = 'gemini-2.5-flash'
    LOG_FILE: str = 'agent.log'
    LOG_LEVEL: int = logging.INFO

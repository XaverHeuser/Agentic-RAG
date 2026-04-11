import logging
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Config


# Initialize logger
logger = logging.getLogger(__name__)


class AgentStore:
    """Handles vector database operations including ingestion and semantic search."""

    def __init__(self, config: Config):
        """Initializes the vector store with embeddings and ChromaDB connection."""
        self.config = config
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.config.EMBEDDING_MODEL,
            version='v1beta',
            project=self.config.PROJECT_ID,
            location=self.config.LOCATION,
            vertexai=True,
        )
        self.vector_db = Chroma(
            persist_directory=self.config.DB_DIR,
            embedding_function=self.embeddings,
            collection_name=self.config.COLLECTION_NAME,
        )
        logger.info('AgentStore initialized successfully')

        # Map extensions to loader classes
        self.LOADER_MAPPING = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
        }

    def ingest_path(self, path_str=str) -> None:
        """
        Recursively processes documents from a given path and load them into the vector store.

        Args:
            path_str (str): The local file path to process.

        Process:
            1. Identifies files based on `LOADER_MAPPING` (.pdf, .docx, .txt).
            2. Loads document content using LangChain loaders.
            3. Splits text into 1000-character chunks with 100-character overlap.
            4. Generates embeddings using Google Generative AI.
            5. Upserts chunks into the Chroma vector store.
        """
        path = Path(path_str)

        extensions = self.LOADER_MAPPING.keys()
        loader_files = []

        # Find files with support document types selected in LOADER_MAPPING
        if path.is_dir():
            for ext in extensions:
                loader_files.extend(list(path.rglob(f'*{ext}')))
        elif path.suffix in extensions:
            loader_files = [path]

        if not loader_files:
            logger.warning(f'No supported files found at path: {path_str}')
            return

        # Initialize splitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

        for file in loader_files:
            logger.info(f'Starting ingestion for: {file.name}')
            try:
                # Dynamically select the loader class based on file type
                loader_class = self.LOADER_MAPPING.get(file.suffix)
                if not loader_class:
                    continue

                # load data and create chunks
                loader = loader_class(str(file))
                data = loader.load()
                chunks = splitter.split_documents(data)
                if not chunks:
                    continue

                # Add chunks to vector db
                self.vector_db.add_documents(chunks)

                logger.info(
                    f'Successfully added {len(chunks)} chunks from {file.name} to vector db'
                )
            except Exception as e:
                logger.error(f'Failed to ingest {file.name}: {str(e)}')

    def search(self, query: str, k: int = 3) -> str:
        """Performs a similarity search and returns a formatted context string."""
        logger.debug(f'Performing vector search for query: {query}')
        results = self.vector_db.similarity_search(query, k=k)

        if not results:
            logger.warning(f'No relevant documents found for query: {query}')
            return 'No relevant information found in the docs for this specific query.'

        context = ''
        for doc in results:
            name = os.path.basename(doc.metadata.get('source', 'Unknown'))
            page = int(doc.metadata.get('page', 0)) + 1
            context += f'\n--- Source: {name} | Page: {page} ---\n{doc.page_content}\n'

        logger.info(f'Retrieved {len(results)} chunks for the agent')
        return context

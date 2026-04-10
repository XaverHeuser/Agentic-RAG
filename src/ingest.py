import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import vertexai

from langchain_chroma import Chroma

load_dotenv()

# GCP Konfiguration aus deiner .env oder Umgebung
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = 'us-central1'

# Vertex AI Initialisierung
vertexai.init(project=PROJECT_ID, location=LOCATION)


def process_file(file_path, db, text_splitter):
    """Verarbeitet eine einzelne PDF-Datei."""
    try:
        print(f"Verarbeite: {file_path.name}...")
        loader = PyPDFLoader(str(file_path))
        data = loader.load()
        
        chunks = text_splitter.split_documents(data)
        print(chunks[0])
        print(chunks[1])
        print(chunks[2])
        print(chunks[-1])
        print(chunks[-2])

        print("Starte schrittweise Indizierung...")
        for i, chunk in enumerate(chunks):
            try:
                db.add_documents([chunk])
                if (i + 1) % 5 == 0:
                    print(f"Fortschritt: {i + 1}/{len(chunks)} Chunks verarbeitet...")
            except Exception as e:
                print(f"❌ Fehler bei Chunk {i}: {e}")
                continue # Weitermachen bei Fehlern

        print(f"✅ Fertig! {len(chunks)} Chunks sind jetzt in der ChromaDB.")
    except Exception as e:
        print(f"Fehler bei {file_path.name}: {e}")


def start_ingestion(input_path):
    """This function ..."""

    # Create embeddings using Google Generative AI
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        version="v1beta",
        project=PROJECT_ID,
        location=LOCATION,
        vertexai=True,
    )
    
    # Initialize ChromaDB
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="uni_docs"
    )

    # Initialize Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    path = Path(input_path)
    print(10* '=')
    print(f"Starte Ingestion für: {path.absolute()}")

    if path.is_file():
        if path.suffix.lower() == '.pdf':
            process_file(path, db, text_splitter)
    
    elif path.is_dir():
        print(f"Durchsuche Ordner: {path.absolute()}")
        # .rglob('*') findet alles rekursiv in Unterordnern
        for file in path.rglob('*.pdf'):
            process_file(file, db, text_splitter)

    print("\n🚀 Ingestion-Prozess beendet.")

if __name__ == "__main__":
    target = "./data" 
    start_ingestion(target)

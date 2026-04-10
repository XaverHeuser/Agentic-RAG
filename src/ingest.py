import os
import shutil
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


def start_ingestion(pdf_path):
    # 1. Clean Start: Alten Datenbank-Ordner löschen
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        print("Alte Datenbank gelöscht.")

    # 2. PDF laden & splitten
    loader = PyPDFLoader(pdf_path)
    data = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    print(f"PDF geladen. {len(chunks)} Chunks erzeugt.")

    # 3. Embeddings initialisieren
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        version="v1beta",
        project=PROJECT_ID,
        location=LOCATION,
        vertexai=True,
    )
    
    # 4. ChromaDB initialisieren
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="uni_docs"
    )

    # 5. Einzel-Upload (Sicherheits-Strategie)
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

if __name__ == "__main__":
    start_ingestion("./data/Mobile Anwendungen - VL1 - Tel.pdf")
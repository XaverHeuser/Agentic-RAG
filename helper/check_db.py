import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def inspect_database():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        version="v1beta"
    )

    if not os.path.exists("./chroma_db"):
        print("❌ Datenbank-Ordner existiert nicht. Bitte zuerst ingest.py ausführen.")
        return

    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="uni_docs"
    )

    # Daten abrufen
    content = db.get()
    
    print("--- Datenbank Statistik ---")
    print(f"Anzahl gespeicherter Einträge: {len(content['ids'])}")
    
    if len(content['ids']) > 0:
        print("\n--- Beispiel-Eintrag (Erster Chunk) ---")
        print(f"ID: {content['ids'][1]}")
        print(f"Metadaten: {content['metadatas'][1]}")
        print(f"Text-Vorschau: {content['documents'][1][:1000]}...")
    else:
        print("Die Datenbank ist leer.")

if __name__ == "__main__":
    inspect_database()
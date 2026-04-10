import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# GCP Konfiguration aus deiner .env oder Umgebung
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = 'us-central1'

def test_search(query):
    # 1. Wir brauchen die gleiche "Sprach-Engine" wie beim Speichern
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        version="v1beta",
        project=PROJECT_ID,
        location=LOCATION,
        vertexai=True,
    )

    # 2. Verbindung zur bestehenden Datenbank herstellen
    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="uni_docs"
    )

    print(f"\n🔍 Suche in den Uni-Unterlagen nach: '{query}'")
    
    # 3. Die Suche ausführen
    # k=3 bedeutet: Gib mir die 3 relevantesten Textstücke zurück
    results = db.similarity_search(query, k=3)

    print(f"\n✅ {len(results)} relevante Stellen gefunden:\n")
    print("-" * 50)
    
    for i, doc in enumerate(results):
        print(f"Ergebnis {i+1} (Seite {doc.metadata.get('page', 'unbekannt')}):")
        print(f"{doc.page_content[:300]}...") # Zeige nur den Anfang
        print("-" * 50)

if __name__ == "__main__":
    # Teste es mit einer Frage, die definitiv in deinem PDF beantwortet wird!
    test_search("Was ist Expo?")
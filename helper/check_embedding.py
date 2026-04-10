import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Wir nutzen das neue 2026er SDK direkt für maximale Transparenz
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def test_single_embedding():
    test_text = "Informatik ist die Wissenschaft der systematischen Verarbeitung von Informationen."
    
    print(f"Sende Text an Gemini: '{test_text}'")
    
    try:
        # Wir nutzen das Modell aus deiner Liste
        response = client.models.embed_content(
            model="models/gemini-embedding-2-preview",
            contents=test_text
        )
        
        # Ein Vektor ist mathematisch gesehen ein Punkt in einem n-dimensionalen Raum
        vector = response.embeddings[0].values
        
        print("\n✅ Erfolg!")
        print(f"Vektor-Dimensionen: {len(vector)}")
        print(f"Vektor-Vorschau (erste 5 Werte): {vector[:5]}")
        
    except Exception as e:
        print(f"❌ Fehler bei der Vektorisierung: {e}")

if __name__ == "__main__":
    test_single_embedding()
import google.auth
from google.cloud import aiplatform

def check_iam():
    credentials, project = google.auth.default()
    print(f"--- Identitäts-Check ---")
    print(f"Erkanntes Projekt: {project}")
    print(f"Account-E-Mail: {credentials.service_account_email if hasattr(credentials, 'service_account_email') else 'User-Account'}")
    
    try:
        # Versuche eine minimale Aktion auf Vertex AI
        from vertexai.generative_models import GenerativeModel
        import vertexai
        vertexai.init(project=project, location="us-central1")
        model = GenerativeModel("gemini-1.5-flash")
        print("✅ Verbindung zur Vertex AI Plattform steht!")
    except Exception as e:
        print(f"❌ Zugriff verweigert: {e}")

if __name__ == "__main__":
    check_iam()
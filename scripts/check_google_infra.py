import os
import sys

import google.auth
import vertexai
from vertexai.generative_models import GenerativeModel


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def verify_infrastructure():
    """Validates local credentials and Vertex AI API access."""
    config = Config()

    print('--- Infrastructure Health Check ---')

    # Check Identity
    try:
        credentials, project = google.auth.default()
        print(f'Detected Project: {project}')

        # Check if project matches config
        if project != config.PROJECT_ID:
            print(
                f'Active GCP project ({project}) differs from Config ({config.PROJECT_ID})'
            )

        account = (
            credentials.service_account_email
            if hasattr(credentials, 'service_account_email')
            else 'Personal User Account'
        )
        print(f'Active Identity:  {account}')

    except Exception as e:
        print(f'Failed to detect GCP Credentials: {e}')
        return

    # Check Vertex AI Connection
    try:
        vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)
        # Attempt to initialize the model (lazy loading check)
        model = GenerativeModel(config.AGENT_MODEL)

        # perform a tiny generation test to confirm the API is actually enabled and reachable
        print(f'Connecting to model: {config.AGENT_MODEL}...')
        # Use a very short prompt to minimize cost/tokens
        model.generate_content('ping')

        print('Vertex AI: Connection established and API is active.')

    except Exception as e:
        print(f'Vertex AI Error: {e}')


if __name__ == '__main__':
    verify_infrastructure()

#!/usr/bin/env python3
"""
Configuration example for AI Video Generator
Copy this file to config.py and update with your values
"""

import os

# Google Cloud Project Configuration
PROJECT_ID = "veo-testing"
LOCATION_ID = "us-central1"
MODEL_ID = "veo-3.0-generate-preview"

# Authentication Options - Choose ONE:

# Option 1: Service Account Key File (RECOMMENDED)
# Download service account key and set the path
SERVICE_ACCOUNT_KEY_PATH = "/path/to/your/service-account-key.json"

# Option 2: API Key (Limited support)
API_KEY = "your-api-key-here"


# Option 3: Use environment variables
def setup_environment():
    """Set up environment variables for authentication."""

    # Basic configuration
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION_ID
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

    # Authentication - uncomment ONE of the following:

    # Service Account (recommended)
    if SERVICE_ACCOUNT_KEY_PATH and os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY_PATH
        print(f"🔑 Using service account: {SERVICE_ACCOUNT_KEY_PATH}")

    # API Key (if supported)
    elif API_KEY:
        os.environ["GOOGLE_API_KEY"] = API_KEY
        print("🔑 Using API key authentication")

    # Optional: GCS bucket for output storage
    # os.environ['GCS_BUCKET'] = 'your-bucket-name'


if __name__ == "__main__":
    print("This is a configuration example file.")
    print("Copy this to config.py and update with your values.")
    print("\nThen import it in your main script:")
    print("from config import setup_environment")
    print("setup_environment()")

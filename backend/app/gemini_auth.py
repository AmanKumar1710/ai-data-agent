from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_google_oauth_token(service_account_path):
    SCOPES = [
        # "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/generative-language"
    ]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token

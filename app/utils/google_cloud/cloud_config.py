from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from google.auth.transport.requests import Request
from config.settings import GOOGLE_SCOPES
import streamlit as st

client_config = {
    "installed": {
        "client_id": st.secrets.installed.client_id,
        "project_id": st.secrets.installed.project_id,
        "auth_uri": st.secrets.installed.auth_uri,
        "token_uri": st.secrets.installed.token_uri,
        "auth_provider_x509_cert_url": st.secrets.installed.auth_provider_x509_cert_url,
        "client_secret": st.secrets.installed.client_secret,
        "redirect_uris": st.secrets.installed.redirect_uris
    }
}


def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GOOGLE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, GOOGLE_SCOPES)
            creds = flow.run_console()
            # creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
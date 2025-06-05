from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.google_cloud.cloud_config import get_credentials
import streamlit as st


@tool
def list_emails_tool(limit: str, label_ids: list = None) -> str:
    """
    Retrieve and list the latest emails from the Gmail inbox,
    optionally filtered by label IDs.

    Parameters:
    - limit (str): The maximum number of emails to retrieve. (Default will be 5)
    - label_ids (list): An optional list of label IDs to filter emails.

    Returns:
    - str: A formatted string containing the latest emails or an error message.
    """
    print("Used read email tool")

    try:
        emails = list_emails(limit, label_ids)
        if not emails:
            return "No emails found in the inbox with the specified criteria."
        return "\n\n".join(emails)
    except Exception as e:
        print(f"Failed to retrieve emails: {str(e)}")
        return f"Failed to retrieve emails: {str(e)}"

def list_emails(limit: str, label_ids: list = None) -> list[str]:
    """
    Retrieves a list of emails from the Gmail inbox.
    Don't ask for labels if user only asks for emails.
    Use the ids if user talks about specific types e.g. drafts or spam etc.
    Don't ask the user too much and use the context.

    Parameters:
    - limit (str): The maximum number of emails to retrieve.
    - label_ids (list): An optional list of label IDs to filter emails.
                       If None, defaults to ['INBOX'].
    it can be [
        'INBOX',
        'SPAM',
        'TRASH',
        'UNREAD',
        'STARRED',
        'IMPORTANT',
        'SENT',
        'DRAFT',
    ]

    Returns:
    - list[str]: A list of formatted strings, each representing an email summary.
    """
    try:
        creds = get_credentials() # Assuming this function is defined and provides valid credentials
        service = build('gmail', 'v1', credentials=creds)

        # Set default labels if none are provided
        if label_ids is None:
            label_ids = ['INBOX']

        results = service.users().messages().list(
            userId='me',
            maxResults=int(limit),
            labelIds=label_ids
        ).execute()

        messages = results.get('messages', [])
        email_summaries = []
        for msg in messages:
            msg_detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()
            headers = msg_detail.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
            email_summaries.append(f"From: {sender}\nSubject: {subject}")
        return email_summaries
    except HttpError as error:
        print(f'An error occurred: {error}')
        return [f'An error occurred: {error}']

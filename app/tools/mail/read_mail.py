import base64

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

        # messages = results.get('messages', [])
        # email_summaries = []
        # for msg in messages:
        #     msg_detail = service.users().messages().get(
        #         userId='me',
        #         id=msg['id'],
        #         format='metadata',
        #         metadataHeaders=['Subject', 'From','Content']
        #     ).execute()
        #     headers = msg_detail.get('payload', {}).get('headers', [])
        #     subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        #     sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
        #     content = next((h['value'] for h in headers if h['name'] == 'Content'), '(Unknown Sender)')
        #
        #     email_summaries.append(f"From: {sender}\nSubject: {subject}\nContent: {content}")
        # return email_summaries

        messages = results.get('messages', [])
        email_summaries = []

        for msg in messages:
            msg_detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                # Change format to 'full' to get the entire message payload, including the body
                format='full'
            ).execute()

            payload = msg_detail.get('payload')
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')

            email_body = ""
            # Emails can have multiple parts (e.g., plain text, HTML, attachments)
            parts = payload.get('parts')

            if parts:
                for part in parts:
                    mime_type = part.get('mimeType')
                    body = part.get('body')

                    # Prioritize plain text content
                    if mime_type == 'text/plain' and body and 'data' in body:
                        data = body['data']
                        decoded_bytes = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        email_body = decoded_bytes.decode('UTF-8')
                        break  # We found the plain text body, no need to check further parts
                    elif mime_type == 'text/html' and body and 'data' in body:
                        # If no plain text, take the HTML. You might want to strip HTML tags later.
                        data = body['data']
                        decoded_bytes = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        email_body = decoded_bytes.decode('UTF-8')
                        # Don't break here, in case there's a plain text version later in the parts
            elif payload.get('body') and 'data' in payload['body']:
                # Handle cases where the email body is directly in the payload (simpler emails)
                data = payload['body']['data']
                decoded_bytes = base64.urlsafe_b64decode(data.encode('UTF-8'))
                email_body = decoded_bytes.decode('UTF-8')

            email_summaries.append(f"From: {sender}\nSubject: {subject}\nContent: {email_body}")

        return email_summaries



    except HttpError as error:
        print(f'An error occurred: {error}')
        return [f'An error occurred: {error}']

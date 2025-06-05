from langchain.tools import tool
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import base64
from app.utils.google_cloud.cloud_config import get_credentials


@tool
def send_email_tool(recipient: str = "", subject: str = "", message_text: str = "") -> str:
    """
    Creates a draft email in Gmail.
    Always ask for required fields before calling this tool.

    Args:
        recipient (str): Email address of the recipient.
        subject (str): Subject of the email.
        message_text (str): Body of the email.

    Returns:
        str: Success or error message.
    """
    print("Used send email tool")

    # Validate input
    if not recipient or "@" not in recipient:
        return "❌ Error: A valid recipient email address is required."
    if not subject:
        return "❌ Error: Email subject is required."
    if not message_text:
        return "❌ Error: Email message text is required."

    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Create email content
        message = MIMEText(message_text)
        message['to'] = recipient
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create draft
        draft = {'message': {'raw': raw_message}}
        response = service.users().drafts().create(userId='me', body=draft).execute()

        print(f"✅ Draft created successfully with ID: {response['id']}")
        return f"✅ Draft created successfully with ID: {response['id']}"
    except FileNotFoundError:
        print("❌ Error: 'client_secret.json' or 'token.json' not found. Authenticate with Gmail API first.")
        return "❌ Error: 'client_secret.json' or 'token.json' not found. Authenticate with Gmail API first."
    except Exception as e:
        print( f"❌ Unexpected error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"


# @tool
# def send_email_tool(to: str, subject: str, body: str) -> str:
#     """
#     Send an email via Gmail API.
#     Ask the user for information about the email before sending the email.
#     Never ever create an email without collecting necessary data from the user.
#
#     Parameters:
#     - to (str): Recipient email address. Must be a valid email format.
#     - subject (str): Subject line of the email.
#     - body (str): Body content of the email.
#
#     Returns:
#     - str: Success message or an error message if parameters are invalid.
#     """
#     # Basic parameter validation
#     if not to:
#         return "Error: Recipient email address ('to') is required."
#     if "@" not in to or "." not in to:
#         return "Error: Invalid email address format for 'to'."
#     if not subject:
#         return "Error: Email subject is required."
#     if not body:
#         return "Error: Email body cannot be empty."
#
#     # Call the actual send_email function (assumed imported)
#     try:
#         # response = send_email(to, subject, body)
#         return f"Email sent successfully to {to}."
#     except Exception as e:
#         return f"Failed to send email: {str(e)}"



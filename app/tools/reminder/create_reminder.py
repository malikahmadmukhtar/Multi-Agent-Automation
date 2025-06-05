from _pydatetime import timedelta
from app.utils.google_cloud.cloud_config import get_credentials
from langchain.tools import tool
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import streamlit as st

@tool
def create_reminder_tool(summary: str = "", start_time: str = "", duration_minutes: int = 60) -> str:
    """
    Creates a reminder as a calendar event using Google Calendar API.
    Don't ask the user for formatting the date, format it yourself.

    Args:
        summary (str): Title of the reminder.
        start_time (str): ISO format time string (e.g. "2025-06-02T14:00:00").
        duration_minutes (int): Duration in minutes.

    Returns:
        str: Success or error message.
    """
    st.sidebar.info("Used create reminder tool")

    print("📌 Starting create_reminder_tool...")
    print(f"📋 Received summary: {summary}")
    print(f"🕒 Received start_time: {start_time}")
    print(f"⏳ Received duration_minutes: {duration_minutes}")

    if not summary:
        print("❌ Missing summary")
        return "❌ Error: Reminder summary is required."
    if not start_time:
        print("❌ Missing start_time")
        return "❌ Error: Start time is required in ISO format (e.g., 2025-06-02T14:00:00)."

    try:
        # Ensure start_time is a datetime object
        if isinstance(start_time, str):
            start = datetime.fromisoformat(start_time)
            print(f"✅ Parsed start_time to datetime: {start}")
        else:
            print("❌ start_time is not a string")
            return "❌ Error: start_time must be a string in ISO format."

        end = start + timedelta(minutes=duration_minutes)
        print(f"📆 Calculated end_time: {end}")

        print("🔐 Fetching credentials...")
        creds = get_credentials()
        print("✅ Credentials loaded")

        print("🔧 Building Google Calendar service...")
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Calendar service built")

        event = {
            'summary': summary,
            'start': {'dateTime': start.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'UTC'}
        }

        print("📤 Inserting event...")
        result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Event inserted: {result}")

        return f"✅ Reminder created successfully: {result.get('htmlLink')}"

    except ValueError:
        print("❌ ValueError: Invalid datetime format")
        return "❌ Error: Invalid datetime format. Use ISO format like 2025-06-02T14:00:00"
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"

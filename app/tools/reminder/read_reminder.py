from langchain.tools import tool
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import streamlit as st
from app.utils.google_cloud.cloud_config import get_credentials


@tool
def read_reminders_tool(date: str = "") -> str:
    """
    Reads reminders from Google Calendar on a specific date.
    Take date and format it as required by the tool, don't ask user to format it.

    Args:
        date (str): Date in YYYY-MM-DD format (don't ask user to format it).

    Returns:
        str: List of reminders or an error message.
    """
    st.sidebar.info("Used read reminders tool")
    print(f"📅 Reading reminders for date: {date}")

    try:
        # Validate date format
        try:
            query_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "❌ Error: Invalid date format. Use YYYY-MM-DD."

        # Define time range in UTC
        tz = pytz.UTC
        start_of_day = tz.localize(datetime(query_date.year, query_date.month, query_date.day))
        end_of_day = start_of_day + timedelta(days=1)

        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        print(f"📌 Found {len(events)} reminders")

        if not events:
            return f"No reminders found on {date}."

        reminders = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            reminders.append(f"🕒 {start}: {summary}")

        return "\n".join(reminders)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"
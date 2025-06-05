import json
import os
from datetime import datetime

CHAT_HISTORY_DIR = "app/history/history_data"  # Directory to store chat history files


def ensure_chat_history_dir_exists():
    """Ensures the chat history directory exists."""
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


def _get_file_path_for_session_id(session_id: str) -> str:
    """Helper to find the file path for a given session ID."""
    ensure_chat_history_dir_exists()
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith(f"-{session_id}.json"):
            return os.path.join(CHAT_HISTORY_DIR, filename)
    return None  # Not found


def save_chat_session(chat_history: list, agent_log: list, session_id: str) -> str:
    """
    Saves or updates the current chat history and agent log to a JSON file.
    It uses the provided session_id to find and update an existing file,
    or creates a new one if the ID doesn't exist.
    Returns the ID of the saved session.
    """
    ensure_chat_history_dir_exists()

    # Determine the file path for this session ID
    file_path = _get_file_path_for_session_id(session_id)

    # If file_path is None, it means this is a new session or the file was deleted.
    # Create a new filename using the session_id.
    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # For new files, use a generic name prefix, actual display name is in JSON
        file_name = f"{timestamp}-chat-{session_id}.json"
        file_path = os.path.join(CHAT_HISTORY_DIR, file_name)

    # Generate display name from first user message, or use a default
    display_name = "New Chat"
    for msg in chat_history:
        if msg["role"] == "user" and len(msg["content"]) > 0:
            # display_name = msg["content"][:20].replace(" ", "_").replace("/", "_").replace("\\", "_")
            display_name = msg["content"][:20].replace("/", "_").replace("\\", "_")

            if len(msg["content"]) > 20:
                display_name += "..."
            break

    session_data = {
        "id": session_id,
        "timestamp": datetime.now().strftime("%Y%m%d-%H%M%S"),  # Update timestamp on save
        "chat_history": chat_history,
        "agent_log": agent_log,
        "display_name": display_name  # Always update display name
    }

    with open(file_path, "w") as f:
        json.dump(session_data, f, indent=2)
    return session_id


def load_chat_session(file_path: str) -> dict:
    """
    Loads a specific chat session from a JSON file.
    Returns a dictionary containing chat_history and agent_log.
    """
    with open(file_path, "r") as f:
        session_data = json.load(f)
    return session_data


def get_saved_sessions() -> list:
    """
    Retrieves a list of all saved chat session files.
    Each item in the list is a tuple: (full_file_path, display_name, session_id).
    """
    ensure_chat_history_dir_exists()
    sessions = []
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(CHAT_HISTORY_DIR, filename)
            try:
                with open(file_path, "r") as f:
                    session_data = json.load(f)
                    # Use stored display name and ID
                    display_name = session_data.get("display_name", filename.replace(".json", ""))
                    session_id = session_data.get("id", None)
                    timestamp = session_data.get("timestamp", "")  # Get timestamp for sorting

                    if session_id:  # Only add if a valid ID is present
                        sessions.append((file_path, display_name, session_id, timestamp))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filename}")
            except KeyError:
                print(f"Warning: Missing 'id' or 'display_name' in {filename}")

    # Sort by timestamp (newest first)
    sessions.sort(key=lambda x: x[3], reverse=True)  # Sort by the timestamp we loaded
    return [(s[0], s[1], s[2]) for s in sessions]  # Return without timestamp


def delete_chat_session(file_path: str) -> None:
    """Deletes a specific chat session file."""
    if os.path.exists(file_path):
        os.remove(file_path)
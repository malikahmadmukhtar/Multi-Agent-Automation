import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
import uuid
from streamlit.components.v1 import html
from app.agents.general_chat_agent import Charlie
from app.agents.mail_agent import Alpha
from app.agents.reminder_agent import Bravo
from app.utils.agent_config import create_and_compile_swarm
from app.utils.llm import get_llm
from app.history.chat_history import save_chat_session, load_chat_session, get_saved_sessions, delete_chat_session, \
    ensure_chat_history_dir_exists
from app.utils.voice.stt import stt_data
from app.utils.voice.tts import speak, generate_and_play_groq_audio
from config.settings import agent_image, user_image, active_model, MAX_PREVIOUS_MESSAGES_FOR_CONTEXT

# Load environment variables
load_dotenv()

# Ensure the chat history directory exists on startup
ensure_chat_history_dir_exists()

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "active_agent_log" not in st.session_state:
    st.session_state["active_agent_log"] = []
if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = str(uuid.uuid4())
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = st.session_state["current_session_id"]
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

st.set_page_config(page_title="Automation Assistant", layout="wide")


# --- Initialize LLM and Agents (cached for performance) ---
@st.cache_resource
def initialize_all_components():
    """Initializes LLM, agents, and the swarm workflow."""
    llm = get_llm()
    if not llm:
        return None, None, None  # Ensure consistent return structure

    agents_list = [Alpha, Bravo, Charlie]  # Pass all agents to the list

    # The default active agent name. Ensure it matches one of your agent's .name attribute.
    # Assuming 'Alpha' is the name property of the Alpha agent instance
    app, checkpointer = create_and_compile_swarm(agents_list, default_active_agent_name="Charlie")
    return agents_list, app, checkpointer


# Get initialized components
agents_list, app, checkpointer = initialize_all_components()

# Only proceed if all components were successfully initialized
if agents_list and app and checkpointer:
    # --- Streamlit UI ---
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(image=agent_image, output_format="PNG", width=120)
    with col2:
        st.title("Multi Agent Assistant")

    st.header("Type below to get Started")

    TOKEN_FILENAME = "token.json"

    # Check if the token file already exists in the project root
    token_exists = os.path.exists(os.path.join(os.getcwd(), TOKEN_FILENAME))

    with st.sidebar:
        if not token_exists:
            st.header("Upload your token")
            uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        else:
            st.success(f"Token file '{TOKEN_FILENAME}' already exists!")
            uploaded_file = None  # Ensure uploaded_file is None if token exists

    # Main section shows result
    if uploaded_file is not None:
        st.success(f"Uploaded file: {uploaded_file.name}")

        # Save to project root
        save_path = os.path.join(os.getcwd(), uploaded_file.name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

    elif token_exists:
        st.success(f"Token file '{TOKEN_FILENAME}' is already present.")

    with st.sidebar:
        st.sidebar.subheader("Try asking me:")
        st.markdown("""
                * 🌍 How is Redmi note 14.
                * ☀️ Weather tomorrow in lahore.
                * 📧 Any unread emails? 
                * ⏰ Remind me at 7 PM tomorrow. 
                * 🎨 Generate an image of a cat. 
                ---
                """)

    # Sidebar - Voice Mode Toggle (TTS only)
    st.session_state.voice_mode = st.sidebar.toggle("🔊 Voice Responses", value=st.session_state.voice_mode,
                                                    help="Enable text-to-speech for assistant responses")
    # --- Sidebar for Chat History Management ---
    st.sidebar.header("Chat Sessions")

    # Button to start a new chat
    if st.sidebar.button("➕ Start New Chat", key="new_chat_button",use_container_width=True):
        # Save current session before starting a new one, if it has content
        if st.session_state["chat_history"]:
            save_chat_session(
                st.session_state["chat_history"],
                st.session_state["active_agent_log"],
                st.session_state["current_session_id"]
            )
        st.session_state["chat_history"] = []
        st.session_state["active_agent_log"] = []
        st.session_state["current_session_id"] = str(uuid.uuid4())  # New session ID
        st.session_state["thread_id"] = st.session_state["current_session_id"]  # New LangGraph thread ID
        st.rerun()  # Rerun to clear chat and load new session

    saved_sessions = get_saved_sessions()

    if saved_sessions:
        st.sidebar.subheader("Saved Chats")
        # Iterate with an index to ensure unique keys for buttons
        for i, (file_path, display_name, session_id) in enumerate(saved_sessions):
            col1, col2 = st.sidebar.columns([1, 0.2])

            # Load Session Button: Added __{i} to the key
            if col1.button(display_name, key=f"load_{session_id}__{i}",use_container_width=True):
                # Save current session if it has content before loading new one
                if st.session_state["chat_history"] and st.session_state["current_session_id"] != session_id:
                    save_chat_session(
                        st.session_state["chat_history"],
                        st.session_state["active_agent_log"],
                        st.session_state["current_session_id"]
                    )

                loaded_data = load_chat_session(file_path)
                st.session_state["chat_history"] = loaded_data["chat_history"]
                st.session_state["active_agent_log"] = loaded_data["agent_log"]
                st.session_state["current_session_id"] = loaded_data["id"]  # Set current session ID
                st.session_state["thread_id"] = loaded_data["id"]  # Set LangGraph thread ID
                st.rerun()  # Rerun to display loaded chat

            # Delete Session Button: Added __{i} to the key
            if col2.button("🗑️", key=f"delete_{session_id}__{i}"):
                st.session_state["confirm_delete"] = file_path  # Store path for confirmation
                st.session_state["confirm_delete_id"] = session_id  # Store ID for confirmation message
                st.rerun()  # Rerun to show confirmation prompt

    # Confirmation for deletion
    if "confirm_delete" in st.session_state and st.session_state["confirm_delete"]:
        file_to_delete = st.session_state["confirm_delete"]
        session_id_to_delete = st.session_state["confirm_delete_id"]
        st.sidebar.warning(f"Are you sure you want to delete chat session {session_id_to_delete[:8]}...?")
        col_confirm_yes, col_confirm_no = st.sidebar.columns(2)

        # Ensure confirmation buttons also have unique keys
        if col_confirm_yes.button("Yes, Delete", key=f"confirm_yes_{session_id_to_delete}"):
            delete_chat_session(file_to_delete)
            st.sidebar.success("Session deleted!")
            # If current session was deleted, start a new one
            if st.session_state["current_session_id"] == session_id_to_delete:
                st.session_state["chat_history"] = []
                st.session_state["active_agent_log"] = []
                st.session_state["current_session_id"] = str(uuid.uuid4())
                st.session_state["thread_id"] = st.session_state["current_session_id"]
            del st.session_state["confirm_delete"]
            del st.session_state["confirm_delete_id"]
            st.rerun()
        if col_confirm_no.button("No, Cancel", key=f"confirm_no_{session_id_to_delete}"):
            del st.session_state["confirm_delete"]
            del st.session_state["confirm_delete_id"]
            st.rerun()

    st.sidebar.header("Agent Activity Log")
    for log in st.session_state["active_agent_log"]:
        st.sidebar.info(log)

    for i, message in enumerate(st.session_state["chat_history"]):
        if message["role"] == "user":
            with st.chat_message("user", avatar=user_image):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=agent_image):
                col1, col2 = st.columns([10, 1])  # 10:1 ratio for message and button
                with col1:
                    st.markdown(message["content"])
                    # if st.button("🔈", key=f"speak_{i}", help="Speak this message"):
                    #     speak(message["content"])
                        # generate_and_play_groq_audio(text=message["content"])
                with col2:
                    if st.button("🔈", key=f"speak_{i}", help="Speak this message"):
                        speak(message["content"])
                        # generate_and_play_groq_audio(text=message["content"])

    ## rendering STT
    html(stt_data)

    # Chat input at the bottom of the main page
    if prompt := st.chat_input("Send a message...", key="chat_input_main"):  # Added unique key
        # 1. Add user message to Streamlit's chat history for display
        st.session_state["chat_history"].append({"role": "user", "content": prompt, "avatar": user_image})

        # Display the user's message immediately
        with st.chat_message("user", avatar=user_image):
            st.markdown(prompt)

        # 2. Prepare messages for LangGraph invocation with limit
        langgraph_messages_for_invoke = []
        messages_to_send = st.session_state["chat_history"][-MAX_PREVIOUS_MESSAGES_FOR_CONTEXT:]

        for msg in messages_to_send:
            if msg["role"] == "user":
                langgraph_messages_for_invoke.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langgraph_messages_for_invoke.append(AIMessage(content=msg["content"]))

        # 3. Process the message through the LangGraph app
        try:
            # with st.spinner(f"{active_model} is working on it"):
            with st.spinner(f"Thinking 🤔..."):

                response = app.invoke(
                    {"messages": langgraph_messages_for_invoke},
                    config={"configurable": {"thread_id": st.session_state["thread_id"]}},
                )

                if response and response.get("messages"):
                    ai_message_obj = response["messages"][-1]

                    # 4. Convert AI response back to Streamlit's chat history format
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": ai_message_obj.content, "avatar": agent_image})

                    ## TTS
                    if st.session_state.voice_mode:
                        speak(ai_message_obj.content)


                    # Infer and log the active agent
                    active_agent_name = "Unknown Agent"
                    if hasattr(ai_message_obj, 'name') and ai_message_obj.name:
                        active_agent_name = ai_message_obj.name
                    elif response.get("intermediate_steps"):
                        last_step = response["intermediate_steps"][-1]
                        if hasattr(last_step, 'action') and hasattr(last_step.action, 'tool'):
                            active_agent_name = f"Tool: {last_step.action.tool}"
                        elif hasattr(last_step, 'agent'):
                            active_agent_name = last_step.agent

                    st.session_state["active_agent_log"].append(f"**{active_agent_name}:** Responded")

                    # Automatically save the current session after every interaction
                    save_chat_session(
                        st.session_state["chat_history"],
                        st.session_state["active_agent_log"],
                        st.session_state["current_session_id"]
                    )

                    st.rerun()

                else:
                    st.session_state["active_agent_log"].append("**Error:** No response received from agents.")
                    st.error("No response received from the agents.")

        except Exception as e:
            st.session_state["active_agent_log"].append(f"**Error during invocation:** {e}")
            st.error(f"An error occurred: {e}")

else:
    st.error("Application components are not fully initialized. Please check initial load messages.")
    st.stop()
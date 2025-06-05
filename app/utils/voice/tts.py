import json
import re
import streamlit as st
from groq import Groq

from config.settings import groq_api_key


def speak(text: str):
    # Clean and prepare text
    safe_text = re.sub(r"[^\x20-\x7E]+", " ", text).strip()  # remove non-printable chars

    safe_text_without_numbers = re.sub(r"\b\d{6,}\b", "", safe_text)

    url_pattern = r"(?:https?://|www\.)\S+|(?:\S+\.[a-z]{2,})/\S*"  # This is a more comprehensive URL pattern

    safe_text_without_urls = re.sub(url_pattern, "", safe_text_without_numbers)

    js_safe_text = json.dumps(safe_text_without_urls)  # safely escape quotes, newlines, etc.

    # Inject TTS JS and call it
    st.components.v1.html(f"""
    <script>
    const speak = (text) => {{
        if (window.speechSynthesis.speaking) {{
            window.speechSynthesis.cancel();
        }}
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";
        window.speechSynthesis.speak(utterance);
    }};
    speak({js_safe_text});
    </script>
    """, height=0)


# def speak(text: str):
#     """
#     Generates and plays audio using the client-side Web Speech API,
#     providing basic playback controls within Streamlit.
#
#     Args:
#         text (str): The text to be spoken.
#     """
#     # Clean and prepare text
#     safe_text = re.sub(r"[^\x20-\x7E]+", " ", text).strip()
#     safe_text_without_numbers = re.sub(r"\b\d{6,}\b", "", safe_text)
#     url_pattern = r"(?:https?://|www\.)\S+|(?:\S+\.[a-z]{2,})/\S*"
#     safe_text_without_urls = re.sub(url_pattern, "", safe_text_without_numbers)
#
#     js_safe_text = json.dumps(safe_text_without_urls) # Safely escape for JavaScript
#
#     # Use a unique ID for each set of controls to avoid conflicts
#     # when the function is called multiple times on the same page.
#     control_id = hash(text) % 1_000_000 # Simple hash for a unique ID
#
#     # Inject TTS JS and call it with controls
#     st.components.v1.html(f"""
#     <style>
#         .audio-controls-container {{
#             display: flex;
#             align-items: center;
#             gap: 8px; /* Space between buttons */
#             padding: 5px 0;
#             flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
#         }}
#         .audio-controls-container button {{
#             background-color: #f0f2f6;
#             border: 1px solid #ccc;
#             border-radius: 4px;
#             padding: 8px 12px;
#             font-size: 14px;
#             cursor: pointer;
#             transition: background-color 0.2s;
#             display: flex;
#             align-items: center;
#             gap: 4px;
#         }}
#         .audio-controls-container button:hover:not(:disabled) {{
#             background-color: #e0e2e6;
#         }}
#         .audio-controls-container button:active:not(:disabled) {{
#             background-color: #d0d2d6;
#         }}
#         .audio-controls-container button:disabled {{
#             opacity: 0.5;
#             cursor: not-allowed;
#         }}
#     </style>
#
#     <div id="audioControls_{control_id}" class="audio-controls-container">
#         <button id="playBtn_{control_id}">▶️ Play</button>
#         <button id="pauseBtn_{control_id}" disabled>⏸️ Pause</button>
#         <button id="resumeBtn_{control_id}" disabled>▶️ Resume</button>
#         <button id="stopBtn_{control_id}" disabled>⏹️ Stop</button>
#     </div>
#
#     <script>
#     const synth_{control_id} = window.speechSynthesis;
#     let utterance_{control_id} = null;
#
#     const updateButtonStates_{control_id} = () => {{
#         const playBtn = document.getElementById('playBtn_{control_id}');
#         const pauseBtn = document.getElementById('pauseBtn_{control_id}');
#         const resumeBtn = document.getElementById('resumeBtn_{control_id}');
#         const stopBtn = document.getElementById('stopBtn_{control_id}');
#
#         if (!playBtn || !pauseBtn || !resumeBtn || !stopBtn) return; // Ensure elements exist
#
#         if (synth_{control_id}.speaking) {{
#             playBtn.disabled = true;
#             stopBtn.disabled = false;
#             if (synth_{control_id}.paused) {{
#                 pauseBtn.disabled = true;
#                 resumeBtn.disabled = false;
#             }} else {{
#                 pauseBtn.disabled = false;
#                 resumeBtn.disabled = true;
#             }}
#         }} else {{
#             playBtn.disabled = false;
#             pauseBtn.disabled = true;
#             resumeBtn.disabled = true;
#             stopBtn.disabled = true;
#         }}
#     }};
#
#     // Function to speak the text
#     const speakText_{control_id} = (text) => {{
#         if (synth_{control_id}.speaking) {{
#             synth_{control_id}.cancel();
#         }}
#         utterance_{control_id} = new SpeechSynthesisUtterance(text);
#         utterance_{control_id}.lang = "en-US"; // Set language
#
#         utterance_{control_id}.onend = () => {{
#             console.log('Speech finished for ID: {control_id}');
#             updateButtonStates_{control_id}();
#         }};
#         utterance_{control_id}.onstart = () => {{
#             console.log('Speech started for ID: {control_id}');
#             updateButtonStates_{control_id}();
#         }};
#         utterance_{control_id}.onpause = () => {{
#             console.log('Speech paused for ID: {control_id}');
#             updateButtonStates_{control_id}();
#         }};
#         utterance_{control_id}.onresume = () => {{
#             console.log('Speech resumed for ID: {control_id}');
#             updateButtonStates_{control_id}();
#         }};
#         utterance_{control_id}.onerror = (event) => {{
#             console.error('Speech synthesis error for ID {control_id}:', event.error);
#             updateButtonStates_{control_id}();
#         }};
#
#         synth_{control_id}.speak(utterance_{control_id});
#         updateButtonStates_{control_id}(); // Update immediately after calling speak
#     }};
#
#     // Attach event listeners to buttons
#     document.getElementById('playBtn_{control_id}').onclick = () => speakText_{control_id}({js_safe_text});
#     document.getElementById('pauseBtn_{control_id}').onclick = () => {{
#         if (synth_{control_id}.speaking && !synth_{control_id}.paused) {{
#             synth_{control_id}.pause();
#         }}
#     }};
#     document.getElementById('resumeBtn_{control_id}').onclick = () => {{
#         if (synth_{control_id}.paused) {{
#             synth_{control_id}.resume();
#         }}
#     }};
#     document.getElementById('stopBtn_{control_id}').onclick = () => {{
#         if (synth_{control_id}.speaking || synth_{control_id}.paused) {{
#             synth_{control_id}.cancel();
#         }}
#     }};
#
#     // Initial state update when the component loads
#     updateButtonStates_{control_id}();
#
#     </script>
#     """, height=50) # Increased height to accommodate buttons comfortably



## for groq
def generate_and_play_groq_audio(text: str, voice: str = "Angelo-PlayAI"):
    """
    Generates speech from text using Groq's Text-to-Speech API
    and plays it directly in Streamlit using st.audio.

    Args:
        text (str): The text to convert to speech.
        voice (str): The voice to use for audio generation.
                     Refer to Groq API documentation for available voices.
                     Default is "allura-playai".
    """
    # Ensure Groq API key is set


    client = Groq(api_key=groq_api_key)

    try:
        with st.spinner(f"Generating speech with '{voice}' voice..."):
            chat_completion = client.audio.speech.create(
                model="playai-tts",  # Use the Groq TTS model
                voice=voice,
                input=text,
                response_format="wav" # WAV format is generally well-supported
            )
            audio_bytes = chat_completion.read()

        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav", autoplay=True)
            st.success("Audio generated and playing!")
        else:
            st.warning("No audio data received from Groq. Check your text and API key.")

    except Exception as e:
        st.error(f"Error generating or playing speech: {e}")


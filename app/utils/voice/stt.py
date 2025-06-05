stt_data=("""
<style>
  #mic-button-container {
    position: fixed;
    bottom: 0px;
    right: 0px;
    top: 80px;
    z-index: 1000000;
  }

  #mic-btn {
    background-color: #dc3545;
    color: white;
    font-size: 28px;
    padding: 12px 16px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s ease;
  }

  #mic-btn.listening {
    background-color: #28a745 !important;
  }
</style>

<div id="mic-button-container">
  <button id="mic-btn" onclick="toggleRecognition()">🎙️</button>
</div>

<script>
  let recognizing = false;
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;

  function toggleRecognition() {
    const button = document.getElementById("mic-btn");
    if (!recognizing) {
      recognition.start();
      recognizing = true;
      button.classList.add("listening");
    } else {
      recognition.stop();
      recognizing = false;
      button.classList.remove("listening");
    }
  }

  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;

    let chatInput = Array.from(window.parent.document.querySelectorAll("textarea"))
                         .find(el => el.getAttribute("data-testid")?.includes("stChatInput"));

    if (chatInput) {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      setter.call(chatInput, transcript);
      chatInput.dispatchEvent(new Event("input", { bubbles: true }));

      // Trigger Enter key press to auto-submit
      const keyboardEvent = new KeyboardEvent("keydown", {
        bubbles: true,
        cancelable: true,
        key: "Enter",
        code: "Enter"
      });
      chatInput.dispatchEvent(keyboardEvent);
    }
  };

  recognition.onend = function() {
    const button = document.getElementById("mic-btn");
    recognizing = false;
    button.classList.remove("listening");
  };
</script>
""")


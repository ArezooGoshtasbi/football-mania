document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
  
    function loadMessages() {
      fetch("/comments/")
        .then(response => response.json())
        .then(data => {
          chatMessages.innerHTML = "";
          data.forEach(msg => {
            const div = document.createElement("div");
            div.className = "chat-message";
            div.innerHTML = `<strong>${msg.user}</strong>: ${msg.message} <br><small>${msg.timestamp}</small>`;
            chatMessages.appendChild(div);
          });
        });
    }
  
    loadMessages();
  
    if (chatForm) {
      chatForm.addEventListener("submit", event => {
        event.preventDefault();
        const message = chatInput.value.trim();
        if (message === "") return;
  
        fetch("/comments/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ message })
        })
        .then(response => {
          if (response.ok) {
            chatInput.value = "";
            loadMessages();
          }
        });
      });
    }
  });
  
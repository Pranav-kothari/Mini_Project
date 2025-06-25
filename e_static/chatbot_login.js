function toggleChatbot() {
  var chatbot = document.getElementById("chatbot-window");
  if (chatbot.style.display === "block") {
    chatbot.style.display = "none";
  } else {
    chatbot.style.display = "block";
    initializeLoginChat();
  }
}

function initializeLoginChat() {
  var content = document.getElementById("chatbot-content");
  content.innerHTML = "";

  appendBotMessage("Hi there! 👋 Are you a new user or trying to log in?");
  
  let signupBtn = document.createElement("button");
  signupBtn.textContent = "I'm New";
  signupBtn.classList.add("chatbot-option");
  signupBtn.onclick = () => {
    appendUserMessage("I'm New");
    appendBotMessage("Awesome! Let's get you signed up.");
    setTimeout(() => {
      window.location.href = "/signup/";
    }, 1000);
  };
  content.appendChild(signupBtn);

  let loginBtn = document.createElement("button");
  loginBtn.textContent = "I have an account";
  loginBtn.classList.add("chatbot-option");
  loginBtn.onclick = () => {
    appendUserMessage("I have an account");
    appendBotMessage("Great — please enter your username and password above to log in.");
  };
  content.appendChild(loginBtn);
}

function appendBotMessage(message) {
  var content = document.getElementById("chatbot-content");
  var msg = document.createElement("p");
  msg.classList.add("bot-message");
  msg.textContent = "🤖: " + message;
  content.appendChild(msg);
  scrollChatToBottom();
}

function appendUserMessage(message) {
  var content = document.getElementById("chatbot-content");
  var msg = document.createElement("p");
  msg.classList.add("user-message");
  msg.textContent = "🧑: " + message;
  content.appendChild(msg);
  scrollChatToBottom();
}

function scrollChatToBottom() {
  var content = document.getElementById("chatbot-content");
  content.scrollTop = content.scrollHeight;
}

window.addEventListener("load", initializeLoginChat);

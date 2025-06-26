function toggleChatbot() {
  var chatbot = document.getElementById("chatbot-window");
  var button = document.getElementById("chatbot-button");

  if (chatbot.style.display === "flex" || chatbot.style.display === "block") {
    chatbot.style.display = "none";
    button.style.opacity = "1";
  } else {
    chatbot.style.display = "flex";
    button.style.opacity = "0";
    initializeLoginChat();
  }
}

function scrollChatToBottom() {
  var content = document.getElementById("chatbot-content");
  content.scrollTop = content.scrollHeight;
}

function initializeLoginChat() {
  var content = document.getElementById("chatbot-content");
  content.innerHTML = "";

  appendBotMessage("Hi there! 👋 Are you a new user or trying to log in?");

  // Sign up button
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

  // Login button
  let loginBtn = document.createElement("button");
  loginBtn.textContent = "I have an account";
  loginBtn.classList.add("chatbot-option");
  loginBtn.onclick = () => {
    appendUserMessage("I have an account");
    appendBotMessage("Great — please enter your username and password above to log in.");
  };
  content.appendChild(loginBtn);

  // Explore products button
  let exploreBtn = document.createElement("button");
  exploreBtn.textContent = "Explore products first";
  exploreBtn.classList.add("chatbot-option");
  exploreBtn.onclick = () => {
    appendUserMessage("I want to explore products first");
    startProductChoiceFlow();
  };
  content.appendChild(exploreBtn);

  scrollChatToBottom();
}

function startProductChoiceFlow() {
  var content = document.getElementById("chatbot-content");
  content.innerHTML = "";
  appendBotMessage("Before we proceed, what kind of products are you looking for today?");
  fetchCategoriesForLogin();
}

function fetchCategoriesForLogin() {
  fetch("/api/categories/")
    .then(response => response.json())
    .then(data => {
      showOptions(data.categories.slice(0, 3), category => {
        appendUserMessage(category.name);
        fetchSubcategoriesForLogin(category.id);
      });
    });
}

function fetchSubcategoriesForLogin(categoryId) {
  appendBotMessage("Nice! Which sub-category interests you?");
  fetch(`/api/subcategories/${categoryId}/`)
    .then(response => response.json())
    .then(data => {
      showOptions(data.subcategories.slice(0, 3), subcategory => {
        appendUserMessage(subcategory.name);
        redirectToAccountPage(subcategory.id);
      });
    });
}

function redirectToAccountPage(subcategoryId) {
  appendBotMessage("Awesome — let's get your account set up to explore these products!");
  setTimeout(() => {
    window.location.href = `/signup/?subcategory=${subcategoryId}`;
  }, 1200);
}

function showOptions(options, callback) {
  var content = document.getElementById("chatbot-content");
  options.forEach(option => {
    var btn = document.createElement("button");
    btn.textContent = option.name;
    btn.classList.add("chatbot-option");
    btn.onclick = () => callback(option);
    content.appendChild(btn);
  });
  scrollChatToBottom();
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

// Initialize when page loads
window.addEventListener("load", initializeLoginChat);

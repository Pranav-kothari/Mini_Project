let isChatInitialized=false;
function initializeChat() {
  if (isChatInitialized) return; // Prevent re-clearing
  isChatInitialized = true;

  fetchUserName();
}

function appendBotMessage(message) {
  var content = document.getElementById("chatbot-content");
  var msg = document.createElement("p");
  msg.classList.add("bot-message");
  msg.textContent = "🤖: " + message;
  content.appendChild(msg);
  logChatMessage(message, 'bot');
  scrollChatToBottom();
}

function appendUserMessage(message) {
  var content = document.getElementById("chatbot-content");
  var msg = document.createElement("p");
  msg.classList.add("user-message");
  msg.textContent = "🧑: " + message;
  content.appendChild(msg);
  logChatMessage(message, 'user');
  scrollChatToBottom();
}


function fetchCategories() {
  fetch("/api/categories/")
    .then(response => response.json())
    .then(data => {
      let visibleCategories = data.categories.slice(0, 3);
      showOptions(visibleCategories, category => {
        appendUserMessage(category.name);
        fetchSubcategories(category.id);
      });

      if (data.categories.length > 3) {
    appendViewMoreButton({ type: "more_categories" });
}

    });
}

function fetchSubcategories(categoryId) {
  appendBotMessage("Great choice! Pick a sub-category:");
  fetch(`/api/subcategories/${categoryId}/`)
    .then(response => response.json())
    .then(data => {
      let visibleSubcategories = data.subcategories.slice(0, 3);
      showOptions(visibleSubcategories, subcategory => {
        appendUserMessage(subcategory.name);
        askBudget(subcategory.id);
      });

      if (data.subcategories.length > 3) {
            appendViewMoreButton({ type: "more_subcategories", categoryId: categoryId });
        }

    });
}

function askBudget(subcategoryId) {
  fetch(`/api/price_range/${subcategoryId}/`)
    .then(response => response.json())
    .then(data => {
      let basePrice = data.min_price;

      if (basePrice === null) {
        appendBotMessage("Sorry, no products available in this sub-category.");
        return;
      }

      appendBotMessage(`What's your budget? (Starting from ₹${basePrice})`);

      let budgets = [
        { name: `Under ₹${basePrice}`, min: 0, max: basePrice },
        { name: `₹${basePrice} – ₹${basePrice * 2}`, min: basePrice, max: basePrice * 2 },
        { name: `Above ₹${basePrice * 2}`, min: basePrice * 2, max: 999999 }
      ];

      budgets.forEach(budget => {
        let btn = document.createElement("button");
        btn.textContent = budget.name;
        btn.classList.add("chatbot-option");
        btn.onclick = () => {
          appendUserMessage(budget.name);
          appendBotMessage(`Sure — fetching products in ${budget.name} range for you!`);

          // Add loading animation
          const content = document.getElementById("chatbot-content");
          let loadingMsg = document.createElement("p");
          loadingMsg.textContent = "🤖: Loading";
          content.appendChild(loadingMsg);

          let dots = 0;
          let interval = setInterval(() => {
            dots = (dots + 1) % 4;
            loadingMsg.textContent = "🤖: Loading" + ".".repeat(dots);
          }, 400);

          setTimeout(() => {
            clearInterval(interval);
            window.location.href = `/home/?subcategory=${subcategoryId}&min_price=${budget.min}&max_price=${budget.max}`;
          }, 1500);
        };
        document.getElementById("chatbot-content").appendChild(btn);
      });

    });
}




function appendViewMoreButton(action) {
  let btn = document.createElement("button");
  btn.textContent = "View More";
  btn.classList.add("chatbot-option");

  if (action.type === "more_categories") {
    btn.onclick = () => {
      window.location.href = `/home/?view=all_categories`;
    };
  } else if (action.type === "more_subcategories") {
    btn.onclick = () => {
      window.location.href = `/home/?category=${action.categoryId}`;
    };
  } else {
    btn.onclick = () => window.location.href = action.url;
  }

  document.getElementById("chatbot-content").appendChild(btn);
}



function fetchProducts(subcategoryId, maxPrice) {
  appendBotMessage("Awesome! Here are products for you:");

  fetch(`/api/products/${subcategoryId}/?max_price=${maxPrice}`)
    .then(response => response.json())
    .then(data => {
      if (data.products.length === 0) {
        appendBotMessage("Sorry, no products found in this budget.");
        return;
      }

      data.products.forEach(product => {
        appendBotMessage(`🛒 ${product.name} - ₹${product.price}`);
      });
    });
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
}

function fetchUserName() {
  fetch("/api/userinfo/")
    .then(response => response.json())
    .then(data => {
      appendBotMessage(`Hi ${data.name}! 👋 What are you looking for today?`);
      fetchCategories();
    })
    .catch(() => {
      // fallback if API fails
      appendBotMessage("Hi there! 👋 What are you looking for today?");
      fetchCategories();
    });
}



function toggleChatbot() {
    const chatbot = document.getElementById('chatbot-window');
    if (chatbot.classList.contains('is-open')) {
        chatbot.classList.remove('is-open');
        chatbot.classList.add('is-closed');
    } else {
        chatbot.classList.remove('is-closed');
        chatbot.classList.add('is-open');
        initializeChat();
    }
}



function scrollChatToBottom() {
  var content = document.getElementById("chatbot-content");
  content.scrollTop = content.scrollHeight;
}



function logChatMessage(message, by) {
  fetch("/api/log_message/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie('csrftoken')
    },
    body: JSON.stringify({
      session_id: getSessionId(),
      page: window.location.pathname,
      message: message,
      message_by: by
    })
  });
}



function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getSessionId() {
  if (!localStorage.getItem("chat_session_id")) {
    const randomId = Math.random().toString(36).substring(2, 15);
    localStorage.setItem("chat_session_id", randomId);
  }
  return localStorage.getItem("chat_session_id");
}




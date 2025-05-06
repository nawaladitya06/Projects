document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    
    // DOM elements
    const usernameModal = document.getElementById('username-modal');
    const usernameInput = document.getElementById('username-input');
    const joinButton = document.getElementById('join-button');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const usersList = document.getElementById('users-list');
    const typingIndicator = document.getElementById('typing-indicator');
    
    let username;
    let typingTimer;
    
    // Join chat when the user submits their username
    joinButton.addEventListener('click', () => {
      username = usernameInput.value.trim();
      
      if (username) {
        socket.emit('user-join', username);
        usernameModal.style.display = 'none';
      }
    });
    
    // Allow Enter key to send messages
    usernameInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        joinButton.click();
      }
    });
    
    // Send message
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
      
      // Emit typing event
      socket.emit('typing');
      
      // Clear previous timer
      clearTimeout(typingTimer);
      
      // Set new timer
      typingTimer = setTimeout(() => {
        socket.emit('stop-typing');
      }, 1000);
    });
    
    function sendMessage() {
      const message = messageInput.value.trim();
      
      if (message) {
        socket.emit('chat-message', message);
        messageInput.value = '';
      }
    }
    
    // Socket events
    socket.on('user-joined', (data) => {
      addSystemMessage(data.message);
      updateUsersList(data.users);
    });
    
    socket.on('user-left', (data) => {
      addSystemMessage(data.message);
    });
    
    socket.on('users-list', (users) => {
      updateUsersList(users);
    });
    
    socket.on('message', (data) => {
      displayMessage(data);
    });
    
    socket.on('user-typing', (username) => {
      typingIndicator.textContent = `${username} is typing...`;
      
      // Clear the typing indicator after 2 seconds
      setTimeout(() => {
        typingIndicator.textContent = '';
      }, 2000);
    });
    
    // Helper functions
    function displayMessage(data) {
      const messageElement = document.createElement('div');
      
      if (data.userId === socket.id) {
        messageElement.className = 'message sent';
      } else {
        messageElement.className = 'message received';
      }
      
      const messageHeader = document.createElement('div');
      messageHeader.className = 'message-header';
      
      const usernameSpan = document.createElement('span');
      usernameSpan.className = 'username';
      usernameSpan.textContent = data.username;
      
      const timestampSpan = document.createElement('span');
      timestampSpan.className = 'timestamp';
      timestampSpan.textContent = data.timestamp;
      
      messageHeader.appendChild(usernameSpan);
      messageHeader.appendChild(timestampSpan);
      
      const messageContent = document.createElement('div');
      messageContent.className = 'message-content';
      messageContent.textContent = data.message;
      
      messageElement.appendChild(messageHeader);
      messageElement.appendChild(messageContent);
      
      chatMessages.appendChild(messageElement);
      
      // Scroll to the bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addSystemMessage(message) {
      const messageElement = document.createElement('div');
      messageElement.className = 'message system';
      messageElement.textContent = message;
      
      chatMessages.appendChild(messageElement);
      
      // Scroll to the bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function updateUsersList(users) {
      usersList.innerHTML = '';
      
      users.forEach(user => {
        const listItem = document.createElement('li');
        listItem.textContent = user;
        usersList.appendChild(listItem);
      });
    }
  });
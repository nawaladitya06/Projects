const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIO(server);

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Store connected users
const users = {};

// Socket.IO connection handler
io.on('connection', (socket) => {
  console.log('New user connected:', socket.id);

  // Handle user joining
  socket.on('user-join', (username) => {
    users[socket.id] = username;
    
    // Broadcast to all users that someone has joined
    io.emit('user-joined', {
      userId: socket.id,
      username: username,
      users: Object.values(users),
      message: `${username} has joined the chat`
    });
    
    // Send current users list to the new user
    socket.emit('users-list', Object.values(users));
  });

  // Handle chat messages
  socket.on('chat-message', (message) => {
    io.emit('message', {
      userId: socket.id,
      username: users[socket.id],
      message: message,
      timestamp: new Date().toLocaleTimeString()
    });
  });

  // Handle typing indicator
  socket.on('typing', () => {
    socket.broadcast.emit('user-typing', users[socket.id]);
  });

  // Handle user disconnection
  socket.on('disconnect', () => {
    if (users[socket.id]) {
      io.emit('user-left', {
        userId: socket.id,
        username: users[socket.id],
        message: `${users[socket.id]} has left the chat`
      });
      
      delete users[socket.id];
      io.emit('users-list', Object.values(users));
    }
    
    console.log('User disconnected:', socket.id);
  });
});

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

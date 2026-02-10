const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('user-username').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

const chatLog = document.getElementById('chat-log');
const typingIndicator = document.getElementById('typing-indicator');

// Notification Setup
const notificationCheckbox = document.getElementById('notification-checkbox');

// Initialize from localStorage
const storedNotificationPref = localStorage.getItem('chat_notifications');
if (storedNotificationPref === 'true') {
    notificationCheckbox.checked = true;
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
}

notificationCheckbox.addEventListener('change', function () {
    if (this.checked) {
        if (!("Notification" in window)) {
            alert("This browser does not support desktop notifications");
            this.checked = false;
        } else if (Notification.permission === "granted") {
            localStorage.setItem('chat_notifications', 'true');
            new Notification("Notifications Enabled", { body: "You will catch all new messages!" });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    localStorage.setItem('chat_notifications', 'true');
                    new Notification("Notifications Enabled", { body: "You will catch all new messages!" });
                } else {
                    notificationCheckbox.checked = false;
                    localStorage.setItem('chat_notifications', 'false');
                }
            });
        } else {
            // value is 'denied'
            alert("Please enable notifications in your browser settings.");
            this.checked = false;
        }
    } else {
        localStorage.setItem('chat_notifications', 'false');
    }
});

chatSocket.onopen = function (e) {
    console.log('Chat socket connected');
    document.querySelector('.status-indicator').textContent = 'Connected';
    document.querySelector('.status-indicator').classList.add('connected');
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
    document.querySelector('.status-indicator').textContent = 'Disconnected';
    document.querySelector('.status-indicator').classList.remove('connected');
};

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.type === 'chat_message') {
        const message = data.message;
        const sender = data.username;
        const isMe = sender === username;

        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${isMe ? 'sent' : 'received'}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        const userDisplay = document.createElement('small');
        userDisplay.className = 'message-user';
        userDisplay.textContent = sender;

        const content = document.createElement('p');
        content.textContent = message;

        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        bubble.appendChild(userDisplay);
        bubble.appendChild(content);
        bubble.appendChild(time);
        wrapper.appendChild(bubble);

        chatLog.appendChild(wrapper);
        scrollToBottom();

        // Remove typing indicator if the message is from the person typing
        if (typingUser === sender) {
            typingIndicator.textContent = '';
            typingUser = null;
        }

        // Send Notification
        if (!isMe && notificationCheckbox.checked && !document.hasFocus()) {
            showNotification(`New message from ${sender}`, message);
        } else if (!isMe && notificationCheckbox.checked) {
            // Optional: Still notify even if focused? User asked "when one person send the message"
            // Let's stick to notifying if not focused OR if it's cleaner to always notify?
            // Usually, notifications are annoying if you are looking at the chat.
            // But let's assume if it's enabled, they want it.
            // Actually, browsers might block notifications if the tab is focused sometimes, or it's just redundant.
            // I'll stick to !document.hasFocus() OR document.hidden check, but the user requirement was simple.
            // Let's do it always if enabled, checking visibility check might be better.
            showNotification(`New message from ${sender}`, message);
        }

    } else if (data.type === 'typing') {
        if (data.username !== username) {
            handleTyping(data.username, data.is_typing);
        }
    } else if (data.type === 'ack') {
        console.log('Message delivered:', data.message);
        // Could update UI to show "Delivered"
    }
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;

    if (message.trim() === "") return;

    chatSocket.send(JSON.stringify({
        'type': 'chat_message',
        'message': message
    }));
    messageInputDom.value = '';

    // Stop typing immediately when sent
    sendTypingStatus(false);
};

// Typing Indicators
let typingTimer;
let typingUser = null;
const doneTypingInterval = 2000;
const input = document.getElementById('chat-message-input');

input.addEventListener('input', () => {
    sendTypingStatus(true);
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => sendTypingStatus(false), doneTypingInterval);
});

function sendTypingStatus(isTyping) {
    if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            'type': 'typing',
            'is_typing': isTyping
        }));
    }
}

function handleTyping(user, isTyping) {
    if (isTyping) {
        typingIndicator.innerHTML = `<span class="typing-text">${user} is typing</span>
                                     <div class="typing-dots">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                     </div>`;
        typingUser = user;
    } else {
        typingIndicator.textContent = '';
        typingUser = null;
    }
}

function scrollToBottom() {
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Initial scroll
scrollToBottom();

function showNotification(title, body) {
    if (!("Notification" in window)) return;

    if (Notification.permission === "granted") {
        const notification = new Notification(title, {
            body: body,
            icon: '/static/images/logo.png' // Optional, if exists
        });

        notification.onclick = function () {
            window.focus();
            notification.close();
        };
    }
}

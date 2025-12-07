// ============================================
// Anony Chat - Room JavaScript
// ============================================

const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const isQuestionCheckbox = document.getElementById('is-question');
const emptyState = document.getElementById('empty-state');
let currentThreadId = null;

// Hide empty state when messages exist
function updateEmptyState() {
  const messages = chatContainer.querySelectorAll('.message');
  if (emptyState) {
    emptyState.style.display = messages.length > 0 ? 'none' : 'flex';
  }
}

// メッセージを表示する関数
function appendMessage(msg) {
  // 重複チェック: 既に同じIDのメッセージがある場合は追加しない
  const existingMsg = document.getElementById(`msg-${msg.id}`);
  if (existingMsg) return;

  const div = document.createElement('div');
  div.id = `msg-${msg.id}`;
  div.className = `message ${msg.is_question ? 'question' : ''}`;

  // メッセージコンテンツをspan要素で包む
  const contentSpan = document.createElement('span');
  contentSpan.className = 'message-content';
  contentSpan.textContent = msg.content;
  div.appendChild(contentSpan);

  if (msg.is_question) {
    const icon = document.createElement('span');
    icon.className = 'thread-icon';
    icon.innerHTML = '💬 スレッド';
    icon.onclick = () => openThread(msg.id);
    div.appendChild(icon);
  }

  // Animation delay based on index for staggered appearance
  const messageCount = chatContainer.querySelectorAll('.message').length;
  div.style.animationDelay = `${Math.min(messageCount * 0.05, 0.3)}s`;

  chatContainer.appendChild(div);

  // 新しいメッセージのIDが現在のlastMessageIdより大きい場合更新
  if (msg.id > lastMessageId) {
    lastMessageId = msg.id;
  }

  // Smooth scroll to bottom
  chatContainer.scrollTo({
    top: chatContainer.scrollHeight,
    behavior: 'smooth'
  });

  updateEmptyState();
}

// メッセージ一覧を取得
let lastMessageId = 0;
async function fetchMessages() {
  try {
    let url = `/team_terrace/api/room/${roomId}/messages/list/`;
    if (lastMessageId > 0) {
      url += `?after_id=${lastMessageId}`;
    }

    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      if (data.messages.length > 0) {
        data.messages.forEach(appendMessage);
      }
      updateEmptyState();
    }
  } catch (error) {
    console.error('Failed to fetch messages:', error);
  }
}

// メッセージ送信
async function sendMessage() {
  const content = messageInput.value.trim();
  const isQuestion = isQuestionCheckbox.checked;
  if (!content) return;

  // Disable button during send
  sendButton.disabled = true;

  try {
    const res = await fetch(`/team_terrace/api/room/${roomId}/messages/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ content: content, is_question: isQuestion })
    });

    if (res.ok) {
      messageInput.value = '';
      isQuestionCheckbox.checked = false;
      const newMsg = await res.json();
      appendMessage(newMsg);
    }
  } catch (error) {
    console.error('Failed to send message:', error);
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

// --- Thread Modal Logic ---
const modal = document.getElementById('thread-modal');
const threadMessages = document.getElementById('thread-messages');
const replyInput = document.getElementById('reply-input');

async function openThread(messageId) {
  currentThreadId = messageId;
  modal.style.display = "block";

  // Loading state
  threadMessages.innerHTML = `
    <div class="loading-indicator">
      <div class="loading-dot"></div>
      <div class="loading-dot"></div>
      <div class="loading-dot"></div>
    </div>
  `;

  try {
    const res = await fetch(`/team_terrace/api/messages/${messageId}/replies/list/`);
    if (res.ok) {
      const data = await res.json();
      threadMessages.innerHTML = '';

      if (data.replies.length === 0) {
        threadMessages.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">返信はまだありません</p>';
      } else {
        data.replies.forEach((r, index) => {
          const div = document.createElement('div');
          div.className = 'reply';
          div.textContent = r.content;
          div.style.animationDelay = `${index * 0.1}s`;
          threadMessages.appendChild(div);
        });
      }
    }
  } catch (error) {
    threadMessages.innerHTML = '<p style="color: var(--text-muted); text-align: center;">読み込みエラー</p>';
  }

  // Focus reply input
  setTimeout(() => replyInput.focus(), 100);
}

function closeModal() {
  modal.style.display = "none";
  currentThreadId = null;
}

async function sendReply() {
  if (!currentThreadId) return;
  const content = replyInput.value.trim();
  if (!content) return;

  try {
    const res = await fetch(`/team_terrace/api/messages/${currentThreadId}/replies/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ content: content })
    });

    if (res.ok) {
      replyInput.value = '';
      openThread(currentThreadId); // Reload replies
    }
  } catch (error) {
    console.error('Error sending reply:', error);
  }
}

// Close modal on backdrop click
window.onclick = function (event) {
  if (event.target == modal) {
    closeModal();
  }
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.style.display === 'block') {
    closeModal();
  }
});

// Reply input Enter key
replyInput?.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendReply();
});

// --------------------------

// CSRFトークン取得のためのヘルパー関数
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

// 初回ロード
fetchMessages();
fetchReactions();

// ポーリング開始 (2秒間隔)
setInterval(() => {
  fetchMessages();
  fetchReactions();
}, 2000);

// --- Reaction Logic ---
let lastReactionId = 0;

async function sendReaction(type) {
  try {
    const res = await fetch(`/team_terrace/api/room/${roomId}/reactions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ reaction_type: type })
    });
    if (res.ok) {
      showReactionAnimation(type);
    }
  } catch (error) {
    console.error('Error sending reaction:', error);
  }
}

async function fetchReactions() {
  try {
    const res = await fetch(`/team_terrace/api/room/${roomId}/reactions/list/`);
    if (res.ok) {
      const data = await res.json();
      let maxId = lastReactionId;
      data.reactions.forEach(r => {
        if (r.id > lastReactionId) {
          if (lastReactionId !== 0) {
            showReactionAnimation(r.reaction_type);
          }
          if (r.id > maxId) maxId = r.id;
        }
      });
      lastReactionId = maxId;
    }
  } catch (error) {
    console.error('Error fetching reactions:', error);
  }
}

function showReactionAnimation(type) {
  const canvas = document.getElementById('reaction-canvas');
  const el = document.createElement('div');
  el.className = 'floating-reaction';

  const emojis = {
    'like': '👍',
    'heh': '😮',
    'question': '❓',
    'clap': '👏'
  };

  el.textContent = emojis[type] || '✨';

  // Random horizontal position (10% - 90%)
  const randomLeft = Math.floor(Math.random() * 80) + 10;
  el.style.left = randomLeft + '%';

  // Slight random delay for multiple reactions
  el.style.animationDelay = `${Math.random() * 0.2}s`;

  canvas.appendChild(el);

  // Remove element after animation completes
  setTimeout(() => {
    el.remove();
  }, 2700);
}

// Initial empty state check
updateEmptyState();

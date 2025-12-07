const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const isQuestionCheckbox = document.getElementById('is-question');
let currentThreadId = null;

// メッセージを表示する関数
function appendMessage(msg) {
  // 重複チェック: 既に同じIDのメッセージがある場合は追加しない
  const existingMsg = document.getElementById(`msg-${msg.id}`);
  if (existingMsg) return;

  const div = document.createElement('div');
  div.id = `msg-${msg.id}`; // IDを付与
  div.className = `message ${msg.is_question ? 'question' : ''}`;
  div.textContent = msg.content;

  if (msg.is_question) {
    const icon = document.createElement('span');
    icon.className = 'thread-icon';
    icon.textContent = '💬 スレッド';
    icon.onclick = () => openThread(msg.id);
    div.appendChild(icon);
  }

  chatContainer.appendChild(div);
  // 新しいメッセージのIDが現在のlastMessageIdより大きい場合更新
  if (msg.id > lastMessageId) {
    lastMessageId = msg.id;
  }
  chatContainer.scrollTop = chatContainer.scrollHeight; // 最下部へスクロール
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
        // lastMessageId is updated in appendMessage
      }
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
  }
}

// --- Thread Modal Logic ---
const modal = document.getElementById('thread-modal');
const threadMessages = document.getElementById('thread-messages');
const replyInput = document.getElementById('reply-input');

async function openThread(messageId) {
  currentThreadId = messageId;
  modal.style.display = "block";
  threadMessages.innerHTML = 'Loading...';

  try {
    const res = await fetch(`/team_terrace/api/messages/${messageId}/replies/list/`);
    if (res.ok) {
      const data = await res.json();
      threadMessages.innerHTML = ''; // Clear loading
      if (data.replies.length === 0) {
        threadMessages.innerHTML = '<p>返信はまだありません。</p>';
      } else {
        data.replies.forEach(r => {
          const div = document.createElement('div');
          div.className = 'reply';
          div.textContent = r.content;
          threadMessages.appendChild(div);
        });
      }
    }
  } catch (error) {
    threadMessages.textContent = 'Error loading replies.';
  }
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
    alert('Error sending reply');
  }
}

window.onclick = function (event) {
  if (event.target == modal) {
    closeModal();
  }
}
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

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

// 初回ロード
fetchMessages();
fetchReactions(); // Start fetching reactions

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
          if (lastReactionId !== 0) { // Initial load suppression
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
  // Find body or chat container to append to. Body is safer for fixed position.
  const el = document.createElement('div');
  el.className = 'floating-reaction';

  let emoji = '';

  if (type === 'like') emoji = '👍';
  if (type === 'heh') emoji = '😮';
  if (type === 'question') emoji = '❓';
  if (type === 'clap') emoji = '👏';

  el.textContent = emoji;

  // Random horizontal position
  const randomLeft = Math.floor(Math.random() * 80) + 10; // 10% to 90%
  el.style.left = randomLeft + '%';

  document.body.appendChild(el);

  setTimeout(() => { el.remove(); }, 3000);
}

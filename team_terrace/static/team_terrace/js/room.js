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
  div.dataset.messageId = String(msg.id);
  div.className = `message ${msg.is_question ? 'question' : ''}`;

  // メッセージコンテンツをspan要素で包む
  const contentSpan = document.createElement('span');
  contentSpan.className = 'message-content';
  contentSpan.textContent = msg.content;
  div.appendChild(contentSpan);

  // Like Button
  const likeBtn = document.createElement('button');
  likeBtn.className = 'like-btn';
  likeBtn.onclick = () => toggleLike(msg.id);

  const heartIcon = document.createElement('span');
  heartIcon.className = 'heart-icon';
  heartIcon.textContent = '♥'; // or simple heart character

  const countSpan = document.createElement('span');
  countSpan.className = 'like-count';
  countSpan.id = `like-count-${msg.id}`;
  countSpan.textContent = '0';

  likeBtn.appendChild(heartIcon);
  likeBtn.appendChild(countSpan);
  div.appendChild(likeBtn);

  // Check if I liked this message
  const myLikes = getMyLikes();
  if (myLikes.includes(msg.id)) {
    likeBtn.classList.add('liked');
  }

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

// --- Like Feature ---
function getMyLikes() {
  const likes = localStorage.getItem('my_likes_terrace');
  return likes ? JSON.parse(likes) : [];
}

function addToMyLikes(messageId) {
  const likes = getMyLikes();
  if (!likes.includes(messageId)) {
    likes.push(messageId);
    localStorage.setItem('my_likes_terrace', JSON.stringify(likes));
  }
}

function removeFromMyLikes(messageId) {
  const likes = getMyLikes();
  const newLikes = likes.filter(id => id !== messageId);
  localStorage.setItem('my_likes_terrace', JSON.stringify(newLikes));
}

async function toggleLike(messageId) {
  const countSpan = document.getElementById(`like-count-${messageId}`);
  if (!countSpan) return;

  const btn = countSpan.parentElement;

  // Check local state
  const myLikes = getMyLikes();
  const isLiked = myLikes.includes(messageId);

  // Optimistic UI update
  let currentCount = parseInt(countSpan.textContent);

  if (isLiked) {
    // UNLIKE
    if (currentCount > 0) countSpan.textContent = currentCount - 1;
    btn.classList.remove('liked');
    removeFromMyLikes(messageId);

    try {
      const res = await fetch(`/team_terrace/api/messages/${messageId}/unlike/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      });
      if (res.ok) {
        const data = await res.json();
        countSpan.textContent = data.like_count;
      }
    } catch (error) {
      console.error('Error unliking:', error);
    }
  } else {
    // LIKE
    countSpan.textContent = currentCount + 1;
    btn.classList.add('liked');
    btn.classList.add('liked-anim');
    setTimeout(() => btn.classList.remove('liked-anim'), 300);
    addToMyLikes(messageId);

    try {
      const res = await fetch(`/team_terrace/api/messages/${messageId}/like/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      });
      if (res.ok) {
        const data = await res.json();
        countSpan.textContent = data.like_count;
      }
    } catch (error) {
      console.error('Error liking:', error);
    }
  }
}

function applyLikesToDOM(likesMap) {
  // Iterate all like-count elements in the DOM
  const countSpans = document.querySelectorAll('.like-count');
  countSpans.forEach(span => {
    const idStr = span.id.replace('like-count-', '');
    // If present in API response, use that count. Otherwise 0.
    const count = likesMap[idStr] || 0;
    span.textContent = count;
  });

  // Ensure my liked state styling is correct
  const myLikes = getMyLikes();
  myLikes.forEach(msgId => {
    const el = document.getElementById(`like-count-${msgId}`);
    if (el) {
      el.parentElement.classList.add('liked');
    }
  });
}

async function fetchLikes() {
  try {
    const res = await fetch(`/team_terrace/api/room/${roomId}/likes/`);
    if (!res.ok) return {};

    const data = await res.json();
    const likesMap = data.likes || {}; // { message_id: count }

    applyLikesToDOM(likesMap);
    return likesMap;
  } catch (error) {
    console.error('Error fetching likes:', error);
    return {};
  }
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
fetchLikes();

// いいね順に手動で並び替え（更新）する
function sortMessagesByLikes(likesMap) {
  // Only reorder existing message elements; do not change polling behavior.
  const messages = Array.from(chatContainer.querySelectorAll('.message'));

  const getLikeCount = (el) => {
    const id = el.dataset.messageId;
    if (!id) return 0;
    const n = likesMap?.[id] ?? 0;
    return Number.isFinite(n) ? n : 0;
  };

  messages.sort((a, b) => {
    const la = getLikeCount(a);
    const lb = getLikeCount(b);
    if (lb !== la) return lb - la; // desc

    // tie-breaker: older first (smaller id) to keep stable ordering
    const ida = parseInt(a.dataset.messageId || '0', 10);
    const idb = parseInt(b.dataset.messageId || '0', 10);
    return ida - idb;
  });

  // Re-append in sorted order
  for (const el of messages) chatContainer.appendChild(el);
}

// Sort mode controls
const sortModeTimeBtn = document.getElementById('sort-mode-time');
const sortModeLikesBtn = document.getElementById('sort-mode-likes');
const sortLikesUpdateBtn = document.getElementById('sort-likes-update');

let sortMode = 'time'; // 'time' | 'likes'

function applySortModeUI() {
  const likesMode = sortMode === 'likes';
  if (sortModeTimeBtn) sortModeTimeBtn.classList.toggle('active', !likesMode);
  if (sortModeLikesBtn) sortModeLikesBtn.classList.toggle('active', likesMode);
  if (sortLikesUpdateBtn) {
    // Keep width reserved so the segment doesn't shift.
    sortLikesUpdateBtn.classList.toggle('is-hidden', !likesMode);
  }
}

function restoreTimeOrder() {
  const messages = Array.from(chatContainer.querySelectorAll('.message'));
  messages.sort((a, b) => {
    const ida = parseInt(a.dataset.messageId || '0', 10);
    const idb = parseInt(b.dataset.messageId || '0', 10);
    return ida - idb;
  });
  for (const el of messages) chatContainer.appendChild(el);
}

function setSortMode(mode) {
  sortMode = mode;
  applySortModeUI();

  if (sortMode === 'likes') {
    // On entering likes mode: refresh counts then sort once.
    fetchLikes().then((likesMap) => sortMessagesByLikes(likesMap));
  } else {
    restoreTimeOrder();
  }
}

if (sortModeTimeBtn) sortModeTimeBtn.addEventListener('click', () => setSortMode('time'));
if (sortModeLikesBtn) sortModeLikesBtn.addEventListener('click', () => setSortMode('likes'));

if (sortLikesUpdateBtn) {
  sortLikesUpdateBtn.addEventListener('click', async () => {
    const likesMap = await fetchLikes();
    sortMessagesByLikes(likesMap);
  });
}

// Initial state: time mode
setSortMode('time');

// ポーリング開始 (2秒間隔)
setInterval(() => {
  fetchMessages();
  fetchReactions();
  fetchLikes();
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

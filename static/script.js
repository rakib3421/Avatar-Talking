const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const personalitySelect = document.getElementById("personality-select");
const userAvatarSelect = document.getElementById("user-avatar-select");
const aiAvatarSelect = document.getElementById("ai-avatar-select");
const aliceBubble = document.getElementById("bubble-alice");
const noraBubble = document.getElementById("bubble-nora");
const userVideo = document.getElementById("user-video");
const aiVideo = document.getElementById("ai-video");

let recognition;

function playVideo(videoEl) {
  videoEl.currentTime = 0;
  videoEl.play();
}

function pauseVideo(videoEl) {
  videoEl.pause();
}

async function handleUserMessage(message) {
  if (!message) return;

  const personality = personalitySelect?.value || "friendly";

  aliceBubble.textContent = message;
  noraBubble.textContent = "⏳ typing...";

  const res = await fetch('/speak', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: message, mode: personality })
  });

  const data = await res.json();

  const userAudio = new Audio(data.user_audio_url);
  const aiAudio = new Audio(data.ai_audio_url);

  userAudio.play();
  playVideo(userVideo);

  userAudio.onended = () => {
    pauseVideo(userVideo);
    noraBubble.textContent = data.reply;
    playVideo(aiVideo);
    aiAudio.play();

    aiAudio.onended = () => {
      pauseVideo(aiVideo);
      startMicRecognition();
    };
  };

  chatInput.value = '';
}

function startMicRecognition() {
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
  };

  recognition.onend = () => {
    const message = chatInput.value.trim();
    handleUserMessage(message);
  };
}

// Avatar switching logic (and make static by default)
userAvatarSelect.addEventListener("change", () => {
  const newSrc = userAvatarSelect.value;
  userVideo.src = newSrc;
  userVideo.load();
  pauseVideo(userVideo);
  localStorage.setItem("userAvatar", newSrc);
});

aiAvatarSelect.addEventListener("change", () => {
  const newSrc = aiAvatarSelect.value;
  aiVideo.src = newSrc;
  aiVideo.load();
  pauseVideo(aiVideo);
  localStorage.setItem("aiAvatar", newSrc);
});

micBtn.addEventListener("click", () => {
  startMicRecognition();
});

sendBtn.addEventListener("click", () => {
  const message = chatInput.value.trim();
  handleUserMessage(message);
});

window.addEventListener("DOMContentLoaded", () => {
  pauseVideo(userVideo);
  pauseVideo(aiVideo);

  const savedUser = localStorage.getItem("userAvatar");
  const savedAI = localStorage.getItem("aiAvatar");
  if (savedUser) {
    userVideo.src = savedUser;
    userAvatarSelect.value = savedUser;
    userVideo.load();
    pauseVideo(userVideo);
  }
  if (savedAI) {
    aiVideo.src = savedAI;
    aiAvatarSelect.value = savedAI;
    aiVideo.load();
    pauseVideo(aiVideo);
  }
});

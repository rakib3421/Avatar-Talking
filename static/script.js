const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
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

function startMicRecognition() {
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.start();

  playVideo(userVideo); // Start user talking animation

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
  };

  recognition.onend = async () => {
    pauseVideo(userVideo); // Stop user video
    const message = chatInput.value.trim();
    if (!message) return;

    aliceBubble.textContent = message;
    noraBubble.textContent = "⏳ typing...";

    const res = await fetch('/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: message })
    });

    const data = await res.json();
    noraBubble.textContent = data.reply;

    playVideo(aiVideo); // Start AI reply video

    const audio = new Audio(data.audio_url);
    audio.onended = () => {
      pauseVideo(aiVideo); // Stop AI reply video
      startMicRecognition(); // Loop back to user
    };

    audio.play();
    chatInput.value = '';
  };
}

micBtn.addEventListener("click", () => {
  startMicRecognition();
});

sendBtn.addEventListener("click", async () => {
  const message = chatInput.value.trim();
  if (!message) return;

  aliceBubble.textContent = message;
  noraBubble.textContent = "⏳ typing...";
  playVideo(userVideo);

  const res = await fetch('/speak', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: message })
  });

  const data = await res.json();
  pauseVideo(userVideo);
  noraBubble.textContent = data.reply;

  playVideo(aiVideo);
  const audio = new Audio(data.audio_url);
  audio.onended = () => {
    pauseVideo(aiVideo);
  };
  audio.play();

  chatInput.value = '';
});

// On load — pause both videos but keep them visible
window.addEventListener("DOMContentLoaded", () => {
  pauseVideo(userVideo);
  pauseVideo(aiVideo);
});
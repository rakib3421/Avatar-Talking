const userInput = document.getElementById("user-input");
const aiInput = document.getElementById("ai-input");
const userSendBtn = document.getElementById("user-send-btn");
const aiSendBtn = document.getElementById("ai-send-btn");
const userMicBtn = document.getElementById("user-mic-btn");
const aiMicBtn = document.getElementById("ai-mic-btn");
const personalitySelect = document.getElementById("personality-select");
const chatHistory = document.getElementById("chat-history");

const userVideo = document.getElementById("user-video");
const aiVideo = document.getElementById("ai-video");
const userAvatarSelect = document.getElementById("user-avatar-select");
const aiAvatarSelect = document.getElementById("ai-avatar-select");
const aiReplyFromSelect = document.getElementById("ai-reply-from");

let recognition;

function appendMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.textContent = text;
  chatHistory.appendChild(div);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function playAudio(video, audioUrl) {
  const audio = new Audio(audioUrl);

  audio.onloadedmetadata = () => {
    video.currentTime = 0;
    video.loop = true;
    video.play();
    audio.play();

    // When audio finishes, stop video
    audio.onended = () => {
      video.loop = false;
      video.pause();
      video.currentTime = 0;
    };
  };
}

async function generateAudioOnly(text, speaker) {
  const res = await fetch("/audio-only", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, speaker })
  });

  const data = await res.json();
  const video = speaker === "user" ? userVideo : aiVideo;
  playAudio(video, data.audio_url);
}

async function speakWithAI(text, mode) {
  const res = await fetch("/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, mode })
  });

  const data = await res.json();
  playAudio(aiVideo, data.ai_audio_url);
  return data.reply;
}

async function handleUserChat() {
  const userMsg = userInput.value.trim();
  if (!userMsg) return;

  appendMessage(userMsg, "user");
  await generateAudioOnly(userMsg, "user");

  if (aiReplyFromSelect.value === "ai") {
    const mode = personalitySelect.value;
    const aiReply = await speakWithAI(userMsg, mode);
    appendMessage(aiReply, "ai");
  }

  userInput.value = "";
}

async function handleAIChat() {
  const aiMsg = aiInput.value.trim();
  if (!aiMsg || aiReplyFromSelect.value === "ai") return;

  appendMessage(aiMsg, "ai");
  await generateAudioOnly(aiMsg, "ai");
  aiInput.value = "";
}

function startMic(targetInput, autoSend = false, role = "user") {
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-US";
  recognition.start();

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    targetInput.value = transcript;

    if (!autoSend) return;

    const replyMode = aiReplyFromSelect.value;

    if (role === "user") {
      appendMessage(transcript, "user");
      await generateAudioOnly(transcript, "user");

      if (replyMode === "ai") {
        const mode = personalitySelect.value;
        const aiReply = await speakWithAI(transcript, mode);
        appendMessage(aiReply, "ai");
      }

      userInput.value = "";
    }

    if (role === "ai" && replyMode === "user") {
      appendMessage(transcript, "ai");
      await generateAudioOnly(transcript, "ai");
      aiInput.value = "";
    }
  };
}

// Event Listeners
userSendBtn.addEventListener("click", handleUserChat);
userInput.addEventListener("keydown", e => {
  if (e.key === "Enter") handleUserChat();
});
userMicBtn.addEventListener("click", () => startMic(userInput, true, "user"));

aiSendBtn.addEventListener("click", handleAIChat);
aiMicBtn.addEventListener("click", () => startMic(aiInput, true, "ai"));

userAvatarSelect.addEventListener("change", () => {
  userVideo.src = userAvatarSelect.value;
  userVideo.load();
  userVideo.pause();
});
aiAvatarSelect.addEventListener("change", () => {
  aiVideo.src = aiAvatarSelect.value;
  aiVideo.load();
  aiVideo.pause();
});

window.addEventListener("DOMContentLoaded", () => {
  userVideo.src = userAvatarSelect.value;
  aiVideo.src = aiAvatarSelect.value;
  userVideo.pause();
  aiVideo.pause();
});
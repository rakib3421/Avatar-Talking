from flask import Flask, render_template, request, jsonify
import os, uuid, re, requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Voice IDs from ElevenLabs (you can replace with your preferred ones)
USER_VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"
AI_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

# Remove emojis and special characters
def clean_text(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove unicode leftovers
    return text

# Generate TTS audio using ElevenLabs
def generate_elevenlabs_audio(text, voice_id, filename):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.9
        }
    }

    for attempt in range(2):  # Try twice
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return
        else:
            print(f"[WARN] ElevenLabs failed, attempt {attempt + 1}, status: {response.status_code}")

    raise Exception("ElevenLabs audio generation failed.")

# Route for frontend
@app.route("/")
def index():
    return render_template("index.html")

# Main route to handle chat
@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    user_text = data.get("text")
    mode = data.get("mode", "friendly")

    if not user_text:
        return jsonify({"error": "No input text provided."}), 400

    # Different personalities
    personality_prompts = {
        "friendly": "You're casual, kind, like a best friend. Short, natural, and real.",
        "funny": "You’re witty and humorous. Add a little sarcasm, jokes, or clever puns.",
        "flirty": "You’re playful and flirty. Tease gently and compliment.",
        "wise": "You speak like a thoughtful sage. Offer deep, reflective advice.",
        "formal": "You speak in a professional, respectful, and polished tone."
    }
    personality = personality_prompts.get(mode, personality_prompts["friendly"])

    # Prompt for Gemini
    prompt = f"""
    Forget you're an AI. You're a real person chatting with someone you know well.
    Tone: {personality}
    Rules:
    - Avoid sounding robotic or assistant-like.
    - Do not use emojis or overly formal phrases.
    - Keep it under 2-3 sentences max.
    - Use natural speech patterns (e.g., “kinda”, “yeah”, “gotcha” if appropriate).

    Conversation so far:
    Them: {user_text}
    You:"""
    # Generate AI reply using Gemini
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    ai_reply = clean_text(response.text.strip())

    # Audio filenames
    audio_id = uuid.uuid4().hex
    user_audio_filename = f"static/audio/user_{audio_id}.mp3"
    ai_audio_filename = f"static/audio/ai_{audio_id}.mp3"

    # Try to generate audio using ElevenLabs, fallback to gTTS
    try:
        generate_elevenlabs_audio(user_text, USER_VOICE_ID, user_audio_filename)
        generate_elevenlabs_audio(ai_reply, AI_VOICE_ID, ai_audio_filename)
    except Exception as e:
        print("Fallback to gTTS due to error:", e)
        from gtts import gTTS
        gTTS(user_text).save(user_audio_filename)
        gTTS(ai_reply).save(ai_audio_filename)

    # Return everything to frontend
    return jsonify({
        "reply": ai_reply,
        "user_audio_url": "/" + user_audio_filename,
        "ai_audio_url": "/" + ai_audio_filename
    })

@app.route("/audio-only", methods=["POST"])
def audio_only():
    data = request.json
    text = data.get("text")
    speaker = data.get("speaker", "user")
    if not text:
        return jsonify({"error": "No text provided."}), 400

    audio_id = uuid.uuid4().hex
    filename = f"static/audio/{speaker}_{audio_id}.mp3"
    voice_id = USER_VOICE_ID if speaker == "user" else AI_VOICE_ID

    try:
        generate_elevenlabs_audio(text, voice_id, filename)
    except Exception as e:
        from gtts import gTTS
        gTTS(text).save(filename)

    return jsonify({
        "audio_url": "/" + filename
    })

# Make sure audio folder exists and run app
if __name__ == "__main__":
    os.makedirs("static/audio", exist_ok=True)
    app.run(debug=True)
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

# Voice IDs
USER_VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"
AI_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

def clean_text(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

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
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error: ElevenLabs API returned {response.status_code}")
        raise Exception("Failed to generate audio")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    user_text = data.get("text")
    mode = data.get("mode", "friendly")

    if not user_text:
        return jsonify({"error": "No input text provided."}), 400

    personality_prompts = {
        "friendly": "You're casual, kind, like a best friend. Short, natural, and real.",
        "funny": "You’re witty and humorous. Add a little sarcasm, jokes, or clever puns.",
        "flirty": "You’re playful and flirty. Tease gently and compliment.",
        "wise": "You speak like a thoughtful sage. Offer deep, reflective advice.",
        "formal": "You speak in a professional, respectful, and polished tone."
    }
    personality = personality_prompts.get(mode, personality_prompts["friendly"])

    prompt = (
        f"You are not an assistant. You're a cool, casual human friend. "
        f"Speak naturally like texting. No emojis. Be fun or relaxed, based on the mode.\n\n"
        f"{personality}\n\n"
        f"Here's what they just said:\n"
        f"{user_text}\n\n"
        f"Reply casually, as if you're continuing a real convo."
    )

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    ai_reply = clean_text(response.text.strip())

    audio_id = uuid.uuid4().hex
    user_audio_filename = f"static/audio/user_{audio_id}.mp3"
    ai_audio_filename = f"static/audio/ai_{audio_id}.mp3"

    try:
        generate_elevenlabs_audio(user_text, USER_VOICE_ID, user_audio_filename)
        generate_elevenlabs_audio(ai_reply, AI_VOICE_ID, ai_audio_filename)
    except Exception as e:
        print("Fallback to gTTS due to error:", e)
        from gtts import gTTS
        gTTS(user_text).save(user_audio_filename)
        gTTS(ai_reply).save(ai_audio_filename)

    return jsonify({
        "reply": ai_reply,
        "user_audio_url": "/" + user_audio_filename,
        "ai_audio_url": "/" + ai_audio_filename
    })

# 🔥 ADD THIS NEW ROUTE
@app.route("/audio-only", methods=["POST"])
def audio_only():
    data = request.json
    text = data.get("text")
    speaker = data.get("speaker")

    if not text or speaker not in ["user", "ai"]:
        return jsonify({"error": "Missing or invalid input."}), 400

    voice_id = USER_VOICE_ID if speaker == "user" else AI_VOICE_ID
    audio_id = uuid.uuid4().hex
    filename = f"static/audio/{speaker}_{audio_id}.mp3"

    try:
        generate_elevenlabs_audio(text, voice_id, filename)
    except Exception as e:
        print("Fallback to gTTS due to error:", e)
        from gtts import gTTS
        gTTS(text).save(filename)

    return jsonify({"audio_url": "/" + filename})

if __name__ == "__main__":
    os.makedirs("static/audio", exist_ok=True)
    app.run(debug=True)
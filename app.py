from flask import Flask, render_template, request, jsonify
import os, uuid
from gtts import gTTS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    user_text = data.get("text")

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = (
        f"You are having a casual, friendly, and natural conversation with someone. "
        f"Reply like you're a close friend — keep it short, chill, and real. "
        f"Don't sound robotic or overly formal. Here's what they said:\n\n"
        f"{user_text}"
    )

    response = model.generate_content(prompt)
    ai_reply = response.text.strip()

    audio_id = uuid.uuid4().hex
    filename = f"static/audio/ai_{audio_id}.mp3"
    gTTS(ai_reply).save(filename)

    return jsonify({
        "reply": ai_reply,
        "audio_url": "/" + filename
    })

if __name__ == "__main__":
    os.makedirs("static/audio", exist_ok=True)
    app.run(debug=True)
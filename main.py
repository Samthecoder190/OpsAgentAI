import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

OLLAMA_URL = "https://ollama.com"
OLLAMA_MODEL = "glm-5.3-flash"


def get_ollama_headers():
    api_key = os.getenv("OLLAMA_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing OLLAMA_API_KEY. Save it in a .env file as OLLAMA_API_KEY=your_key_here")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def call_ollama(prompt):
    headers = get_ollama_headers()
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code == 401:
        raise RuntimeError("Ollama rejected the key with 401. Check OLLAMA_API_KEY.")
    if response.status_code == 402:
        raise RuntimeError("Ollama requires usage credits for this account (402).")
    if response.status_code == 404:
        raise RuntimeError("Model glm-5.3-flash was not found (404).")
    if response.status_code == 429:
        raise RuntimeError("Ollama usage limit reached (429).")

    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


@app.route("/", methods=["GET"])
def index():
    return {
        "status": "ok",
        "message": "OpsAgentAI is ready. Use POST /api/chat with a JSON body containing a prompt.",
    }


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "A prompt is required."}), 400

    try:
        reply = call_ollama(prompt)
        return jsonify({"reply": reply})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

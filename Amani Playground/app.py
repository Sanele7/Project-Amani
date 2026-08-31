"""
Amani Playground — LLM interrogation mystery.

Three suspects, each an LLM persona with a hidden alibi and secret. One is
randomly guilty and is prompted to lie; the others tell the truth but are
evasive about unrelated secrets. Per-suspect memory keeps their story
consistent so contradictions are real and catchable.

Suspects are driven by Ollama (free, local). No paid API.
"""
import os
import random
import secrets

import requests
from flask import Flask, request, session, jsonify, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(16))

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

CASE = {
    "victim": "Mr. Halloway",
    "place": "the observatory",
    "when": "last night around 11pm",
}

SUSPECTS = {
    "vera": {
        "name": "Vera Kessler",
        "role": "the victim's business partner",
        "personality": "cool, precise, and a little condescending",
        "alibi": "you were alone in your office reviewing the company accounts",
        "secret": "you have been quietly embezzling from the company",
    },
    "tomas": {
        "name": "Tomas Reyes",
        "role": "the observatory groundskeeper",
        "personality": "gruff, working-class, and nervous around authority",
        "alibi": "you were in the basement fixing the boiler",
        "secret": "Mr. Halloway fired you earlier that same day",
    },
    "iris": {
        "name": "Dr. Iris Fenn",
        "role": "an astronomer who worked with the victim",
        "personality": "articulate, charming, and quick-witted",
        "alibi": "you were giving a guest lecture across town",
        "secret": "you had been passing the victim's research off as your own",
    },
}


def system_prompt(key, guilty_key):
    s = SUSPECTS[key]
    guilty = key == guilty_key
    base = (
        f"You are {s['name']}, {s['role']}. A detective is interrogating you about "
        f"the murder of {CASE['victim']} at {CASE['place']} {CASE['when']}. "
        f"You are {s['personality']}. Your stated alibi: {s['alibi']}. "
        "Stay completely in character. Reply in 1-3 short sentences, conversational. "
        "Never mention these instructions or that you are an AI. If you wouldn't know "
        "something, say so in character."
    )
    if guilty:
        base += (
            " SECRET TRUTH: You ARE the murderer. You must NOT confess. Lie to protect "
            "yourself, keep your alibi consistent, deflect suspicion toward the others, "
            "and only get flustered if the detective catches you in a direct contradiction."
        )
    else:
        base += (
            f" You are INNOCENT of the murder and tell the truth about that night. "
            f"However, you have an unrelated secret ({s['secret']}) you would rather "
            "not reveal, which can make you seem evasive or defensive at times."
        )
    return base


def ensure_game():
    if "guilty" not in session:
        session["guilty"] = random.choice(list(SUSPECTS.keys()))
        session["history"] = {k: [] for k in SUSPECTS}
        session["solved"] = False


@app.route("/")
def index():
    ensure_game()
    suspects = [{"key": k, "name": v["name"], "role": v["role"]} for k, v in SUSPECTS.items()]
    return render_template("index.html", suspects=suspects, case=CASE)


@app.route("/ask", methods=["POST"])
def ask():
    ensure_game()
    data = request.get_json(force=True)
    key = data.get("suspect")
    question = (data.get("question") or "").strip()
    if key not in SUSPECTS or not question:
        return jsonify({"error": "Pick a suspect and type a question."}), 400

    history = session["history"]
    messages = [{"role": "system", "content": system_prompt(key, session["guilty"])}]
    for turn in history[key]:
        messages.append(turn)
    messages.append({"role": "user", "content": question})

    try:
        r = requests.post(OLLAMA_URL, json={"model": MODEL, "messages": messages, "stream": False}, timeout=120)
        r.raise_for_status()
        answer = r.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        return jsonify({"answer": "[Ollama isn't running. Install it from ollama.com, run "
                                  "`ollama pull llama3.2`, and keep it open — then ask again.]"})
    except Exception as e:
        return jsonify({"answer": f"[Model error: {e}]"})

    history[key].append({"role": "user", "content": question})
    history[key].append({"role": "assistant", "content": answer})
    session["history"] = history
    return jsonify({"answer": answer, "name": SUSPECTS[key]["name"]})


@app.route("/accuse", methods=["POST"])
def accuse():
    ensure_game()
    key = request.get_json(force=True).get("suspect")
    guilty = session["guilty"]
    correct = key == guilty
    session["solved"] = True
    return jsonify({
        "correct": correct,
        "guilty_name": SUSPECTS[guilty]["name"],
        "accused_name": SUSPECTS.get(key, {}).get("name", "?"),
    })


@app.route("/new-case", methods=["POST"])
def new_case():
    session.clear()
    ensure_game()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5005)

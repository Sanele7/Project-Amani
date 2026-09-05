"""
Amani Playground — LLM interrogation mystery (build-out).

Now with: multiple cases, selectable difficulty, an evidence system you can
present mid-interrogation (the suspect must react), and a detective's notebook
that records every answer and auto-flags likely contradictions between what
suspects told you. Suspects run on Ollama (free, local).
"""
import os
import random
import secrets
import difflib

import requests
from flask import Flask, request, session, jsonify, render_template

import cases as casedb

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(16))

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# words that often signal a contradiction in an alibi statement
CONTRADICTION_HINTS = ["wasn't", "was not", "didn't", "did not", "never", "actually",
                       "lie", "lying", "mistaken", "wrong", "not true", "that's false"]


def new_game(case_key=None, difficulty="normal"):
    case_key = case_key or random.choice(list(casedb.CASES.keys()))
    case = casedb.CASES[case_key]
    session["case"] = case_key
    session["difficulty"] = difficulty
    session["guilty"] = random.choice(list(case["suspects"].keys()))
    session["history"] = {k: [] for k in case["suspects"]}
    session["notebook"] = []          # list of {suspect, q, a}
    session["evidence_shown"] = []     # evidence keys presented so far
    session["solved"] = False


def ensure_game():
    if "case" not in session:
        new_game()


def case_payload():
    case = casedb.CASES[session["case"]]
    return {
        "title": case["title"],
        "brief": case["brief"],
        "victim": case["victim"],
        "setting": case["setting"],
        "when": case["when"],
        "difficulty": session["difficulty"],
        "suspects": [{"key": k, "name": v["name"], "role": v["role"]}
                     for k, v in case["suspects"].items()],
        "evidence": [{"key": k, "name": v["name"]} for k, v in case["evidence"].items()],
    }


@app.route("/")
def index():
    ensure_game()
    return render_template("index.html", case=case_payload(),
                           cases=[{"key": k, "title": v["title"]} for k, v in casedb.CASES.items()])


def ask_model(messages):
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "messages": messages, "stream": False}, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def detect_contradictions(case_key, suspect_key, answer):
    """Very light heuristic: flag if a new answer echoes another suspect's name
    plus a negation, or contradicts the suspect's own earlier statements."""
    flags = []
    case = casedb.CASES[case_key]
    low = answer.lower()

    # Does this answer mention another suspect by first name with a negation nearby?
    for other_key, other in case["suspects"].items():
        if other_key == suspect_key:
            continue
        first = other["name"].split()[0].lower()
        if first in low and any(h in low for h in CONTRADICTION_HINTS):
            flags.append(f"{case['suspects'][suspect_key]['name']} said something pointing at {other['name']}.")

    # Does it contradict this suspect's own earlier answers (low text similarity on alibi topic)?
    for entry in session["notebook"]:
        if entry["suspect"] == suspect_key:
            sim = difflib.SequenceMatcher(None, entry["a"].lower(), low).ratio()
            if any(h in low for h in CONTRADICTION_HINTS) and sim < 0.5:
                flags.append(f"{case['suspects'][suspect_key]['name']}'s story may have shifted from an earlier answer.")
                break
    return flags


@app.route("/ask", methods=["POST"])
def ask():
    ensure_game()
    data = request.get_json(force=True)
    key = data.get("suspect")
    question = (data.get("question") or "").strip()
    case = casedb.CASES[session["case"]]
    if key not in case["suspects"] or not question:
        return jsonify({"error": "Pick a suspect and type a question."}), 400

    system = casedb.build_system_prompt(
        session["case"], key, session["guilty"], session["difficulty"], session["evidence_shown"])
    messages = [{"role": "system", "content": system}]
    messages += session["history"][key]
    messages.append({"role": "user", "content": question})

    try:
        answer = ask_model(messages)
    except requests.exceptions.ConnectionError:
        return jsonify({"answer": "[Ollama isn't running. Start it and run `ollama pull llama3.2`, then ask again.]",
                        "flags": []})
    except Exception as e:
        return jsonify({"answer": f"[Model error: {e}]", "flags": []})

    history = session["history"]
    history[key].append({"role": "user", "content": question})
    history[key].append({"role": "assistant", "content": answer})
    session["history"] = history

    flags = detect_contradictions(session["case"], key, answer)
    notebook = session["notebook"]
    notebook.append({"suspect": key, "name": case["suspects"][key]["name"], "q": question, "a": answer})
    session["notebook"] = notebook

    return jsonify({"answer": answer, "name": case["suspects"][key]["name"], "flags": flags})


@app.route("/present", methods=["POST"])
def present():
    """Present an evidence item to a suspect — they must react to it."""
    ensure_game()
    data = request.get_json(force=True)
    key = data.get("suspect")
    ev_key = data.get("evidence")
    case = casedb.CASES[session["case"]]
    if key not in case["suspects"] or ev_key not in case["evidence"]:
        return jsonify({"error": "Pick a suspect and an evidence item."}), 400

    shown = session["evidence_shown"]
    if ev_key not in shown:
        shown.append(ev_key)
        session["evidence_shown"] = shown

    ev = case["evidence"][ev_key]
    prompt = f"Detective presents evidence — {ev['name']}: {ev['detail']} What do you say?"
    system = casedb.build_system_prompt(
        session["case"], key, session["guilty"], session["difficulty"], session["evidence_shown"])
    messages = [{"role": "system", "content": system}]
    messages += session["history"][key]
    messages.append({"role": "user", "content": prompt})

    try:
        answer = ask_model(messages)
    except requests.exceptions.ConnectionError:
        return jsonify({"answer": "[Ollama isn't running. Start it, then try again.]", "flags": []})
    except Exception as e:
        return jsonify({"answer": f"[Model error: {e}]", "flags": []})

    history = session["history"]
    history[key].append({"role": "user", "content": prompt})
    history[key].append({"role": "assistant", "content": answer})
    session["history"] = history

    flags = detect_contradictions(session["case"], key, answer)
    notebook = session["notebook"]
    notebook.append({"suspect": key, "name": case["suspects"][key]["name"],
                     "q": f"[Presented: {ev['name']}]", "a": answer})
    session["notebook"] = notebook

    return jsonify({"answer": answer, "name": case["suspects"][key]["name"], "flags": flags})


@app.route("/notebook")
def notebook():
    ensure_game()
    return jsonify(session.get("notebook", []))


@app.route("/accuse", methods=["POST"])
def accuse():
    ensure_game()
    key = request.get_json(force=True).get("suspect")
    case = casedb.CASES[session["case"]]
    guilty = session["guilty"]
    correct = key == guilty
    session["solved"] = True
    return jsonify({
        "correct": correct,
        "guilty_name": case["suspects"][guilty]["name"],
        "accused_name": case["suspects"].get(key, {}).get("name", "?"),
        "guilty_secret": case["suspects"][guilty]["secret"],
    })


@app.route("/new-case", methods=["POST"])
def new_case():
    data = request.get_json(force=True) if request.data else {}
    case_key = data.get("case")
    difficulty = data.get("difficulty", "normal")
    if case_key not in casedb.CASES:
        case_key = None
    new_game(case_key, difficulty)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5005)

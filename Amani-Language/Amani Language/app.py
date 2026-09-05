"""
Amani Language — web app (build-out).

A language lab: build and save a corpus across sessions, load bundled starter
corpora (isiZulu / English), train bigram or trigram models, compare their fit,
generate with a temperature control, and export your corpus + model summary.
"""
import json
import re
from pathlib import Path

from flask import Flask, request, render_template, Response, jsonify

from model import NGramModel

app = Flask(__name__)
HERE = Path(__file__).parent
CORPORA = HERE / "corpora"
SAVED = HERE / "my_corpus.txt"          # the user's own saved corpus (persists)

# In-memory trained model for the session.
STATE = {"model": None, "stats": None, "n": 2, "corpus_len": 0}


def list_corpora():
    files = sorted(CORPORA.glob("*.txt")) if CORPORA.exists() else []
    return [f.stem for f in files]


def read_saved():
    return SAVED.read_text(encoding="utf-8") if SAVED.exists() else ""


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", state=STATE, output={},
                           error=None, corpora=list_corpora(),
                           saved=read_saved())


@app.route("/train", methods=["POST"])
def train():
    corpus = request.form.get("corpus", "").strip()
    n = int(request.form.get("n", 2))
    error, output = None, {}
    if not corpus:
        error = "Add some text to train on first."
    else:
        try:
            m = NGramModel(n=n)
            stats = m.train(corpus)
            STATE.update(model=m, stats=stats, n=n, corpus_len=len(corpus))
            output["trained"] = stats
        except ValueError as e:
            error = str(e)
    return render_template("index.html", state=STATE, output=output,
                           error=error, corpora=list_corpora(), saved=corpus)


@app.route("/load-corpus")
def load_corpus():
    """Return the text of a bundled corpus (for the 'Load starter' buttons)."""
    name = request.args.get("name", "")
    path = CORPORA / f"{name}.txt"
    if not path.exists() or path.parent != CORPORA:
        return jsonify({"error": "not found"}), 404
    return jsonify({"text": path.read_text(encoding="utf-8")})


@app.route("/save-corpus", methods=["POST"])
def save_corpus():
    text = request.get_json(force=True).get("text", "")
    SAVED.write_text(text, encoding="utf-8")
    return jsonify({"ok": True, "chars": len(text)})


@app.route("/generate", methods=["POST"])
def generate():
    if STATE["model"] is None:
        return jsonify({"error": "Train a model first."}), 400
    d = request.get_json(force=True)
    text = STATE["model"].generate(
        max_words=int(d.get("max_words", 40)),
        seed=(d.get("seed") or "").strip() or None,
        temperature=float(d.get("temperature", 1.0)),
    )
    return jsonify({"text": text})


@app.route("/predict", methods=["POST"])
def predict():
    if STATE["model"] is None:
        return jsonify({"error": "Train a model first."}), 400
    prompt = (request.get_json(force=True).get("prompt") or "").strip()
    preds = STATE["model"].predict(prompt, k=6)
    return jsonify({"predictions": [[w, round(p, 4)] for w, p in preds]})


@app.route("/perplexity", methods=["POST"])
def perplexity():
    if STATE["model"] is None:
        return jsonify({"error": "Train a model first."}), 400
    sample = (request.get_json(force=True).get("sample") or "").strip()
    return jsonify({"perplexity": STATE["model"].perplexity(sample)})


@app.route("/compare", methods=["POST"])
def compare():
    """Train bigram and trigram on the same corpus and compare perplexity on a
    held-out tail of the corpus itself — a quick, honest quality check."""
    corpus = request.get_json(force=True).get("corpus", "").strip()
    if not corpus:
        return jsonify({"error": "Add a corpus first."}), 400
    words = corpus.split()
    if len(words) < 20:
        return jsonify({"error": "Corpus too short to compare (add more text)."}), 400
    cut = int(len(words) * 0.85)
    train_text, test_text = " ".join(words[:cut]), " ".join(words[cut:])
    results = {}
    for n in (2, 3):
        try:
            m = NGramModel(n=n)
            m.train(train_text)
            results[f"{n}-gram"] = m.perplexity(test_text)
        except ValueError:
            results[f"{n}-gram"] = None
    return jsonify({"results": results})


@app.route("/export/corpus")
def export_corpus():
    text = read_saved() or (STATE.get("corpus_len") and "")
    return Response(
        read_saved(), mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=amani-corpus.txt"},
    )


@app.route("/export/model")
def export_model():
    """Export a JSON summary of the trained model (vocab + top continuations)."""
    if STATE["model"] is None:
        return jsonify({"error": "Train a model first."}), 400
    m = STATE["model"]
    top = {}
    for ctx, counter in list(m.counts.items())[:500]:
        key = " ".join(ctx)
        top[key] = counter.most_common(3)
    summary = {"n": m.n, "vocab_size": len(m.vocab),
               "contexts": len(m.counts), "sample_transitions": top}
    return Response(
        json.dumps(summary, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=amani-model.json"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5004)

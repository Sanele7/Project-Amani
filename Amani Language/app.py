"""
Amani Language — train an n-gram language model on any text, then generate,
predict, and score it. The trained model is held in memory for the session.
"""
from flask import Flask, request, render_template

from model import NGramModel

app = Flask(__name__)

# Simple in-memory store: last trained model + stats.
STATE = {"model": None, "stats": None, "n": 2}

SAMPLE = ("Sawubona. Unjani namuhla? Ngiyaphila ngiyabonga. "
          "Sawubona mngane. Unjani wena? Ngikhona ngiyabonga. "
          "Ngicela usizo. Yebo ngingakusiza. Ngiyabonga kakhulu. "
          "Uphi umama? Umama usekhaya. Ubaba usemsebenzini.")


@app.route("/", methods=["GET", "POST"])
def index():
    output = {}
    error = None
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "train":
                n = int(request.form.get("n", 2))
                corpus = request.form.get("corpus", "").strip()
                if not corpus:
                    error = "Paste some text to train on first."
                else:
                    model = NGramModel(n=n)
                    stats = model.train(corpus)
                    STATE.update(model=model, stats=stats, n=n)
                    output["trained"] = stats
            elif STATE["model"] is None:
                error = "Train a model first."
            elif action == "generate":
                seed = request.form.get("seed", "").strip()
                output["generated"] = STATE["model"].generate(max_words=40, seed=seed or None)
            elif action == "predict":
                prompt = request.form.get("prompt", "").strip()
                output["predictions"] = STATE["model"].predict(prompt, k=6)
                output["prompt"] = prompt
            elif action == "perplexity":
                sample = request.form.get("sample", "").strip()
                output["perplexity"] = STATE["model"].perplexity(sample)
        except ValueError as e:
            error = str(e)

    return render_template("index.html", state=STATE, output=output, error=error, sample=SAMPLE)


if __name__ == "__main__":
    app.run(debug=True, port=5004)

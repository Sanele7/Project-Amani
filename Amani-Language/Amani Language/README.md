# Amani Language

A language model for the languages big AI ignores — isiZulu, Sesotho, Xitsonga
and others. Build a corpus, train a real statistical model on it, then generate
text, predict words, and measure how well it learned. Comes with an isiZulu
starter corpus so it works the moment you open it.

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5004

## What works now
- Load a bundled starter corpus (isiZulu or English), or paste your own text.
- Save your corpus so it persists between sessions; export it as a .txt file
  (the corpus itself is a citable contribution).
- Train a bigram or trigram model instantly.
- Compare bigram vs trigram quality (perplexity on held-out text).
- Generate text with a creativity (temperature) control.
- Next-word prediction with probabilities; perplexity scoring.
- Export the trained model as JSON.

## What's next (build-out)
- Grow the isiZulu corpus (public-domain text, news, folktales) — the biggest
  lever on quality and the clearest route to recognition.
- Swap the n-gram core for a small neural model (char-RNN, then a tiny
  transformer) trained free on Kaggle's weekly GPU hours.
- Add speech-to-text, which is even more underserved for these languages.

## Corpora
Drop more `.txt` files into the `corpora/` folder and they appear as
"Load" buttons automatically.

Secured by Impunga Yehlathi Technologies.

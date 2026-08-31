# Amani Language

A language model for low-resource languages — the ones big AI ignores (isiZulu,
Sesotho, Xitsonga, Yoruba...). Paste a text corpus in any language and it trains
a real statistical language model that generates new text, predicts the next
word, and scores how well it learned the language (perplexity).

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5004

## What works now
- Trains an n-gram model (bigram/trigram) instantly on whatever text you give it.
- Generate text in the style of your corpus.
- Next-word prediction with probabilities.
- Perplexity score — a genuine measure of the model's fit.
This is the real statistical foundation of every language model.

## What's next (build-out)
- Swap the n-gram core for a small neural model (character RNN, then a tiny
  transformer) trained free on Kaggle's weekly GPU hours.
- Build and publish a cleaned corpus for one language — the corpus itself is a
  citable contribution and the fastest route to recognition here.
- Add speech-to-text (even more underserved than text for these languages).

Secured by Impunga Yehlathi Technologies.

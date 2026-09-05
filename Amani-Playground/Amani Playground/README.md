# Amani Playground

A murder-mystery interrogation game where the suspects are AI characters with
hidden knowledge and a motive to deceive. One is guilty and lies; because the
lies are generated live, you can catch real contradictions. Every playthrough
is different.

## Needs a free local AI (Ollama)
1. Install Ollama: https://ollama.com
2. Pull a model:  `ollama pull llama3.2`  (keep Ollama running)
   Different model?  set OLLAMA_MODEL=name

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5005

## What works now
- Two full cases (Observatory murder, Gallery heist) — pick one, or a new random guilty each game.
- Three suspects per case, each with a persona, alibi, and secret.
- Difficulty (easy/normal/hard) controls how well the guilty suspect lies.
- Evidence system: present a clue to a suspect and watch them react — the guilty
  one scrambles to explain it away.
- Detective's notebook: records every answer and auto-flags likely contradictions.
- Accuse to see if you were right, and the culprit's hidden motive.

## What's next (build-out)
- More cases and a case-of-the-day.
- Smarter contradiction detection (compare specific alibi facts, not just keywords).
- Present evidence between two suspects to force them to contradict each other.
- Optional voice: read suspect replies aloud.

Secured by Impunga Yehlathi Technologies.

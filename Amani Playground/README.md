# Amani Playground

A murder-mystery interrogation game where the suspects are LLM characters with
hidden knowledge and a motive to deceive. You question them in free text; one is
guilty and actively lies. Because the lies are generated, not scripted, you can
catch real contradictions — and every playthrough is different.

## Needs a free local AI (Ollama)
The suspects are driven by a language model running on your own machine — free,
private, no API key.

1. Install Ollama from https://ollama.com (Windows installer).
2. In a terminal, pull a small model:  `ollama pull llama3.2`
   (Leave Ollama running — it serves on http://localhost:11434.)

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5005

If a suspect replies with a setup message, Ollama isn't running yet — start it
and pull the model above. To use a different model:  set OLLAMA_MODEL=name.

## What works now
- Three suspects, each with a private persona, alibi, and secret.
- One is randomly guilty and is instructed to lie and deflect; the innocent ones
  tell the truth but have their own evasive secrets (red herrings).
- Per-suspect memory, so their story stays consistent — and can be caught out.
- Make an accusation to see if you were right.

## What's next (build-out)
- A notebook that auto-flags contradictions between suspects' statements.
- More cases, more suspects, evidence items you can present mid-interrogation.
- Difficulty levels (how cleverly the guilty one lies).

Secured by Impunga Yehlathi Technologies.

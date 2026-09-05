# Amani

**Seven projects across cybersecurity, AI, data science, and games — one brand, one interface.**
*Secured by Impunga Yehlathi Technologies.*

Amani (isiZulu/Swahili for *peace*) is a portfolio of working tools built around a
simple idea: technology that protects people and serves communities that mainstream
software overlooks. Every project runs locally, is free to run, and shares the same
neon interface.

Open **`index.html`** for the portfolio home page linking to all seven.

---

## The projects

### Cybersecurity
- **Amani Test** — a web application vulnerability scanner. Crawls a target, proves
  real OWASP issues (reflected XSS, missing security headers), and produces a
  consultant-grade report. Scoped to authorised targets only, with a login system
  built to the same standard it audits. *Flask · port 5000*
- **Amani Audit** — a mobile app security auditor. Unpacks an Android APK and reports
  hardcoded secrets, risky manifest settings, dangerous permissions, and third-party
  trackers, rolled into a 0–100 risk score. *Flask · port 5003*

### Artificial Intelligence
- **Amani Language** — a language model for low-resource languages like isiZulu.
  Build and save a corpus, train a bigram/trigram model, then generate text, predict
  words, and measure quality. Ships with an isiZulu starter corpus. *Flask · port 5004*
- **Amani Sign** — real-time hand-sign recognition from a webcam that you can *teach*
  your own signs, built toward South African Sign Language. Runs in the browser, no
  install. *Open the HTML file*

### Data Science
- **Amani Grid** — a community service-outage map. Report power/water/internet
  outages, confirm and resolve them, and export the open dataset as CSV/GeoJSON.
  *Flask · port 5001*
- **Amani Satellite Detection** — change detection between two satellite images of
  the same place, highlighting new construction, cleared land, or flooding.
  *Flask · port 5002*

### Game
- **Amani Playground** — a murder-mystery interrogation game where the suspects are
  AI characters who genuinely lie. Present evidence, catch contradictions in a
  detective's notebook, and name the killer. Runs on a free local AI (Ollama).
  *Flask · port 5005*

---

## Running a project

Each project is self-contained in its own folder with its own `requirements.txt`.
For any Flask project (example: Amani Grid):

```bash
cd "Amani Grid"
python -m venv venv           # first time only
venv\Scripts\activate.bat     # Windows (use: source venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
python app.py
```

Then open the port listed above (e.g. http://localhost:5001).

- **Amani Sign** needs no server — open `Amani Sign/amani-sign.html` in Chrome or Edge.
- **Amani Playground** needs [Ollama](https://ollama.com): install it, run
  `ollama pull llama3.2`, and keep it running.

---

## Tech

Python · Flask · SQLite · vanilla JavaScript · Leaflet · MediaPipe · Ollama.
No paid services required.

## Author

Built by **Sanele Ngcobo** — BSc Honours, Computer Science, University of Zululand.

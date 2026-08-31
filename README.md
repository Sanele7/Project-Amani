# Amani — Projects 2–7

Six projects, one brand, one neon interface — the siblings of Amani Test.
Every project is self-contained in its own folder and runs on its own port, so
you can run several at once. Open **index.html** in a browser for the portfolio
landing page that ties all seven together.

| Project | Folder | What it does | How to run |
|---|---|---|---|
| Amani Audit | `Amani Audit` | Scan an APK for hardcoded secrets | Flask · port 5003 |
| Amani Language | `Amani Language` | Train a language model on any text | Flask · port 5004 |
| Amani Sign | `Amani Sign` | Live webcam sign recognition | Open the HTML file |
| Amani Grid | `Amani Grid` | Community service-outage map | Flask · port 5001 |
| Amani Satellite Detection | `Amani Satellite Detection` | Image change detection | Flask · port 5002 |
| Amani Playground | `Amani Playground` | LLM interrogation mystery game | Flask · port 5005 (needs Ollama) |

## Where to put this
Extract this folder into:
`C:\Users\Sanele Ngcobo\OneDrive\Documents\Project_Amani\`
so these sit right next to your `Amani Test` folder.

## Running any Flask project (same five steps as Amani Test)
Open Command Prompt and, for example, for Amani Grid:

    cd "C:\Users\Sanele Ngcobo\OneDrive\Documents\Project_Amani\Amani Grid"
    python -m venv venv
    venv\Scripts\activate.bat
    pip install -r requirements.txt
    python app.py

Then open the port shown above (e.g. http://localhost:5001). Each project has
its own `venv` and its own `requirements.txt`. Press Ctrl+C to stop.

## Amani Sign — no install
Just double-click **Amani Sign\amani-sign.html** to open it in Chrome or Edge and
allow the camera. (Needs internet the first time to load the tracking model.)

## Amani Playground — needs a free local AI
Install Ollama from https://ollama.com, then run `ollama pull llama3.2` and keep
Ollama open. See that project's README for details.

## Honest status
These are working **foundations**, not finished products. Each one does something
real today and each has a "What's next" section in its own README showing the
build-out that takes it to Amani Test's depth. Build them out one at a time — a
few finished, polished projects beat seven half-built ones.

Secured by Impunga Yehlathi Technologies.

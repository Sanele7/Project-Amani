# Amani Sign

Real-time hand-sign recognition from a normal webcam — and now you can *teach* it
your own signs. It tracks 21 points on your hand, and a classifier you train in
the browser learns to recognise whatever shapes you show it, including the letters
of a fingerspelling alphabet. Built toward sign languages with almost no
technology, like South African Sign Language.

## Run
No install, no server. Open **amani-sign.html** in Chrome or Edge and allow the
camera. (Needs internet the first time to load the hand-tracking model.)

## How to use it
1. Click **Start camera**.
2. Hold a hand shape, type a label (e.g. `A`), and press **capture** — it grabs
   30 samples while you hold steady.
3. Repeat for more signs (`B`, `Hello`, etc.).
4. Just show a sign — it tells you which one, with a confidence score.
5. **Save** stores your training in the browser; **Load** brings it back.

## What works now
- Live webcam hand tracking with the skeleton drawn on screen.
- Teach unlimited custom signs by example (no coding).
- A k-nearest-neighbour classifier over translation- and scale-invariant hand
  features, so it works wherever your hand is on screen.
- Save / load your trained model; the samples you record are your own dataset.

## What's next (build-out)
- Recognise motion (dynamic signs), not just static hand shapes.
- Export your recorded samples as a dataset file to share/cite.
- Spell words by holding letters in sequence, and read them aloud.
- Swap the KNN for a small neural net once you have lots of samples.

Secured by Impunga Yehlathi Technologies.

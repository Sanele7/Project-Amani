# Amani Sign

Real-time hand-sign recognition from a normal laptop webcam. It tracks 21 points
on your hand and reads the gesture live — built toward sign languages that have
almost no technology, like South African Sign Language.

## Run
No install, no server. Just open **amani-sign.html** in Chrome or Edge, and allow
camera access when asked. (It needs internet the first time to load the hand-
tracking model, and a webcam.)

## What works now
- Live webcam hand tracking (Google MediaPipe) with the skeleton drawn on screen.
- Recognises several gestures by hand geometry: fist, open palm, pointing,
  peace/V, thumbs up, and a live extended-finger count.

## What's next (build-out)
- Record your own labelled clips and train a small classifier so it learns the
  full fingerspelling alphabet (this is where it becomes a real SASL tool, and
  the clips you record are your own dataset — a citable contribution).
- Recognise motion (dynamic signs), not just static hand shapes.
- Caption full sentences and read them aloud.

Secured by Impunga Yehlathi Technologies.

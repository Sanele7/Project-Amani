# Amani Satellite Detection

Change detection between two images of the same place at different times. Upload
a "before" and an "after" image and it highlights what changed — new buildings,
cleared land, flooding, coastline shift — as a red heatmap, with a % changed.

Works with any before/after pair. For real satellite work, grab free Sentinel-2
images (same tile, two dates) from the Copernicus Browser or Google Earth Engine.

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5002

## What works now
- Upload two images; they're aligned to the same size.
- Per-pixel difference, blurred and thresholded, drawn as a red overlay.
- Percentage of the scene that changed.

## What's next (build-out)
- Pull Sentinel-2 tiles by coordinates + date automatically.
- Proper co-registration (align images that aren't already matched).
- Classify *type* of change (vegetation loss vs new construction) via NDVI/bands.
- Time series across many dates → a change-over-time chart.

Note: analyse imagery you have the rights to use. Sentinel-2 (Copernicus) is free
and openly licensed.

Secured by Impunga Yehlathi Technologies.

# Amani Grid

Community service-outage map with a real, exportable open dataset. People report
power / water / internet / gas / transport outages; the community confirms them
(so duplicates gain weight, not clutter) and marks them resolved when service
returns. Everything is filterable, summarised live, and downloadable — the
dataset is the point.

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5001

Want the map lively on first open? Load demo data first (app not running):
    python seed.py

## What works now
- Report an outage by clicking the map (service type + note).
- Outage lifecycle: active → confirmed (upvotes) → resolved.
- Filters: active only, last 24h, last 7 days, all.
- Live stats: active/resolved counts, breakdown by service, a 7-day trend
  sparkline, and the busiest active cluster.
- Heatmap toggle for outage density.
- One-click open-data export: **CSV** and **GeoJSON**.

## What's next (build-out)
- Seed automatically from official feeds (e.g. EskomSePush has a free API tier
  for load-shedding; municipal water notices).
- Reverse-geocode clusters to real place names (free OSM Nominatim).
- Accounts + moderation so bad reports can be flagged (reuse Amani Test's auth).
- A public read-only dataset page others can cite — the recognisable asset.

Secured by Impunga Yehlathi Technologies.

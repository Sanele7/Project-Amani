"""
Amani Satellite Detection — change detection between two images.

Given a 'before' and 'after' image of the same area, it computes where the
scene changed and returns a red heatmap overlay plus a percentage. Pure
Pillow + NumPy, no paid services.
"""
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from flask import Flask, request, render_template

app = Flask(__name__)


def to_gray_array(file_storage, size):
    img = Image.open(file_storage).convert("L").resize(size)
    return np.asarray(img, dtype=np.float32)


def detect_change(before_fs, after_fs):
    """Return (overlay_png_b64, percent_changed)."""
    size = (512, 512)
    before = Image.open(before_fs).convert("RGB").resize(size)
    after_fs.seek(0)
    after = Image.open(after_fs).convert("RGB").resize(size)

    # Difference on grayscale, smoothed to suppress noise.
    b_gray = np.asarray(before.convert("L"), dtype=np.float32)
    a_gray = np.asarray(after.convert("L"), dtype=np.float32)
    diff = np.abs(a_gray - b_gray)
    diff_img = Image.fromarray(diff.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    diff = np.asarray(diff_img, dtype=np.float32)

    # Threshold: changed where difference exceeds an adaptive cutoff.
    cutoff = max(30.0, diff.mean() + 2 * diff.std())
    mask = diff > cutoff
    percent = 100.0 * mask.sum() / mask.size

    # Build a red overlay on top of the 'after' image.
    overlay = np.asarray(after, dtype=np.float32).copy()
    overlay[mask] = 0.4 * overlay[mask] + 0.6 * np.array([255, 40, 90])
    out = Image.fromarray(overlay.astype(np.uint8))

    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode(), round(percent, 2)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        before = request.files.get("before")
        after = request.files.get("after")
        if not before or not after or before.filename == "" or after.filename == "":
            error = "Please choose both a before and an after image."
        else:
            try:
                img_b64, percent = detect_change(before, after)
                result = {"image": img_b64, "percent": percent}
            except Exception as e:
                error = f"Could not process the images: {e}"
    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5002)

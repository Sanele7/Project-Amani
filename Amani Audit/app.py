"""
Amani Audit — web app (build-out).

Upload an APK; it runs the analyzer and renders a severity-rated report with a
risk score. Only analyse apps you own or are authorised to test.
"""
from flask import Flask, request, render_template

from analyzer import scan_apk

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB APKs


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        apk = request.files.get("apk")
        if not apk or apk.filename == "":
            error = "Please choose an APK file to scan."
        else:
            result, error = scan_apk(apk.read())
    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5003)

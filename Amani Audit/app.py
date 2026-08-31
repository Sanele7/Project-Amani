"""
Amani Audit — static security scan of an Android APK.

An APK is just a ZIP archive. This unpacks it in memory and scans every file
for hardcoded secrets, embedded URLs, and requested permissions. No paid tools.

Only scan apps you own or are authorised to test.
"""
import re
import zipfile
import io

from flask import Flask, request, render_template

app = Flask(__name__)

# name -> (compiled regex, severity)  — common secret shapes.
SECRET_PATTERNS = {
    "Google API key":     (re.compile(rb"AIza[0-9A-Za-z\-_]{35}"), "High"),
    "AWS access key":     (re.compile(rb"AKIA[0-9A-Z]{16}"), "High"),
    "Stripe secret key":  (re.compile(rb"sk_live_[0-9A-Za-z]{24}"), "High"),
    "Slack token":        (re.compile(rb"xox[baprs]-[0-9A-Za-z\-]{10,48}"), "High"),
    "Private key block":  (re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "High"),
    "JSON Web Token":     (re.compile(rb"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "Medium"),
    "Generic api_key=":   (re.compile(rb"(?i)(api[_-]?key|secret|passwd|password)\s*[=:]\s*['\"][^'\"]{6,}['\"]"), "Medium"),
}
URL_PATTERN = re.compile(rb"https?://[A-Za-z0-9\.\-_/:%?=&#]{6,}")
# Android permission strings appear as plain text inside the (binary) manifest.
PERM_PATTERN = re.compile(rb"android\.permission\.[A-Z_]+")

DANGEROUS_PERMS = {
    "android.permission.READ_SMS", "android.permission.SEND_SMS",
    "android.permission.READ_CONTACTS", "android.permission.RECORD_AUDIO",
    "android.permission.ACCESS_FINE_LOCATION", "android.permission.READ_CALL_LOG",
    "android.permission.CAMERA", "android.permission.READ_EXTERNAL_STORAGE",
}


def scan_apk(file_bytes):
    findings = []
    urls = set()
    perms = set()

    try:
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
    except zipfile.BadZipFile:
        return None, "That file isn't a valid APK/ZIP archive."

    for name in zf.namelist():
        try:
            data = zf.read(name)
        except Exception:
            continue

        for label, (pattern, severity) in SECRET_PATTERNS.items():
            for match in set(pattern.findall(data)):
                snippet = match.decode("utf-8", "replace")[:60]
                findings.append({
                    "name": f"Hardcoded secret: {label}",
                    "severity": severity,
                    "location": name,
                    "evidence": f"Matched: {snippet}",
                    "remediation": "Never ship secrets in the app. Move them server-side "
                                   "and rotate this key — assume it is compromised.",
                })

        for u in URL_PATTERN.findall(data):
            urls.add(u.decode("utf-8", "replace")[:120])
        for p in PERM_PATTERN.findall(data):
            perms.add(p.decode("utf-8", "replace"))

    # Flag notably sensitive permissions.
    for p in sorted(perms & DANGEROUS_PERMS):
        findings.append({
            "name": f"Sensitive permission requested: {p.split('.')[-1]}",
            "severity": "Low",
            "location": "AndroidManifest",
            "evidence": p,
            "remediation": "Confirm the app genuinely needs this permission; remove if not.",
        })

    summary = {
        "files": len(zf.namelist()),
        "urls": sorted(urls)[:40],
        "perms": sorted(perms),
        "secret_count": sum(1 for f in findings if f["name"].startswith("Hardcoded")),
    }
    order = {"High": 0, "Medium": 1, "Low": 2}
    findings.sort(key=lambda f: order.get(f["severity"], 9))
    return {"findings": findings, "summary": summary}, None


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

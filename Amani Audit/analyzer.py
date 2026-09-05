"""
Amani Audit — static APK security analysis (build-out).

An APK is a ZIP. This unpacks it in memory and runs several passes:
  - hardcoded secrets (API keys, tokens, private keys)
  - risky manifest settings (debuggable, allowBackup, cleartext traffic)
  - dangerous permissions
  - known third-party trackers/SDKs
Findings are severity-rated and rolled into a single risk score, then rendered
as a consultant-grade report — the mobile sibling of Amani Test.

Only analyse apps you own or are authorised to test.
"""
import re
import io
import zipfile

SECRET_PATTERNS = {
    "Google API key":    (re.compile(rb"AIza[0-9A-Za-z\-_]{35}"), "High"),
    "AWS access key":    (re.compile(rb"AKIA[0-9A-Z]{16}"), "High"),
    "Stripe secret key": (re.compile(rb"sk_live_[0-9A-Za-z]{24}"), "High"),
    "Slack token":       (re.compile(rb"xox[baprs]-[0-9A-Za-z\-]{10,48}"), "High"),
    "Google OAuth ID":   (re.compile(rb"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com"), "Medium"),
    "Firebase URL":      (re.compile(rb"[a-z0-9\-]+\.firebaseio\.com"), "Medium"),
    "Private key block": (re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "High"),
    "JSON Web Token":    (re.compile(rb"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "Medium"),
    "Generic secret =":  (re.compile(rb"(?i)(api[_-]?key|secret|passwd|password|token)\s*[=:]\s*['\"][^'\"]{6,}['\"]"), "Medium"),
}

URL_PATTERN  = re.compile(rb"https?://[A-Za-z0-9\.\-_/:%?=&#]{6,}")
PERM_PATTERN = re.compile(rb"android\.permission\.[A-Z_]+")

DANGEROUS_PERMS = {
    "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "READ_CONTACTS", "WRITE_CONTACTS",
    "RECORD_AUDIO", "CAMERA", "ACCESS_FINE_LOCATION", "ACCESS_BACKGROUND_LOCATION",
    "READ_CALL_LOG", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE",
    "READ_PHONE_STATE", "SYSTEM_ALERT_WINDOW", "REQUEST_INSTALL_PACKAGES",
}

# Known trackers/SDKs by a path fragment that appears in the APK.
TRACKERS = {
    "com/google/firebase/analytics": "Firebase Analytics",
    "com/facebook": "Facebook SDK",
    "com/google/android/gms/ads": "Google AdMob",
    "com/flurry": "Flurry Analytics",
    "com/appsflyer": "AppsFlyer",
    "io/branch": "Branch",
    "com/mixpanel": "Mixpanel",
}

SEVERITY_WEIGHT = {"High": 10, "Medium": 4, "Low": 1}
SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def _manifest_findings(manifest_bytes):
    """Heuristic manifest checks. The manifest is binary (AXML), but these
    setting names appear as readable UTF-16/ASCII fragments, so we scan bytes."""
    findings = []
    m = manifest_bytes

    def present(token):
        return token.encode("utf-8") in m or token.encode("utf-16-le") in m

    if present("debuggable"):
        findings.append(("App is debuggable", "High", "AndroidManifest",
                         "The 'debuggable' flag appears set.",
                         "Never ship a debuggable build — it lets anyone inspect and manipulate the app."))
    if present("usesCleartextTraffic") or present("cleartextTrafficPermitted"):
        findings.append(("Cleartext (HTTP) traffic allowed", "Medium", "AndroidManifest",
                         "Cleartext traffic appears permitted.",
                         "Disable cleartext traffic; require HTTPS to protect data in transit."))
    if present("allowBackup"):
        findings.append(("Backup allowed", "Low", "AndroidManifest",
                         "'allowBackup' appears enabled.",
                         "Set android:allowBackup=false if the app holds sensitive data."))
    return findings


def scan_apk(file_bytes):
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
    except zipfile.BadZipFile:
        return None, "That file isn't a valid APK/ZIP archive."

    findings = []
    urls, perms, trackers = set(), set(), set()
    names = zf.namelist()

    for name in names:
        try:
            data = zf.read(name)
        except Exception:
            continue

        if name == "AndroidManifest.xml":
            for t in _manifest_findings(data):
                findings.append({"name": t[0], "severity": t[1], "location": t[2],
                                 "evidence": t[3], "remediation": t[4]})

        for label, (pattern, severity) in SECRET_PATTERNS.items():
            for match in set(pattern.findall(data)):
                findings.append({
                    "name": f"Hardcoded secret: {label}", "severity": severity, "location": name,
                    "evidence": f"Matched: {match.decode('utf-8','replace')[:60]}",
                    "remediation": "Move secrets server-side and rotate this key — assume it is compromised.",
                })

        for u in URL_PATTERN.findall(data):
            urls.add(u.decode("utf-8", "replace")[:120])
        for p in PERM_PATTERN.findall(data):
            perms.add(p.decode("utf-8", "replace").split(".")[-1])

    # Trackers from the file listing
    joined = "\n".join(names)
    for frag, label in TRACKERS.items():
        if frag in joined:
            trackers.add(label)

    for p in sorted(perms & DANGEROUS_PERMS):
        findings.append({
            "name": f"Sensitive permission: {p}", "severity": "Low", "location": "AndroidManifest",
            "evidence": f"android.permission.{p}",
            "remediation": "Confirm the app genuinely needs this permission; remove if not.",
        })
    for t in sorted(trackers):
        findings.append({
            "name": f"Third-party tracker/SDK: {t}", "severity": "Low", "location": "bundled libraries",
            "evidence": f"{t} appears bundled in the app.",
            "remediation": "Disclose data sharing in your privacy policy; remove trackers you don't need.",
        })

    findings.sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))

    # Risk score 0-100 from weighted findings.
    raw = sum(SEVERITY_WEIGHT.get(f["severity"], 0) for f in findings)
    score = min(100, raw)
    grade = ("Critical" if score >= 40 else "High" if score >= 20 else
             "Moderate" if score >= 8 else "Low")

    summary = {
        "files": len(names),
        "urls": sorted(urls)[:40],
        "perms": sorted(perms),
        "trackers": sorted(trackers),
        "counts": {sev: sum(1 for f in findings if f["severity"] == sev) for sev in ("High", "Medium", "Low")},
        "score": score, "grade": grade,
    }
    return {"findings": findings, "summary": summary}, None

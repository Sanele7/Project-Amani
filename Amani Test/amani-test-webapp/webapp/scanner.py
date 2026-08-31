"""
Compact scanner used by the dashboard.

It reuses the same principles as the Amani Test CLI: it refuses any target
not on the authorized list, then runs quick checks (security headers +
reflected XSS) and returns findings. The fuller context-aware engine plugs
in right here when you're ready.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathlib import Path

AUTHORIZED_FILE = Path(__file__).parent / "authorized_targets.txt"

SECURITY_HEADERS = {
    "Content-Security-Policy": "Reduces XSS risk by controlling what can load.",
    "X-Frame-Options": "Prevents clickjacking via framing.",
    "X-Content-Type-Options": "Stops MIME-sniffing.",
    "Strict-Transport-Security": "Forces HTTPS.",
}
MARKER = "amaniXSS7391"
PAYLOAD = f"<script>{MARKER}</script>"


def is_authorized(url):
    host = urlparse(url).hostname
    if not host:
        return False
    if not AUTHORIZED_FILE.exists():
        return False
    allowed = set()
    for line in AUTHORIZED_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            allowed.add(line.lower())
    return host.lower() in allowed


def scan(url):
    """Return (findings, error). findings is a list of dicts."""
    if not is_authorized(url):
        return None, ("Target is not authorized. Add its host to "
                      "authorized_targets.txt only if you own it or have written permission.")

    findings = []
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        return None, f"Could not reach target: {e}"

    # Security headers
    present = {k.lower() for k in resp.headers}
    for header, why in SECURITY_HEADERS.items():
        if header.lower() not in present:
            findings.append({
                "name": f"Missing security header: {header}",
                "severity": "Medium",
                "location": url,
                "evidence": f"Response did not include '{header}'.",
                "remediation": f"Send the '{header}' header. {why}",
            })

    # Reflected XSS on discovered forms
    soup = BeautifulSoup(resp.text, "html.parser")
    for form in soup.find_all("form"):
        action = urljoin(url, form.get("action", ""))
        method = form.get("method", "get").lower()
        names = [t.get("name") for t in form.find_all(["input", "textarea"]) if t.get("name")]
        if not names:
            continue
        data = {n: PAYLOAD for n in names}
        try:
            r = (requests.post(action, data=data, timeout=10) if method == "post"
                 else requests.get(action, params=data, timeout=10))
        except requests.RequestException:
            continue
        if PAYLOAD in r.text:
            findings.append({
                "name": "Reflected Cross-Site Scripting (XSS)",
                "severity": "High",
                "location": action,
                "evidence": "Injected payload was reflected unescaped.",
                "remediation": "Encode user input on output; apply a Content-Security-Policy.",
            })

    return findings, None

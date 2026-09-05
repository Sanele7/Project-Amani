# Amani Audit

Mobile app security auditor — the mobile sibling of Amani Test. Upload an Android
APK and it produces a severity-rated report with a risk score: hardcoded secrets,
risky manifest settings, dangerous permissions, and bundled third-party trackers.

## The one rule (same as Amani Test)
Only analyse apps you own, apps you build, or apps you are explicitly authorised
to test. Report findings responsibly to the vendor; never publish extracted secrets.

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5003

## What works now
- Unpacks the APK (a ZIP) and scans every file.
- Secret detectors: Google/AWS/Stripe/Slack keys, OAuth IDs, Firebase URLs,
  private keys, JWTs, and generic key/secret/token assignments.
- Manifest checks: debuggable build, cleartext (HTTP) traffic, allowBackup.
- Dangerous-permission flagging and third-party tracker/SDK detection.
- A 0-100 risk score with a grade, findings grouped by severity, plus the list
  of embedded URLs.

## What's next (build-out)
- Decompile DEX to Java with jadx for readable, line-referenced findings.
- Fully parse the binary AndroidManifest (androguard) for exported components
  and the exact target SDK.
- Certificate/signature inspection and a downloadable PDF report.

Secured by Impunga Yehlathi Technologies.

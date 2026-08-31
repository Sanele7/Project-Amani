# Amani Audit

Mobile app security auditor. Upload an Android APK and it statically scans the
package for hardcoded secrets (API keys, tokens, private keys), embedded URLs,
and the permissions the app requests — the most common ways mobile apps leak
data. The web counterpart to Amani Test.

## The one rule (same as Amani Test)
Only analyse apps you own, apps you build, or apps you are explicitly authorised
to test. Report findings responsibly to the vendor; never publish extracted
secrets.

## Run
    pip install -r requirements.txt
    python app.py
Open http://localhost:5003

## What works now
- An APK is a ZIP — it's unpacked in memory and every file is scanned.
- Regex detectors for common secret formats (Google/AWS/Stripe keys, JWTs,
  private keys, generic api_key=... assignments).
- Extracts embedded http(s) URLs and lists requested permissions.
- Severity-rated findings in the shared Amani report style.

## What's next (build-out)
- Decompile DEX to Java with jadx for readable, line-referenced findings.
- Parse the binary AndroidManifest properly (androguard) for exported
  components, debuggable flag, backup flag.
- Certificate/signature checks and cleartext-traffic config detection.
- Runtime testing against an emulator (MobSF-style dynamic analysis).

Secured by Impunga Yehlathi Technologies.

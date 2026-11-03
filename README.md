# beit-shemesh-moked

Reporting to the Beit Shemesh municipal hotline (מוקד 106) through the API used by the
official resident app "עיריית בית שמש" (`binaaltd.beitshemesh`, vendor E.S. Bina).

Companion to `parking-reports` (Jerusalem 106). Goal: let a Beit Shemesh resident
(Meir) file hazard reports through the same reporting service.

- `docs/design.md` — API findings and pipeline design (read first)
- `reference/app/` — decompilation notes for the resident app
- `tools/bsmoked_client.py` — stdlib-only client (filing is guarded, see design doc)
- `tests/` — synthetic-fixture tests, no network

Rules (same as Jerusalem): no real report is filed without the user's explicit
approval, no borrowed identities, no CAPTCHA/block bypass. The app-embedded shared
secret is public (inside the Play-Store APK, like Jerusalem's subscription key) but
this repo stays private.

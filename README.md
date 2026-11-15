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

## Credential configuration

Set `BSMOKED_SECRET` in the execution environment using the existing secret store,
or pass an explicit `secret=` argument. No shared credential is embedded in the
source. Missing or blank configuration fails before any request. Credentials
are resolved at call time, so changing the environment does not require a module
reload. Never paste credentials into docs, logs or issues.

The two live-filing gates are unchanged. Offline tests use synthetic credentials
and block network requests. Removing a value from current files does not remove
it from Git history or revoke the municipal application's shared credential.

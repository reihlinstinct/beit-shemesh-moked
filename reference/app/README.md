# Beit Shemesh resident app reference (private)

Package `binaaltd.beitshemesh`, "עיריית בית שמש", version 1.6 (code 23), min SDK 21,
native Android (Java/Kotlin, obfuscated with r8 — helper classes under `o/`).
Vendor: E.S. Bina (binaa.co.il), the municipality's CRM supplier. The vendor's
field-team app is `esbinaltd.moked` ("מוקד א.ש בינה") — not the resident app.

APK obtained 2026-11-03 with `apkeep -a binaaltd.beitshemesh -d apk-pure`
(~7.7 MB, single APK, no split). Decompiled with jadx 1.5.0 (19 minor errors,
all unrelated to the networking code).

Key classes (decompiled names):
- `binaaltd.beitshemesh.MokedActivity` — "דיווח למוקד" screen; base URL
  `https://bshemesh.moked-binaa.co.il/api/`; image upload helper `g()`.
- `o/lv0.java` (AsyncTask, mode 1) — report submission: uploads up to 4 images,
  then GET `insert_call.php` with the full param set; parses `{status, number,
  user_hash}`; stores `user_hash` as SharedPreferences `moked_hash`.
- `o/v10.java` (AsyncTask) — mode 5: `get_streets.php`; modes 3/4: legacy
  `add_report.php` / `get_reportsByUser.php` on `betshemesh.muni.il/app/`.
- `binaaltd.beitshemesh.MokedUserActivity` + `o/mv0.java` — reporter details form
  (fname/lname/phone/home/street/email), stored locally; no ID number, no OTP.
- `binaaltd.beitshemesh.UserareaActivity` + `o/cr1.java` — personal-area login:
  `profile.php?cellphone=` sends an SMS OTP; `profile.php?cellphone=&secret=<otp>`
  returns `{user:{hash,first_name,last_name}}`; then a webview opens
  `betshemesh.muni.il/moked-profile/?app=1&cellphone=...&hash=...`.
- `binaaltd.beitshemesh.StreetActivity` + `o/v10.java` mode 5 — street picker.
- `binaaltd.beitshemesh.ReportActivity`/`Report2Activity` — legacy hazard form
  ("כתובת האירוע"/"תיאור המקרה", GPS from EXIF) using `add_report.php`.
- Embedded Google geocode key `AIzaSy...aGI` used for reverse-geocoding the
  event location (app-side only).

The app contains the shared API secret (see docs/design.md). Keep this repo private.
Our filing credentials (when approved) stay in Actions secrets / the vault, never in files.

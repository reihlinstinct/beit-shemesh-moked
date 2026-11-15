# Beit Shemesh moked reporting API — findings and design

Status: research complete 2026-11-03. No report was ever filed; only read-only
GET probes (street list) were run. Filing requires separate user approval.

## Source

Decompiled resident app `binaaltd.beitshemesh` v1.6 (code 23) — see
`reference/app/README.md`. Two reporting stacks coexist in the app; we use the
modern one (Bina CRM). The legacy one is documented for completeness only.

## Modern stack (Bina CRM) — the one to use

Base URL: `https://bshemesh.moked-binaa.co.il/api/`
(verified reachable from Instinct's sandbox 2026-11-03; the municipality's own
site `betshemesh.muni.il` is behind Cloudflare and blocks datacenter IPs — the
Bina host does not).

App-wide shared secret: `secret=[configure BSMOKED_SECRET; value intentionally omitted]` (embedded in the public APK; same
standing as Jerusalem's embedded subscription key).

### 1. Street list — `GET get_streets.php?secret=<secret>`

Verified live 2026-11-03: HTTP 200, 428 streets, JSON
`{"streets":[{"name":"אבא נעמת","homes":[],"id":"42"}, ...]}`.
Notes: works even without the secret (server does not enforce it here);
`homes` is always empty, so the house number is free text; names may carry
trailing spaces; ids are strings.

### 2. File a report — `GET insert_call.php` (query params)

NOT probed (any successful call creates a real municipal ticket).

Reporter block (from the app's local profile form):
- `secret` — the shared secret above
- `fn`, `ln` — reporter first/last name (required by the app)
- `tz` — ID number; the app never sets it, sends "". Not required.
- `cellphone` — reporter mobile (required by the app)
- `email` — optional
- `myHome`, `address` — reporter's own house number / street (optional)
- `hash` — the `user_hash` returned by a previous `insert_call`; "" on the
  first report. Ties reports to one contact; server-side it presumably
  drives the SMS ticket confirmation.

Event block:
- Branch A (street picked from list): `street` (name), `home` (house no.,
  free text), `streetId` (id from get_streets)
- Branch B (GPS): `street`, `home` (from Google reverse geocode),
  `event_lat`, `event_lng`
- `description` — free text, required. There is NO category/subject field and
  NO license-plate field (unlike Jerusalem's 72 category codes); a plate goes
  inside the description.
- `img1`..`img4` — public URLs of uploaded images (see below); "" when none.

Response: JSON `{"status": <int>, "number": "<case number>",
"user_hash": "<hash>"}`. The app toasts "פניתך נשלחה בהצלחה, מספר הפניה שלך
הוא: <number>" — the case number is returned synchronously, unlike Jerusalem
(where it arrives later by email). Failure is signaled by an empty/"0" number.

### 3. Photo upload — `POST https://uploads.binaa.co.il/upload.php`

Query: `folder_name=app.betshemesh.muni.il&file_name=<epoch_ms>_<1..4>.png`.
Body: `multipart/form-data`, single field `imageToAttach` (app sends the file
bytes; filename inside the part is the same `file_name`). Hard 25 MiB cap in
the app (downscales to ≤1024px first). After upload the public URL is
`https://uploads.binaa.co.il/app.betshemesh.muni.il/<YYYY>/<MM>/<file_name>`
(month computed in Asia/Jerusalem). The app ignores the upload response body;
failure handling is weak — we should verify the URL returns 200 before filing.

### 4. Personal area / status — `GET profile.php` + webview

`GET profile.php?cellphone=<num>` → if the number is registered, sends an SMS
OTP and returns `{"status":1}`; then `GET profile.php?cellphone=<num>
&secret=<otp>` → `{"status":1,"user":{"hash","first_name","last_name"}}`.
The app then opens the webview
`https://betshemesh.muni.il/moked-profile/?app=1&cellphone=<num>&hash=<hash>`
which shows the resident's calls and their statuses. There is no REST
status-list endpoint in the modern stack. Status checking therefore needs
either the reporter's phone for the OTP (Meir forwards the code, or his own
Instinct does it) or scraping the webview page (Cloudflare may block us there;
untested — do not probe without approval). Do NOT probe profile.php with real
phone numbers: step 1 sends a real SMS.

### Legacy stack (do not use)

`GET https://betshemesh.muni.il/app/add_report.php` and `get_reportsByUser.php`
with shared creds `username=beitshemesh&userpass=1111` (embedded in the APK),
fields `rAddress`, `rInfo`, `rImg1..4`, `pFName/pLName/pCellphone/pKCellphone/
pHome/pStreet`, `userId` (server-assigned, persisted). Older hazard form; the
host is Cloudflare-blocked from our network (403 verified 2026-11-03). The
modern insert_call flow supersedes it and returns a real case number.

## Proposed pipeline (mirrors parking-reports)

1. Meir (or his Instinct) sends a photo + note.
2. GPS from EXIF → nearest street in the get_streets table (streetId branch),
   house number free text.
3. Description: what is seen + plate when it's a vehicle (registry facts can
   be appended exactly like Jerusalem).
4. Upload images (≤4, downscaled), verify each URL is fetchable.
5. `insert_call` → store `number` + `user_hash` (first call), reuse the hash
   afterwards. Summary line with the case number, same as Jerusalem's email.
6. Status: via profile.php OTP owned by the reporter — Meir's Instinct is the
   natural owner of that step.

## What we need before any live filing

- Approval to file real reports (this research got approval for read-only
  probing only). The first insert_call is a real municipal ticket; suggest a
  genuine small report as the test.
- Whose identity files: Meir's details (name, cellphone; his Instinct should
  hold them) — needs Meir's consent. No ID number is required.
- Confirmations/SMS go to the contact phone — Meir's.
- The municipality published no API terms of use; the secret is embedded in
  the public app (like Jerusalem). Rate limits unknown — be conservative.
- GitHub Actions reachability to bshemesh.moked-binaa.co.il is unverified
  (Jerusalem blocks GH runners; if the same holds here, filing runs from
  Instinct directly, like Jerusalem since 2026-10-12).

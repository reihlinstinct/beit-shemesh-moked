"""Beit Shemesh moked (Bina CRM) client. Stdlib only.

Filing (insert_call, upload) is guarded: functions build and return the
prepared request by default and only touch the network when live=True AND the
environment variable BSMOKED_LIVE=1 is set. Never file without the user's
explicit approval (see docs/design.md).
"""
import json
import os
import urllib.parse
import urllib.request

API_BASE = "https://bshemesh.moked-binaa.co.il/api/"
UPLOAD_BASE = "https://uploads.binaa.co.il/"
UPLOAD_FOLDER = "app.betshemesh.muni.il"
APP_SECRET = os.environ.get("BSMOKED_SECRET", "3Q03YE3OG5")  # embedded in the public APK
MAX_IMAGES = 4
USER_AGENT = "beit-shemesh-moked/0.1"


def _live_ok(live):
    return live and os.environ.get("BSMOKED_LIVE") == "1"


def _get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_streets_url(base=API_BASE, secret=APP_SECRET):
    return urllib.parse.urljoin(base, "get_streets.php") + "?" + urllib.parse.urlencode({"secret": secret})


def get_streets(base=API_BASE, secret=APP_SECRET, live=True):
    """Street list is read-only; the app itself fetches it on every open."""
    data = _get_json(get_streets_url(base, secret))
    return data["streets"]


def build_insert_call_params(reporter, event, secret=APP_SECRET):
    """Assemble the exact param set the app sends to insert_call.php.

    reporter: {fn, ln, cellphone, email?, my_home?, address?, tz?, hash?}
    event:    {description, street, home, street_id?  OR  event_lat/event_lng,
               images: [public urls up to 4]}
    """
    p = {
        "secret": secret,
        "fn": reporter.get("fn", ""),
        "ln": reporter.get("ln", ""),
        "tz": reporter.get("tz", ""),
        "cellphone": reporter.get("cellphone", ""),
        "email": reporter.get("email", ""),
        "myHome": reporter.get("my_home", ""),
        "address": reporter.get("address", ""),
        "hash": reporter.get("hash", ""),
        "description": event["description"],
    }
    if event.get("street_id"):
        p["street"] = event["street"]
        p["home"] = event.get("home", "")
        p["streetId"] = str(event["street_id"])
    else:
        p["street"] = event["street"]
        p["home"] = event.get("home", "")
        p["event_lat"] = str(event["event_lat"])
        p["event_lng"] = str(event["event_lng"])
    images = list(event.get("images", []))[:MAX_IMAGES]
    for i in range(MAX_IMAGES):
        p[f"img{i+1}"] = images[i] if i < len(images) else ""
    return p


def insert_call_url(params, base=API_BASE):
    # The app concatenates base + "/insert_call.php" (double slash works);
    # urljoin normalizes it.
    return urllib.parse.urljoin(base, "insert_call.php") + "?" + urllib.parse.urlencode(params)


def parse_insert_call_response(payload):
    """Return (ok, case_number, user_hash). The app treats ''/'0' as failure."""
    data = json.loads(payload) if isinstance(payload, str) else payload
    number = str(data.get("number", ""))
    user_hash = str(data.get("user_hash", ""))
    ok = number not in ("", "0", "None")
    return ok, (number if ok else ""), user_hash


def insert_call(reporter, event, secret=APP_SECRET, base=API_BASE, live=False):
    """File a report. Default: returns the prepared URL without sending."""
    params = build_insert_call_params(reporter, event, secret)
    url = insert_call_url(params, base)
    if not _live_ok(live):
        return {"sent": False, "url": url, "params": params}
    data = _get_json(url)
    ok, number, user_hash = parse_insert_call_response(data)
    return {"sent": True, "ok": ok, "number": number, "user_hash": user_hash}


def upload_filename(epoch_ms, index):
    return f"{epoch_ms}_{index}.png"


def upload_url(folder=UPLOAD_FOLDER, file_name="", base=UPLOAD_BASE):
    return urllib.parse.urljoin(base, "upload.php") + "?" + urllib.parse.urlencode(
        {"folder_name": folder, "file_name": file_name})


def public_image_url(year, month, file_name, folder=UPLOAD_FOLDER, base=UPLOAD_BASE):
    return f"{base}{folder}/{year}/{month:02d}/{file_name}"


def build_multipart(field, file_name, data, boundary="---------------------------7d226f700d0"):
    head = (f"{boundary}\r\nContent-Disposition: form-data; name=\"{field}\";"
            f"filename={file_name}\r\n\r\n").encode()
    return head + data + f"\r\n{boundary}--\r\n".encode(), boundary

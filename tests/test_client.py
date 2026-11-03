import json
import os
import sys
import unittest
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import bsmoked_client as c  # noqa: E402


class TestStreets(unittest.TestCase):
    def test_url_contains_secret_and_path(self):
        url = c.get_streets_url(secret="S")
        self.assertTrue(url.startswith("https://bshemesh.moked-binaa.co.il/api/"))
        self.assertIn("get_streets.php", url)
        self.assertIn("secret=S", url)

    def test_fixture_shape(self):
        # Mirrors the verified live response (2026-11-03, 428 streets).
        fixture = {"streets": [
            {"name": "אבא נעמת", "homes": [], "id": "42"},
            {"name": "אביטל", "homes": [], "id": "41"},
            {"name": "אביי", "homes": [], "id": "771"},
        ]}
        streets = fixture["streets"]
        self.assertEqual(streets[0]["name"], "אבא נעמת")
        self.assertEqual(streets[0]["id"], "42")
        self.assertEqual(streets[0]["homes"], [])


REPORTER = {"fn": "משה", "ln": "כהן", "cellphone": "0500000000",
            "email": "m@example.com", "my_home": "3", "address": "הרצל", "hash": "H1"}


class TestInsertCallParams(unittest.TestCase):
    def test_street_branch(self):
        p = c.build_insert_call_params(REPORTER, {
            "description": "רכב חוסם מדרכה, מ.ר. 1234567",
            "street": "אבא נעמת", "home": "5", "street_id": "42",
            "images": ["https://u/1.png", "https://u/2.png"]})
        self.assertEqual(p["streetId"], "42")
        self.assertNotIn("event_lat", p)
        self.assertEqual(p["img1"], "https://u/1.png")
        self.assertEqual(p["img2"], "https://u/2.png")
        self.assertEqual(p["img3"], "")
        self.assertEqual(p["img4"], "")
        self.assertEqual(p["tz"], "")          # app never sets an ID number
        self.assertEqual(p["hash"], "H1")      # returning contact
        self.assertEqual(p["cellphone"], "0500000000")
        self.assertEqual(p["secret"], c.APP_SECRET)

    def test_gps_branch(self):
        p = c.build_insert_call_params(REPORTER, {
            "description": "עמוד נפל",
            "street": "הרצל", "home": "10",
            "event_lat": 31.745, "event_lng": 34.989})
        self.assertEqual(p["event_lat"], "31.745")
        self.assertEqual(p["event_lng"], "34.989")
        self.assertNotIn("streetId", p)

    def test_first_report_sends_empty_hash(self):
        r = dict(REPORTER); r.pop("hash")
        p = c.build_insert_call_params(r, {
            "description": "x", "street": "אבא נעמת", "home": "5", "street_id": "42"})
        self.assertEqual(p["hash"], "")

    def test_images_capped_at_four(self):
        p = c.build_insert_call_params(REPORTER, {
            "description": "x", "street": "s", "home": "1", "street_id": "1",
            "images": ["a", "b", "c", "d", "e"]})
        self.assertEqual(p["img4"], "d")

    def test_hebrew_is_url_encoded(self):
        url = c.insert_call_url(c.build_insert_call_params(REPORTER, {
            "description": "רכב חוסם מדרכה", "street": "אבא נעמת",
            "home": "5", "street_id": "42"}))
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        self.assertEqual(qs["street"], ["אבא נעמת"])
        self.assertEqual(qs["description"], ["רכב חוסם מדרכה"])


class TestResponseParsing(unittest.TestCase):
    def test_success(self):
        ok, number, h = c.parse_insert_call_response(
            '{"status": 1, "number": "12345", "user_hash": "abc"}')
        self.assertTrue(ok)
        self.assertEqual(number, "12345")
        self.assertEqual(h, "abc")

    def test_failure_zero(self):
        ok, number, _ = c.parse_insert_call_response('{"status": 0, "number": "0"}')
        self.assertFalse(ok)
        self.assertEqual(number, "")

    def test_failure_empty(self):
        ok, _, _ = c.parse_insert_call_response('{"status": 0}')
        self.assertFalse(ok)


class TestFilingGuard(unittest.TestCase):
    def test_default_does_not_send(self):
        out = c.insert_call(REPORTER, {
            "description": "x", "street": "s", "home": "1", "street_id": "1"})
        self.assertFalse(out["sent"])
        self.assertIn("insert_call.php", out["url"])

    def test_live_requires_env(self):
        os.environ.pop("BSMOKED_LIVE", None)
        out = c.insert_call(REPORTER, {
            "description": "x", "street": "s", "home": "1", "street_id": "1"}, live=True)
        self.assertFalse(out["sent"])


class TestUploadHelpers(unittest.TestCase):
    def test_filename(self):
        self.assertEqual(c.upload_filename(1730000000000, 2), "1730000000000_2.png")

    def test_upload_url(self):
        url = c.upload_url(file_name="1730000000000_1.png")
        self.assertEqual(url, "https://uploads.binaa.co.il/upload.php?"
                              "folder_name=app.betshemesh.muni.il&file_name=1730000000000_1.png")

    def test_public_url(self):
        self.assertEqual(
            c.public_image_url(2026, 11, "1730000000000_1.png"),
            "https://uploads.binaa.co.il/app.betshemesh.muni.il/2026/11/1730000000000_1.png")

    def test_multipart_shape(self):
        body, boundary = c.build_multipart("imageToAttach", "f.png", b"PNGDATA")
        self.assertIn(b'name="imageToAttach";filename=f.png', body)
        self.assertTrue(body.endswith(boundary.encode() + b"--\r\n"))
        self.assertIn(b"PNGDATA", body)


if __name__ == "__main__":
    unittest.main()

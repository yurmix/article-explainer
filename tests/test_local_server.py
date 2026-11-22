"""Local HTTP/security regression tests; no dependencies, audio playback, or external network access.

Place in repository tests/ and run: python -m unittest discover -s tests -v
Fixtures are generated in a temporary folder. Symlink cases skip on platforms
that do not permit creating symlinks; all other checks still run.
"""

import functools
import http.client
import importlib.util
from pathlib import Path
import tempfile
import threading
import unittest


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        helper = Path(__file__).resolve().parents[1] / "scripts" / "serve_local.py"
        spec = importlib.util.spec_from_file_location("serve_local", helper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.temp = tempfile.TemporaryDirectory(prefix="article-server-test-")
        cls.addClassCleanup(cls.temp.cleanup)
        base = Path(cls.temp.name)
        cls.root = base / "site with spaces"
        cls.root.mkdir()
        (cls.root / "sample.wav").write_bytes(b"0123456789")
        (cls.root / "empty.wav").write_bytes(b"")
        (cls.root / "index.html").write_text("Home", encoding="utf-8")
        (cls.root / ".secret").write_text("private fixture", encoding="utf-8")
        (cls.root / ".hidden").mkdir()
        (cls.root / ".hidden" / "ordinary.html").write_text("private fixture", encoding="utf-8")
        (cls.root / "folder").mkdir()
        (cls.root / "folder" / "index.html").write_text("Nested", encoding="utf-8")
        (cls.root / "unlisted").mkdir()
        outside = base / "outside.txt"
        outside.write_text("outside fixture", encoding="utf-8")
        cls.symlinks_available = True
        try:
            (cls.root / "escape.txt").symlink_to(outside)
            for folder, target in [
                ("hidden-alias", cls.root / ".secret"),
                ("directory-alias", cls.root / ".hidden" / "ordinary.html"),
                ("outside-index", outside),
            ]:
                (cls.root / folder).mkdir()
                (cls.root / folder / "index.html").symlink_to(target)
        except (OSError, NotImplementedError):
            cls.symlinks_available = False

        class QuietHandler(module.LocalHandler):
            def log_message(self, *args):
                pass

        cls.server = module.ThreadingHTTPServer(
            ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(cls.root))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.stop_server)
        cls.authority = f"127.0.0.1:{cls.server.server_port}"
        cls.origin = f"http://{cls.authority}"

    @classmethod
    def stop_server(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def assert_response(self, status, body=None, *, method="GET", path="/sample.wav", headers=None,
                        content_range=None, length=None, raw_headers=None):
        client = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            if raw_headers is None:
                client.request(method, path, headers=headers or {})
            else:
                client.putrequest(method, path, skip_host=True)
                for key, value in raw_headers:
                    client.putheader(key, value)
                client.endheaders()
            response = client.getresponse()
            actual = response.read()
            self.assertEqual(response.status, status)
            if body is not None:
                self.assertEqual(actual, body)
            self.assertEqual(response.getheader("Content-Range"), content_range)
            if length is not None:
                self.assertEqual(response.getheader("Content-Length"), str(length))
            if status in (200, 206, 416) and path.endswith(".wav"):
                self.assertEqual(response.getheader("Accept-Ranges"), "bytes")
            if status in (200, 206):
                self.assertEqual(response.getheader("Cross-Origin-Resource-Policy"), "same-origin")
            self.assertNotIn(b"private fixture", actual)
            self.assertNotIn(b"outside fixture", actual)
        finally:
            client.close()

    def test_full_and_head(self):
        self.assert_response(200, b"0123456789", length=10)
        self.assert_response(200, b"", path="/empty.wav", length=0)
        self.assert_response(200, b"", method="HEAD", length=10)
        self.assert_response(200, b"", method="HEAD", headers={"Range": "bytes=2-5"}, length=10)

    def test_satisfiable_ranges(self):
        cases = [
            ("bytes=2-5", b"2345", "bytes 2-5/10"),
            ("bytes=7-", b"789", "bytes 7-9/10"),
            ("bytes=-3", b"789", "bytes 7-9/10"),
            ("bytes=-99", b"0123456789", "bytes 0-9/10"),
            ("bytes=8-100", b"89", "bytes 8-9/10"),
        ]
        for value, body, selected in cases:
            with self.subTest(value=value):
                self.assert_response(206, body, headers={"Range": value}, content_range=selected, length=len(body))

    def test_unsatisfiable_ranges(self):
        for value in ("bytes=10-", "bytes=-0"):
            with self.subTest(value=value):
                self.assert_response(416, b"", headers={"Range": value}, content_range="bytes */10", length=0)
        self.assert_response(416, b"", path="/empty.wav", headers={"Range": "bytes=0-"}, content_range="bytes */0", length=0)

    def test_ignored_ranges(self):
        for value in ("items=2-5", "bytes=wat", "bytes=8-2", "bytes=0-1,4-5", "bytes=" + "9" * 500 + "-5"):
            with self.subTest(value=value):
                self.assert_response(200, b"0123456789", headers={"Range": value}, length=10)
        self.assert_response(200, b"0123456789", headers={"Range": "bytes=2-5", "If-Range": '"unknown"'}, length=10)

    def test_static_paths(self):
        self.assert_response(200, b"Home", path="/")
        self.assert_response(301, b"", path="/folder", length=0)
        self.assert_response(200, b"Nested", path="/folder/")
        for path in ("/unlisted/", "/.secret", "/missing"):
            with self.subTest(path=path):
                self.assert_response(404, path=path)

    def test_symlink_boundaries(self):
        if not self.symlinks_available:
            self.skipTest("This platform does not permit symlink fixtures")
        for path in ("/escape.txt", "/hidden-alias/", "/directory-alias/", "/outside-index/"):
            with self.subTest(path=path):
                self.assert_response(404, path=path)

    def test_same_origin_requests(self):
        self.assert_response(206, b"2345", headers={"Range": "bytes=2-5", "Origin": self.origin,
                             "Sec-Fetch-Site": "same-origin"}, content_range="bytes 2-5/10", length=4)
        self.assert_response(200, b"Home", path="/", headers={"Sec-Fetch-Site": "none"})

    def test_foreign_headers(self):
        cases = [
            {"Host": f"attacker.invalid:{self.server.server_port}"},
            {"Host": "127.0.0.1:1"},
            {"Origin": "https://attacker.invalid"},
            {"Origin": "null"},
            {"Origin": f"https://{self.authority}"},
            {"Sec-Fetch-Site": "cross-site"},
            {"Sec-Fetch-Site": "same-site"},
        ]
        for headers in cases:
            with self.subTest(headers=headers):
                self.assert_response(403, headers=headers)
        self.assert_response(403, path="/folder", headers={"Host": "attacker.invalid"})
        self.assert_response(403, b"", method="HEAD", headers={"Origin": "https://attacker.invalid"})

    def test_missing_and_duplicate_headers(self):
        cases = [[], [("Host", self.authority), ("Host", self.authority)],
                 [("Host", self.authority), ("Origin", self.origin), ("Origin", self.origin)]]
        for headers in cases:
            with self.subTest(headers=headers):
                self.assert_response(403, raw_headers=headers)

    def test_user_activated_navigation_only(self):
        navigation = {"Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "navigate",
                      "Sec-Fetch-Dest": "document", "Sec-Fetch-User": "?1"}
        self.assert_response(200, b"Home", path="/", headers=navigation)
        self.assert_response(200, b"Home", path="/", headers={**navigation, "Sec-Fetch-Site": "same-site"})
        for overrides in ({"Sec-Fetch-Dest": "iframe"}, {"Sec-Fetch-Mode": "cors"},
                          {"Sec-Fetch-User": "?0"}, {"Origin": "https://attacker.invalid"},
                          {"Host": "attacker.invalid"}):
            with self.subTest(overrides=overrides):
                self.assert_response(403, path="/", headers={**navigation, **overrides})
        for header in ("Sec-Fetch-Mode", "Sec-Fetch-Dest", "Sec-Fetch-User", "Sec-Fetch-Site"):
            with self.subTest(duplicate=header):
                duplicates = [("Host", self.authority), *navigation.items(), (header, navigation[header])]
                self.assert_response(403, path="/", raw_headers=duplicates)


if __name__ == "__main__":
    unittest.main()

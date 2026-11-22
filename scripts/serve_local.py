#!/usr/bin/env python3
"""Serve a local static explainer with seekable audio, using only Python's stdlib.

Usage: python3.12 serve_local.py --directory "My Explainer/site" --port 4327
GET supports one bytes range (206), including open-ended and suffix ranges.
Unsatisfiable ranges return 416. Unsupported, malformed, and multiple ranges
are ignored (200). HEAD ignores Range, as required by HTTP semantics.
Use the printed 127.0.0.1 URL; foreign Host and Origin requests are rejected.
This loopback-only development server is not a public hosting service.
"""

import argparse
import functools
import os
from pathlib import Path
import re
import stat
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, urlunsplit


def byte_range(value, size):
    """Return (start, end), None for ignored input, or False for unsatisfiable."""
    if not value or len(value) > 128:
        return None
    match = re.fullmatch(r"bytes=([0-9]*)-([0-9]*)", value.strip())
    if not match or not any(match.groups()):
        return None
    first, last = match.groups()
    if not first:
        suffix = int(last)
        return (max(0, size - suffix), size - 1) if suffix and size else False
    start = int(first)
    end = int(last) if last else size - 1
    if last and end < start:
        return None
    if start >= size:
        return False
    return start, min(end, size - 1)


class LocalHandler(SimpleHTTPRequestHandler):
    server_version = "ArticleExplainerLocal/1.0"
    sys_version = ""

    def allowed_request(self):
        # Binding loopback alone does not reject a hostile DNS-rebinding Host.
        # Only the exact local origin printed at startup may read these files.
        authority = f"127.0.0.1:{self.server.server_port}"
        authorities = {authority}
        if self.server.server_port == 80:
            authorities.add("127.0.0.1")
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        sites = self.headers.get_all("Sec-Fetch-Site", [])
        modes = self.headers.get_all("Sec-Fetch-Mode", [])
        destinations = self.headers.get_all("Sec-Fetch-Dest", [])
        users = self.headers.get_all("Sec-Fetch-User", [])
        # A deliberate top-level link from a chat may be cross-site. It may
        # open the local page, but cannot embed it or read it from that origin.
        navigation = modes == ["navigate"] and destinations == ["document"] and users == ["?1"]
        allowed = (
            len(hosts) == 1 and hosts[0].strip() in authorities
            and (not origins or len(origins) == 1 and origins[0].strip() in {f"http://{host}" for host in authorities})
            and all(len(values) <= 1 for values in (modes, destinations, users))
            and (not sites or len(sites) == 1 and (
                sites[0].strip() in {"none", "same-origin"}
                or sites[0].strip() in {"same-site", "cross-site"} and navigation
            ))
        )
        if not allowed:
            self.send_error(403, "Use the local URL printed by this server")
        return allowed

    def send_head(self):
        self.remaining = 0
        if not self.allowed_request():
            return None
        root = Path(self.directory).resolve()
        path = Path(self.translate_path(self.path))
        try:
            resolved = path.resolve()
            relative = resolved.relative_to(root)
            if any(part.startswith(".") for part in relative.parts):
                self.send_error(404, "File not found")
                return None
            if resolved.is_dir():
                parts = urlsplit(self.path)
                if not parts.path.endswith("/"):
                    self.send_response(301)
                    location = urlunsplit(("", "", "/" + parts.path.lstrip("/") + "/", parts.query, ""))
                    self.send_header("Location", location)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None
                for index in ("index.html", "index.htm"):
                    candidate = resolved / index
                    if candidate.is_file():
                        resolved = candidate.resolve()
                        break
                else:
                    self.send_error(404, "No index page; directory listing is disabled")
                    return None
            # Index files may themselves be symlinks. Recheck the final target,
            # including hidden directories, before opening any content.
            relative = resolved.relative_to(root)
            if any(part.startswith(".") for part in relative.parts):
                self.send_error(404, "File not found")
                return None
            if not resolved.is_file():
                self.send_error(404, "File not found")
                return None
            source = resolved.open("rb")
            metadata = os.fstat(source.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                source.close()
                self.send_error(404, "File not found")
                return None
        except (OSError, ValueError):
            self.send_error(404, "File not found")
            return None

        size = metadata.st_size
        # If-Range is conservatively answered with the complete current file.
        # Repeated Range fields are also unsupported, like multipart ranges.
        ranges = self.headers.get_all("Range", [])
        selected = None
        if self.command == "GET" and len(ranges) == 1 and not self.headers.get("If-Range"):
            selected = byte_range(ranges[0], size)
        if selected is False:
            source.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        start, end = selected if selected is not None else (0, size - 1)
        self.remaining = max(0, end - start + 1)
        self.send_response(206 if selected is not None else 200)
        self.send_header("Content-Type", self.guess_type(str(resolved)))
        self.send_header("Content-Length", str(self.remaining))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", self.date_time_string(metadata.st_mtime))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        if selected is not None:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        source.seek(start)
        return source

    def copyfile(self, source, outputfile):
        # A browser may abandon an earlier range while the viewer seeks again.
        try:
            while self.remaining:
                chunk = source.read(min(64 * 1024, self.remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                self.remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path.cwd(), help="Static site folder")
    parser.add_argument("--port", type=int, default=4327, help="Local port (default: 4327)")
    args = parser.parse_args()
    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        parser.error(f"Site directory does not exist: {directory}")
    if not 0 <= args.port <= 65535:
        parser.error("Port must be between 0 and 65535")
    handler = functools.partial(LocalHandler, directory=str(directory))
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            print(f"Open http://127.0.0.1:{server.server_port}/", flush=True)
            print(f"Serving {directory}\nKeep this terminal open. Press Ctrl+C to stop.", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    except OSError as error:
        parser.exit(1, f"Could not start the local server: {error}\nTry another --port if it is already in use.\n")


if __name__ == "__main__":
    main()

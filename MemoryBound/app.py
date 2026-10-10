import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        mb = int(query.get("mb", [50])[0])
        hold_ms = int(query.get("hold_ms", [500])[0])

        data = b"x" * (mb * 1024 * 1024)
        time.sleep(hold_ms / 1000)
        del data

        body = f"alocou {mb} MB por {hold_ms} ms\n".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


ThreadingHTTPServer.request_queue_size = 128
ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

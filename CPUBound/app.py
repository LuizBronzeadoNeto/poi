from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import random
from prometheus_client import Counter, Gauge, Histogram, start_http_server

REQUESTS = Counter("http_requests_total", "Requests handled", ["status"])
IN_FLIGHT = Gauge("http_requests_in_flight", "Requests currently running")
LATENCY = Histogram(
    "http_request_seconds",
    "Request latency",
    buckets=(0.1, 0.5, 1, 5, 10, 30, 60, 120, 300)
)

class HighQueueThreadingServer(ThreadingHTTPServer):
    allow_reuse_address = True
    request_queue_size = 128 

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        bound = random.randint(0, 200000)
        body = f"contando primos até {bound}".encode()
        with IN_FLIGHT.track_inprogress(), LATENCY.time():
            self.count_primes(bound)
        REQUESTS.labels(status="200").inc()

        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def count_primes(bound: int) -> int:
        num_primes = 0
        for i in range(2, bound):
            for j in range(2, i):
                if i % j == 0:
                    break
            else:
                num_primes += 1
        return num_primes

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    start_http_server(9101)
    HighQueueThreadingServer(("0.0.0.0", 8000), Handler).serve_forever()


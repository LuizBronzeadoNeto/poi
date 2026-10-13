from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import random

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        bound = random.randint(0,200000)
        body = f"contando primos até {bound}"
        self.count_primes(bound)

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


ThreadingHTTPServer.request_queue_size = 128
ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()


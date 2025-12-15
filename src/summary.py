import http.server
import time
import random
from prometheus_client import (
    start_http_server,
    Counter,
    Histogram
)

APP_PORT = 8000
METRICS_PORT = 8001

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    buckets=[0.5, 1, 2, 3, 5, 8, 10]
)

class HandleRequests(http.server.BaseHTTPRequestHandler):

    @REQUEST_LATENCY.time()
    def do_GET(self):
        delay = random.choice([0.2, 0.5, 1, 3, 6])
        time.sleep(delay)

        if delay > 5:
            status = 500
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
        else:
            status = 200
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello from Prometheus demo app!")

        REQUEST_COUNT.labels(
            method="GET",
            status=str(status)
        ).inc()

if __name__ == "__main__":
    start_http_server(METRICS_PORT)
    server = http.server.HTTPServer(('localhost', APP_PORT), HandleRequests)
    server.serve_forever()

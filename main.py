import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open('index.html', 'rb') as f:
            self.wfile.write(f.read())

port = int(os.environ.get("PORT", 8080))
server = HTTPServer(('0.0.0.0', port), SimpleHandler)
print(f"Activity running on port {port}")
server.serve_forever()

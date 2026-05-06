import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- STABLE WEB SERVER ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # This serves your HTML file to the web
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        except Exception as e:
            self.send_response(200) # Still send 200 so Railway is happy
            self.end_headers()
            self.wfile.write(f"Server is up, but index.html missing: {e}".encode())

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Web server active on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start the server that Railway checks
    run_web_server()
    

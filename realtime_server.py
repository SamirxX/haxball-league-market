import http.server
import socketserver
import json
import os
import sys

# Read PORT from Render / Cloud environment or default to 8086
PORT = int(os.environ.get('PORT', 8086))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared_market.json')
LEADER_PASSCODE = "PRIM-LEADER-2026"

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class RealtimeMarketHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/players':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"[]")
        else:
            if self.path == '/' or self.path == '/index.html':
                self.path = '/players_market.html'
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/players/update':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                passcode = payload.get('passcode', '')
                
                if passcode != LEADER_PASSCODE:
                    self.send_response(403)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid Leader Passcode!"}).encode('utf-8'))
                    return
                
                updated_players = payload.get('players', [])
                if updated_players:
                    with open(DATA_FILE, 'w', encoding='utf-8') as f:
                        json.dump(updated_players, f, indent=4)
                    print(f"⚡ [REALTIME SYNC] Roster updated by a Leader!", flush=True)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Market updated live!"}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == "__main__":
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), RealtimeMarketHandler) as httpd:
        print(f"==================================================", flush=True)
        print(f"🚀 Realtime Collaborative Market Server running on port {PORT}", flush=True)
        print(f"🔑 Leader Passcode: {LEADER_PASSCODE}", flush=True)
        print(f"==================================================", flush=True)
        httpd.serve_forever()

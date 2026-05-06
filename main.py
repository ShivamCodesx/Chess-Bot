import berserk
import chess
import threading
import requests
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # This looks for the index.html file in your folder
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"index.html not found in your folder!")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: {e}".encode())

def run_dummy_server():
    # Railway assigns a port, or we use 8080 as a backup
    port = int(os.environ.get("PORT", 8080))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Dummy server listening on port {port}")
    httpd.serve_forever()

# --- THE REST OF YOUR BOT CODE BELOW ---
# (Keep your TOKEN, upgrade_account, play_game, and start functions here)

TOKEN = os.environ.get("LICHESS_TOKEN", "your_backup_token_here")


session = berserk.TokenSession(TOKEN)
client = berserk.Client(session=session)

def upgrade_account():
    try:
        profile = client.account.get()
        if profile.get('title') != 'BOT':
            print("Upgrading to BOT account...")
            requests.post("https://lichess.org/api/bot/account/upgrade", 
                          headers={"Authorization": f"Bearer {TOKEN}"})
        else:
            print(f"Logged in as BOT: {profile['username']}")
    except Exception as e:
        print(f"Error during account upgrade: {e}")

def play_game(game_id):
    board = chess.Board()
    print(f"Game {game_id} started!")

    try:
        for event in client.bots.stream_game_state(game_id):
            if event['type'] == 'gameFull':
                # Check if Bot is White
                if event['white'].get('id') == client.account.get()['id']:
                    client.bots.make_move(game_id, "e2e4")
            
            elif event['type'] == 'gameState':
                moves = event['moves'].split()
                board = chess.Board()
                for move in moves:
                    board.push_uci(move)
                
                # Check if it's the Bot's turn
                bot_id = client.account.get()['id']
                is_white = event.get('white', {}).get('id') == bot_id
                
                if (board.turn == chess.WHITE and is_white) or \
                   (board.turn == chess.BLACK and not is_white):
                    
                    legal_moves = list(board.legal_moves)
                    if legal_moves:
                        my_move = legal_moves[0] # Basic AI: Pick first legal move
                        client.bots.make_move(game_id, my_move.uci())
    except Exception as e:
        print(f"Error in game {game_id}: {e}")

def start():
    upgrade_account()
    print("Waiting for challenges...")
    try:
        for event in client.bots.stream_incoming_events():
            if event['type'] == 'challenge':
                cid = event['challenge']['id']
                print(f"Accepting challenge {cid}")
                client.bots.accept_challenge(cid)
                threading.Thread(target=play_game, args=(cid,)).start()
    except Exception as e:
        print(f"Error in event stream: {e}")

if __name__ == "__main__":
    # 1. Start the dummy server in the background
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # 2. Start the Lichess Bot
    start()
    

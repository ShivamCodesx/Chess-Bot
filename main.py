import berserk
import chess
import threading
import requests
import os

# --- PASTE YOUR TOKEN HERE ---
TOKEN = "lip_qcwk3fpoKHutAo7Ib9LV"
# -----------------------------

session = berserk.TokenSession(TOKEN)
client = berserk.Client(session=session)

def upgrade_account():
    profile = client.account.get()
    if profile.get('title') != 'BOT':
        print("Upgrading to BOT account...")
        requests.post("https://lichess.org/api/bot/account/upgrade", 
                      headers={"Authorization": f"Bearer {TOKEN}"})
    else:
        print(f"Logged in as BOT: {profile['username']}")

def play_game(game_id):
    # This uses the 'python-chess' library to track legal moves
    board = chess.Board()
    print(f"Game {game_id} started!")

    for event in client.bots.stream_game_state(game_id):
        if event['type'] == 'gameFull':
            # Handle start of game
            if event['white'].get('id') == client.account.get()['id']:
                # Bot is white, make first move
                client.bots.make_move(game_id, "e2e4")
        
        elif event['type'] == 'gameState':
            moves = event['moves'].split()
            board = chess.Board()
            for move in moves:
                board.push_uci(move)
            
            # If it is the BOT's turn
            if (board.turn == chess.WHITE and board.white_id == 'bot') or \
               (board.turn == chess.BLACK and board.black_id == 'bot'):
                
                # BASIC AI: Pick the first legal move
                # You can replace this with Stockfish later!
                my_move = list(board.legal_moves)[0]
                client.bots.make_move(game_id, my_move.uci())

def start():
    upgrade_account()
    print("Waiting for challenges...")
    for event in client.bots.stream_incoming_events():
        if event['type'] == 'challenge':
            cid = event['challenge']['id']
            client.bots.accept_challenge(cid)
            threading.Thread(target=play_game, args=(cid,)).start()

if __name__ == "__main__":
    start()


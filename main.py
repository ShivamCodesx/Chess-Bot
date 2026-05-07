import os
import threading
import discord
from discord.ext import commands
import chess
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. WEB SERVER ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            if os.path.exists('index.html'):
                with open('index.html', 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.wfile.write(b"<h1>Bot is Online</h1><p>Server is running perfectly.</p>")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print("Web server running on port " + str(port))
    server.serve_forever()

# --- 2. DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
games = {}

@bot.event
async def on_ready():
    print("Bot is logged in as " + str(bot.user))

@bot.command()
async def play(ctx):
    games[ctx.author.id] = chess.Board()
    board_str = str(games[ctx.author.id])
    response = "**New Game Started!**\nYou are White.\n```\n" + board_str + "\n```\nType `!move e2e4` to play."
    await ctx.send(response)

@bot.command()
async def move(ctx, uci_move: str):
    if ctx.author.id not in games:
        await ctx.send("Start a game first with `!play`!")
        return

    board = games[ctx.author.id]
    try:
        my_move = chess.Move.from_uci(uci_move)
        if my_move in board.legal_moves:
            board.push(my_move)
            
            if board.is_game_over():
                await ctx.send("Game Over! Result: " + board.result())
                del games[ctx.author.id]
                return

            # Simple AI: Pick first legal move
            bot_move = list(board.legal_moves)[0]
            board.push(bot_move)
            
            board_str = str(board)
            res = "You: " + uci_move + " | Bot: " + bot_move.uci() + "\n```\n" + board_str + "\n```"
            await ctx.send(res)
            
            if board.is_game_over():
                await ctx.send("Game Over! Result: " + board.result())
                del games[ctx.author.id]
        else:
            await ctx.send("That move is not legal!")
    except:
        await ctx.send("Use UCI format (e.g., e2e4)")

# --- 3. START ---
if __name__ == "__main__":
    # Start web server in background
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Run Discord Bot
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("MISSING DISCORD_TOKEN in Railway Variables!")

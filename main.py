import os
import threading
import discord
from discord.ext import commands
import chess
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. THE WEB SERVER (No more random match logs) ---
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
                self.wfile.write(b"<h1>Bot is Online</h1><p>Upload index.html to see your dashboard.</p>")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print("Web server started on port " + str(port))
    server.serve_forever()

# --- 2. THE DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
games = {}

@bot.event
async def on_ready():
    print("Logged in as " + str(bot.user))

@bot.command()
async def play(ctx):
    games[ctx.author.id] = chess.Board()
    board_display = str(games[ctx.author.id])
    msg = "**Game Started!**\nYour move (White).\n```\n" + board_display + "\n```\nUse `!move e2e4`"
    await ctx.send(msg)

@bot.command()
async def move(ctx, uci_move: str):
    if ctx.author.id not in games:
        await ctx.send("Type `!play` to start a game first!")
        return

    board = games[ctx.author.id]
    try:
        player_move = chess.Move.from_uci(uci_move)
        if player_move in board.legal_moves:
            board.push(player_move)
            
            if board.is_game_over():
                await ctx.send("Game Over! Result: " + board.result())
                del games[ctx.author.id]
                return

            # Bot plays first legal move
            bot_move = list(board.legal_moves)[0]
            board.push(bot_move)
            
            board_display = str(board)
            response = "You moved " + uci_move + ". I moved " + bot_move.uci() + ".\n```\n" + board_display + "\n```"
            await ctx.send(response)
            
            if board.is_game_over():
                await ctx.send("Game Over! Result: " + board.result())
                del games[ctx.author.id]
        else:
            await ctx.send("Invalid move! Try something like `e2e4`.")
    except Exception:
        await ctx.send("Error! Use UCI format like `e2e4`.")

# --- 3. LAUNCH ---
if __name__ == "__main__":
    # Run web server in background
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()
    
    # Run Discord Bot
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("ERROR: DISCORD_TOKEN variable is missing in Railway!")

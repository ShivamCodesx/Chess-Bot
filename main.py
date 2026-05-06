import os
import threading
import discord
from discord.ext import commands
import chess
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. THE WEB SERVER (Shows your index.html & keeps Railway happy) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This fixes the "Random Match" issue by forcing the server to only show your file
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # This looks for your index.html file
            if os.path.exists('index.html'):
                with open('index.html', 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.wfile.write(b"<h1>Bot is Online</h1><p>index.html not found, but server is running!</p>")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: {e}".encode())

def run_web_server():
    # Railway assigns a port automatically
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Web interface live on port {port}")
    server.serve_forever()

# --- 2. THE DISCORD BOT (The Chess Brain) ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# This dictionary stores boards for different users so multiple people can play
games = {}

@bot.event
async def on_ready():
    print(f'Logged in as Discord Bot: {bot.user}')

@bot.command()
async def play(ctx):
    """Starts a new game for the user"""
    games[ctx.author.id] = chess.Board()
    board_str = games[ctx.author.id]
    await ctx.send(f"**Game Started vs {bot.user.name}!**\nYour move (White).\n
http://googleusercontent.com/immersive_entry_chip/0
2.  **Railway Variables:** * Add `PORT` = `8080`
    * Add `DISCORD_TOKEN` = `[Paste your token from Discord Dev Portal]`
3.  **Start Command:** Ensure Railway is set to run `python main.py`.

### How it works now:
* **The URL:** When you go to `chess-bot-production.up.railway.app`, it will look for your **`index.html`** and show it. No more random text.
* **The Discord Bot:** * Type **`!play`** to see the board in the chat.
    * Type **`!move e2e4`** to play a move.
    * The bot will immediately reply with its own move and an updated board.

**One final tip:** Since you're in Termux, make sure you `git add main.py`, `git commit -m "final stable version"`, and `git push` it. Once the deploy finishes, check your Discord—your bot should be glowing green and ready to play!
                

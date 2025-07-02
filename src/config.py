import os
import discord
from dotenv import load_dotenv

# Load environment variables from a .env file.
load_dotenv()

# --- Bot and API Credentials ---
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_OWNER_ID_STR = os.getenv("BOT_OWNER_ID")

# --- Bot Settings ---
COMMAND_PREFIX = '!'
USER_DATA_FILE = "horoscope_users.json" # Renamed for clarity

# --- Sanity Checks ---
if not DISCORD_BOT_TOKEN:
    print("FATAL ERROR: DISCORD_BOT_TOKEN not found in .env file.")
    exit(1)

# Convert owner_id to an integer.
try:
    BOT_OWNER_ID = int(BOT_OWNER_ID_STR) if BOT_OWNER_ID_STR else None
except (ValueError, TypeError):
    print(f"Warning: Invalid BOT_OWNER_ID. Owner-only commands may not work.")
    BOT_OWNER_ID = None

# --- API & AI Settings ---
BASE_CURRENCY_API_URL = "https://api.frankfurter.dev/v1/latest"
HISTORY_CURRENCY_API_URL = "https://currencyhistoryapi.tinaleewx99.workers.dev/"
DEFAULT_GEMINI_MODEL = 'gemini-1.5-flash'
MIN_GEMINI_DELAY = 1.1 # Seconds

# --- Bot Intents ---
# Centralize intents here so they can be imported.
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
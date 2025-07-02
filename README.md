Gemini Multi-Tool Discord Bot
A versatile, multi-functional Discord bot that integrates AI-powered chat, real-time currency exchange rates, and personalized daily horoscopes into a single, easy-to-use package.

(Note: This is a placeholder image. You can create a GIF showcasing your bot's features.)

✨ Features
🤖 AI Chat: Mention the bot (@Gemini Multi-Tool) with any question to get an intelligent, conversational response powered by Google's Gemini Pro model.

💱 Currency Exchange:

Get real-time exchange rates for over 30 currencies.

Convert any amount between currencies (e.g., !usd 150 myr).

View historical performance graphs for any currency pair.

✨ Daily Horoscopes:

Register your zodiac sign (!reg) to receive a personalized horoscope via DM every day.

Fetch your horoscope on-demand at any time.

Fully automated daily delivery.

Modular & Scalable: Built with discord.py Cogs, making it easy to add new features or manage existing ones.

📂 Project Structure
The project is organized into a modular structure for clarity and maintainability:

your-bot-project/
│
├── .env                 # For storing your secret API keys and tokens
├── requirements.txt     # Lists all Python dependencies
├── run.py               # The main entry point to start the bot
│
└── src/
    ├── config.py        # Central configuration for bot settings
    └── cogs/            # Each major feature is a "Cog"
        ├── ai_chat.py   # Handles the Gemini AI mentions
        ├── currency.py  # Handles all currency commands
        └── horoscope.py # Handles horoscope commands & the daily task

🚀 Setup and Installation
Follow these steps to get the bot running on your own server.

1. Prerequisites
Python 3.8 or newer

A Discord Bot Token

A Google Gemini API Key

2. Clone the Repository
Clone this project to your local machine:

git clone <your-repository-url>
cd your-bot-project

3. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

4. Install Dependencies
Install all the required Python packages from requirements.txt:

pip install -r requirements.txt

5. Configure Environment Variables
Create a file named .env in the root of your project directory. This file will hold your secret credentials. Never share this file or commit it to version control.

Copy the following into your .env file and replace the placeholder values with your actual credentials:

# .env

# Your Discord bot's unique token
DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN"

# Your API key from Google AI Studio
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Your personal Discord User ID (optional, for owner-only commands like !test)
BOT_OWNER_ID="YOUR_DISCORD_USER_ID"

import discord
from discord.ext import commands
import os
import asyncio
import google.generativeai as genai

# Import settings and credentials from our config file
from src import config

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=config.intents,
            help_command=None, # We use a custom help command in a cog
            owner_id=config.BOT_OWNER_ID
        )
        self.gemini_model = None

    async def setup_hook(self):
        """This is called once when the bot logs in."""
        # --- Load Cogs ---
        print("Loading cogs...")
        # The loop will automatically find and load the new general.py cog
        for filename in os.listdir('./src/cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'src.cogs.{filename[:-3]}')
                    print(f'  - Loaded {filename}')
                except Exception as e:
                    print(f'  - Failed to load {filename}: {e}')
        print("Cogs loaded.")

        # --- Configure Gemini API ---
        if config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(config.DEFAULT_GEMINI_MODEL)
                print(f"Successfully initialized Gemini model: {config.DEFAULT_GEMINI_MODEL}")
            except Exception as e:
                print(f"CRITICAL: Failed to initialize Gemini model: {e}")
        else:
            print("Warning: GEMINI_API_KEY not found. AI features are disabled.")
            
    async def on_ready(self):
        """Event fired when the bot is ready."""
        print('------')
        print(f'Bot is ready! Logged in as {self.user.name}')
        print(f"Command Prefix: '{config.COMMAND_PREFIX}' | Mention: @{self.user.name}")
        print('------')

    async def on_message(self, message: discord.Message):
        # Ignore all messages from the bot itself
        if message.author == self.user:
            return

        # --- FIX: Explicitly handle and block all DMs ---
        # If the message is a DM, send a reply and stop all further processing.
        if isinstance(message.channel, discord.DMChannel):
            try:
                await message.channel.send("Sorry, I only operate in server channels. Please interact with me there!")
            except discord.errors.Forbidden:
                # This can happen if the user has DMs disabled for non-friends.
                print(f"Could not send DM reply to {message.author.name}")
            return # Stop any other on_message events or commands from running.
            
        # If not a DM, process commands as usual.
        # The other on_message listeners in the cogs will still run.
        await self.process_commands(message)
        
    # The help command has been moved to src/cogs/general.py


async def main():
    bot = MyBot()
    try:
        await bot.start(config.DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("FATAL ERROR: Invalid Discord bot token. Please check your .env file.")
    except Exception as e:
        print(f"An unexpected error occurred while starting the bot: {e}")

if __name__ == '__main__':
    # Using asyncio.run() is the modern way to start an async program.
    asyncio.run(main())

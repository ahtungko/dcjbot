import discord
from discord.ext import commands
import time
import asyncio

# Import config variables and the Gemini model from the bot instance
from src.config import MIN_GEMINI_DELAY

class AIChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_gemini_call_time = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # --- FIX: Explicitly ignore all messages in DMs ---
        if isinstance(message.channel, discord.DMChannel):
            return

        # Ignore messages from the bot itself or if it's not a mention
        if message.author == self.bot.user or not self.bot.user.mentioned_in(message):
            return
        
        # Check if the AI model is available (it's attached to the bot instance in run.py)
        if not hasattr(self.bot, 'gemini_model') or self.bot.gemini_model is None:
            await message.reply("My AI brain is currently offline. Please try again later.")
            return

        user_message = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
        if not user_message:
            await message.reply("Hello! Mention me with a question to get an AI response.")
            return

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_gemini_call_time < MIN_GEMINI_DELAY:
            remaining = MIN_GEMINI_DELAY - (current_time - self.last_gemini_call_time)
            await message.reply(f"I'm thinking... please wait {remaining:.1f}s before asking again.", delete_after=5)
            return

        try:
            async with message.channel.typing():
                print(f"Sending prompt to Gemini from {message.author}: '{user_message}'")
                
                # Access the model from the bot instance
                response = await self.bot.gemini_model.generate_content_async(user_message)
                ai_response_text = response.text
                self.last_gemini_call_time = time.time()

                # Handle long messages
                if len(ai_response_text) > 2000:
                    chunks = [ai_response_text[i:i + 1990] for i in range(0, len(ai_response_text), 1990)]
                    for i, chunk in enumerate(chunks):
                        if i == 0: await message.reply(chunk)
                        else: await message.channel.send(chunk)
                        await asyncio.sleep(1)
                else:
                    await message.reply(ai_response_text)

        except Exception as e:
            print(f"Error processing Gemini prompt: {e}")
            await message.reply("I'm sorry, I encountered an error while trying to think.")

async def setup(bot: commands.Bot):
    await bot.add_cog(AIChatCog(bot))

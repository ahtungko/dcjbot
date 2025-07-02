import discord
from discord.ext import commands, tasks
from discord import ui
import requests
import json
import os
import datetime

# Import config variables
from src.config import USER_DATA_FILE, COMMAND_PREFIX

# --- Helper Functions for Horoscope ---

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

async def fetch_and_send_horoscope(destination, sign: str, user: discord.User = None):
    url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign.capitalize()}&day=TODAY"
    try:
        # Send a "thinking" message only if the destination is a channel
        if isinstance(destination, (discord.TextChannel, commands.Context)):
            mention_text = f"{user.mention}, " if user else ""
            await destination.send(f"{mention_text}fetching today's horoscope for **{sign}**...")

        response = requests.get(url)
        response.raise_for_status()
        horoscope_data = response.json()

        if horoscope_data.get('success') and 'data' in horoscope_data:
            data = horoscope_data['data']
            horoscope_text = data.get('horoscope_data', 'No horoscope data found.')
            embed = discord.Embed(
                title=f"✨ Daily Horoscope for {sign} ✨",
                description=horoscope_text,
                color=discord.Color.purple()
            )
            embed.set_footer(text=f"Date: {data.get('date')}")
            # If the original destination was a context, use its channel
            if isinstance(destination, commands.Context):
                await destination.channel.send(embed=embed)
            else: # Otherwise, send to the user/channel directly
                await destination.send(embed=embed)
        else:
            await destination.send("Sorry, I couldn't retrieve the horoscope right now.")
            
    except Exception as e:
        print(f"Horoscope fetch error for {sign}: {e}")
        await destination.send("Sorry, there was an error connecting to the horoscope service.")


# --- UI Components for Horoscope ---

class ZodiacSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Aries", emoji="♈"), discord.SelectOption(label="Taurus", emoji="♉"),
            discord.SelectOption(label="Gemini", emoji="♊"), discord.SelectOption(label="Cancer", emoji="♋"),
            discord.SelectOption(label="Leo", emoji="♌"), discord.SelectOption(label="Virgo", emoji="♍"),
            discord.SelectOption(label="Libra", emoji="♎"), discord.SelectOption(label="Scorpio", emoji="♏"),
            discord.SelectOption(label="Sagittarius", emoji="♐"), discord.SelectOption(label="Capricorn", emoji="♑"),
            discord.SelectOption(label="Aquarius", emoji="♒"), discord.SelectOption(label="Pisces", emoji="♓"),
        ]
        super().__init__(placeholder="Choose your zodiac sign...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        selected_sign = self.values[0]
        users = load_user_data()
        is_update = user_id in users
        users[user_id] = selected_sign
        save_user_data(users)
        
        confirmation_message = f"✅ Your sign is updated to **{selected_sign}**!" if is_update else f"✅ Your sign is registered as **{selected_sign}**!"
        await interaction.response.edit_message(content=confirmation_message, view=None)
        await fetch_and_send_horoscope(interaction.channel, selected_sign, user=interaction.user)

class ZodiacSelectionView(ui.View):
    def __init__(self, author: discord.User, *, timeout=120):
        super().__init__(timeout=timeout)
        self.author = author
        self.add_item(ZodiacSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("This menu is not for you.", ephemeral=True)
            return False
        return True

# --- Main Cog Class ---

class HoroscopeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Start the background task when the cog is loaded
        self.send_daily_horoscopes.start()

    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.send_daily_horoscopes.cancel()

    # Note: Decorator changes from @bot.command to @commands.command
    @commands.command(name='reg', help="Register for daily horoscopes or see your current one.")
    async def reg(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        users = load_user_data()
        if user_id in users:
            sign = users[user_id]
            await fetch_and_send_horoscope(ctx, sign, user=ctx.author)
            await ctx.send(f"*(Tip: Use `{COMMAND_PREFIX}mod` to update your sign.)*", delete_after=20)
        else:
            view = ZodiacSelectionView(author=ctx.author)
            await ctx.send(f"Welcome, {ctx.author.mention}! Please select your sign to register:", view=view)

    @commands.command(name='mod', help="Modify your registered zodiac sign.")
    async def mod(self, ctx: commands.Context):
        view = ZodiacSelectionView(author=ctx.author)
        await ctx.send(f"{ctx.author.mention}, please select your new sign:", view=view)

    @commands.command(name='remove', help="Remove your horoscope registration.")
    async def remove_record(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        users = load_user_data()
        if user_id in users:
            del users[user_id]
            save_user_data(users)
            await ctx.send(f"✅ Your record has been deleted. Use `{COMMAND_PREFIX}reg` to register again.")
        else:
            await ctx.send(f"You don't have a registered sign to delete.")

    @commands.command(name='test')
    @commands.is_owner()
    async def test_daily_horoscopes(self, ctx: commands.Context):
        await ctx.message.add_reaction('🧪')
        owner_id = str(ctx.author.id)
        users = load_user_data()
        if owner_id in users:
            sign = users[owner_id]
            await ctx.author.send(f"✅ Running a test for your sign: **{sign}**.")
            await fetch_and_send_horoscope(ctx.author, sign, user=ctx.author)
        else:
            await ctx.author.send(f"⚠️ You are not registered. Use `{COMMAND_PREFIX}reg` first.")

    # Note: Decorator changes from @tasks.loop to @tasks.loop
    # Define the time for the task to run (UTC)
    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
    async def send_daily_horoscopes(self):
        print(f"[{datetime.datetime.now()}] Running daily horoscope task...")
        users = load_user_data()
        if not users:
            return

        for user_id, sign in users.items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                if user:
                    print(f"Sending horoscope to {user.name} for sign {sign}")
                    await fetch_and_send_horoscope(user, sign)
            except (discord.NotFound, discord.Forbidden) as e:
                print(f"Cannot send horoscope to user {user_id}: {e}")
            except Exception as e:
                print(f"An error occurred processing user {user_id}: {e}")
        print("Daily horoscope task finished.")
        
    @send_daily_horoscopes.before_loop
    async def before_daily_task(self):
        await self.bot.wait_until_ready() # Wait for the bot to be ready before starting the loop

async def setup(bot: commands.Bot):
    await bot.add_cog(HoroscopeCog(bot))
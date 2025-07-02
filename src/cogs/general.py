import discord
from discord.ext import commands
from src import config

class GeneralCog(commands.Cog):
    """
    Handles general-purpose commands like help.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Shows the main help embed with all commands."""
        # The title will dynamically use your bot's name, e.g., "JenBot Help"
        embed = discord.Embed(
            title=f"{self.bot.user.name} Help",
            description="This bot provides AI Chat, Currency Exchange, and Horoscope functionalities.",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="🤖 AI Chat Functionality",
            # The mention will also be dynamic to your bot's name
            value=f"To chat with the AI, simply mention the bot (`@{self.bot.user.name}`) followed by your question.",
            inline=False
        )
        embed.add_field(
            name=f"💱 Currency Exchange (Prefix: `{config.COMMAND_PREFIX}`)",
            value=(
                f"**Get all rates for a currency:** `{config.COMMAND_PREFIX}usd`\n"
                f"**Get rates for a specific amount:** `{config.COMMAND_PREFIX}usd100` or `{config.COMMAND_PREFIX}usd 100`\n"
                f"**Convert to a specific currency:** `{config.COMMAND_PREFIX}usd myr`\n"
                f"**Convert a specific amount:** `{config.COMMAND_PREFIX}usd100 myr` or `{config.COMMAND_PREFIX}usd 100 myr`\n\n"
                f"Click `📈` on conversions to see a history graph."
            ),
            inline=False
        )
        embed.add_field(
            name=f"✨ Daily Horoscope (Prefix: `{config.COMMAND_PREFIX}`)",
            value=(
                f"**Register your sign:** `{config.COMMAND_PREFIX}reg`\n"
                f"**Modify your sign:** `{config.COMMAND_PREFIX}mod`\n"
                f"**Remove your record:** `{config.COMMAND_PREFIX}remove`\n\n"
                f"Once registered, you will automatically receive your horoscope via DM every day!"
            ),
            inline=False
        )
        embed.set_footer(text="Made with ❤️ by Jenny")
        await ctx.send(embed=embed)

# This setup function is required by discord.py to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))

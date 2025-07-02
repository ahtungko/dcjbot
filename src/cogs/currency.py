import discord
from discord.ext import commands
from discord import ui
import requests
import json
import re
import asyncio
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import config variables
from src.config import COMMAND_PREFIX, BASE_CURRENCY_API_URL, HISTORY_CURRENCY_API_URL

# --- Helper Functions for Currency ---

def generate_history_graph(dates: list, rates: list, base_currency: str, target_currency: str, num_days: int):
    """Uses Matplotlib to generate a currency history graph."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    ax.set_title(f"{num_days}-Day History: {base_currency} to {target_currency}", color='white')
    ax.plot(dates, rates, marker='o', linestyle='-', color='cyan')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel(f"Rate (1 {base_currency} = X {target_currency})", color='white')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#444444')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI Components for Currency ---

class HistoricalGraphView(ui.View):
    """A View that holds the button to generate a historical graph."""
    def __init__(self, base_currency: str, target_currency: str, *, timeout=180):
        super().__init__(timeout=timeout)
        self.base_currency = base_currency
        self.target_currency = target_currency

    @ui.button(label="Show History", style=discord.ButtonStyle.primary, emoji="📈")
    async def show_graph(self, interaction: discord.Interaction, button: ui.Button):
        button.disabled = True
        button.label = "Generating Graph..."
        await interaction.response.edit_message(view=self)
        api_url = f"{HISTORY_CURRENCY_API_URL}?base={self.base_currency}&symbols={self.target_currency}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            rates_over_time = data.get('rates', {})
            if not rates_over_time:
                await interaction.followup.send("Sorry, no historical data found.", ephemeral=True)
                return

            sorted_dates = sorted(rates_over_time.keys())
            rates_for_target = [rates_over_time[date][self.target_currency] for date in sorted_dates]
            
            loop = asyncio.get_running_loop()
            graph_buffer = await loop.run_in_executor(None, generate_history_graph, sorted_dates, rates_for_target, self.base_currency, self.target_currency, len(sorted_dates))
            
            graph_file = discord.File(graph_buffer, filename=f"{self.base_currency}-{self.target_currency}_history.png")
            await interaction.followup.send(file=graph_file)
        except Exception as e:
            print(f"Error generating currency graph: {e}")
            await interaction.followup.send("Sorry, an error occurred while creating the graph.", ephemeral=True)

# --- Main Cog Class ---

class CurrencyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself or DMs
        if message.author == self.bot.user or isinstance(message.channel, discord.DMChannel):
            return
        
        # This listener only handles currency commands that are NOT standard commands
        # e.g., "!usd", "!usd100 myr"
        if message.content.startswith(COMMAND_PREFIX):
            ctx = await self.bot.get_context(message)
            # If it's a valid, registered command, let the bot's main processor handle it.
            if ctx.valid:
                return

            await self.handle_currency_command(message)


    async def fetch_exchange_rates(self, base_currency: str, target_currency: str = None):
        params = {'base': base_currency.upper()}
        if target_currency:
            params['to'] = target_currency.upper()
        try:
            response = requests.get(BASE_CURRENCY_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rates from API: {e}")
            return None

    async def handle_currency_command(self, message: discord.Message):
        """Processes flexible currency conversion requests."""
        full_command_parts = message.content[len(COMMAND_PREFIX):].strip().split()
        if not full_command_parts:
            return

        base_currency, amount, target_currency = None, 1.0, None
        first_arg = full_command_parts[0]
        currency_amount_match = re.match(r'^([A-Z]{2,4})(\d*\.?\d*)?$', first_arg, re.IGNORECASE)

        if currency_amount_match:
            base_currency = currency_amount_match.group(1).upper()
            if attached_amount_str := currency_amount_match.group(2):
                try: amount = float(attached_amount_str)
                except ValueError: amount = 1.0
            
            if len(full_command_parts) > 1:
                second_arg = full_command_parts[1]
                if re.match(r'^\d+(\.\d+)?$', second_arg):
                    try:
                        amount = float(second_arg)
                        if len(full_command_parts) > 2:
                            target_currency = full_command_parts[2].upper()
                    except ValueError: pass
                else:
                    target_currency = second_arg.upper()
        else:
            # Not a currency command format we handle here
            return

        status_message = await message.channel.send(f"Fetching exchange rates for **{base_currency}**...")
        rates_data = await self.fetch_exchange_rates(base_currency, target_currency)

        if rates_data and 'rates' in rates_data:
            base = rates_data.get('base')
            date = rates_data.get('date')
            rates = rates_data.get('rates')
            header = f"**Exchange Rates for {amount:.2f} {base} (as of {date}):**\n"

            if target_currency:
                if rate_for_one := rates.get(target_currency):
                    calculated_rate = rate_for_one * amount
                    response_message = header + f"**{amount:.2f} {base} = {calculated_rate:.4f} {target_currency}**"
                    view = HistoricalGraphView(base_currency=base, target_currency=target_currency)
                    await status_message.edit(content=response_message, view=view)
                else:
                    await status_message.edit(content=f"Could not find rate for `{target_currency}`.")
            else:
                # Code to display all rates (unchanged)
                await status_message.edit(content=header)
                rate_lines = [f"  - {currency}: {(rate_val * amount):.4f}" for currency, rate_val in rates.items()]
                current_chunk = ""
                for line in rate_lines:
                    if len(current_chunk) + len(line) + 1 > 1900:
                        await message.channel.send(f"```\n{current_chunk}\n```")
                        current_chunk = line
                    else:
                        current_chunk += "\n" + line
                if current_chunk:
                    await message.channel.send(f"```\n{current_chunk}\n```")
        else:
            await status_message.edit(content=f"Sorry, I couldn't fetch exchange rates for `{base_currency}`.")

# This setup function is required by discord.py to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(CurrencyCog(bot))
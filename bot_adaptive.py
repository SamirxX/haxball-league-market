import discord
from discord.ext import commands
import json
import datetime
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

SHARED_MARKET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared_market.json')

def load_shared_market():
    if os.path.exists(SHARED_MARKET_FILE):
        try:
            with open(SHARED_MARKET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("Error loading shared_market.json:", e)
    return []

async def send_market_embeds(target):
    players = load_shared_market()
    if not players:
        await target.send("⚠️ No player data found in shared market database.")
        return

    total_val = sum(float(p.get("price", 0)) for p in players) / 1000000.0
    chunk_size = 10
    chunks = [players[i:i + chunk_size] for i in range(0, len(players), chunk_size)]
    total_parts = len(chunks)

    for idx, chunk in enumerate(chunks, 1):
        embed = discord.Embed(
            title=f"🏆 SKILL ISSUE PRIM LEAGUE - TRANSFER MARKET (Part {idx}/{total_parts})",
            description=f"Official Collaborative Roster | Total Players: {len(players)}",
            color=discord.Color.gold()
        )
        
        table_str = "```\n#   PLAYER          POS  CLUB            VALUE\n"
        table_str += "------------------------------------------------\n"
        for p in chunk:
            price_fmt = f"€{(float(p.get('price', 0))/1000000.0):.1f}M"
            p_num = p.get('num', idx)
            table_str += f"{p_num:<3} {p.get('name', 'N/A'):<15} {p.get('pos', 'CM'):<4} {p.get('club', 'Free Agent'):<15} {price_fmt:<7}\n"
        table_str += "```"
        embed.add_field(name=f"Players {chunk[0].get('num', 1)} - {chunk[-1].get('num', len(chunk))}", value=table_str, inline=False)
        
        if idx == total_parts:
            if bot.user.avatar:
                embed.set_footer(text=f"Skill Issue Prim League | Live Total Market Value: €{total_val:.1f}M", icon_url=bot.user.avatar.url)
            else:
                embed.set_footer(text=f"Skill Issue Prim League | Live Total Market Value: €{total_val:.1f}M")
            embed.timestamp = datetime.datetime.now()

        await target.send(embed=embed)

@bot.event
async def on_ready():
    print(f"==================================================", flush=True)
    print(f"🤖 Haxball Collaborative Bot online as: {bot.user.name} ({bot.user.id})", flush=True)
    
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                avatar_bytes = f.read()
                await bot.user.edit(avatar=avatar_bytes)
                print("✅ Updated Bot Profile Picture with Server Logo!", flush=True)
        except Exception as e:
            print(f"ℹ️ Bot avatar update note: {e}", flush=True)

    print(f"Connected to {len(bot.guilds)} server(s):", flush=True)
    for g in bot.guilds:
        print(f" - {g.name} (ID: {g.id})", flush=True)
    print(f"==================================================", flush=True)

@bot.command(name='market', aliases=['printmarket', 'postmarket'])
async def print_market_command(ctx):
    await send_market_embeds(ctx)

@bot.command(name='help_league')
async def help_league(ctx):
    embed = discord.Embed(
        title="⚽ Haxball League Commands",
        description="Here are all the available league commands:",
        color=discord.Color.gold()
    )
    embed.add_field(name="📊 !market or !printmarket", value="Prints the live Transfer Market table.", inline=False)
    embed.set_footer(text="Haxball Collaborative League Manager")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    bot.run(TOKEN)

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

def save_shared_market(data):
    try:
        with open(SHARED_MARKET_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving shared_market.json:", e)

def is_leader(user):
    # Check if user has Administrator permission or Leader/Admin role
    if isinstance(user, discord.Member):
        if user.guild_permissions.administrator:
            return True
        role_names = [r.name.lower() for r in user.roles]
        if any(keyword in role_names for keyword in ['leader', 'admin', 'administrator', 'mod', 'manager', 'co-leader']):
            return True
    return False

async def send_market_embeds(target):
    players = load_shared_market()
    if not players:
        await target.send("⚠️ No player data found in market database.")
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

POSITIONS_CONFIG = {
    "ST": {"emoji": "⚽", "name": "ST", "color": discord.Color.red(), "desc": "Striker / Attacker"},
    "CM": {"emoji": "🧙‍♂️", "name": "CM", "color": discord.Color.green(), "desc": "Central Midfielder"},
    "CB": {"emoji": "🧱", "name": "CB", "color": discord.Color.blue(), "desc": "Center Back / Defender"},
    "GK": {"emoji": "🧤", "name": "GK", "color": discord.Color.gold(), "desc": "Goalkeeper"}
}

class PositionButton(discord.ui.Button):
    def __init__(self, pos_key, pos_data):
        super().__init__(
            label=pos_data["name"],
            emoji=pos_data["emoji"],
            style=discord.ButtonStyle.primary,
            custom_id=f"pos_btn_{pos_key}"
        )
        self.pos_key = pos_key
        self.pos_data = pos_data

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role_name = self.pos_data["name"]

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(
                name=role_name,
                color=self.pos_data["color"],
                mentionable=True
            )

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed **{role_name}** position role.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role_name}** ({self.pos_data['emoji']}) position role!", ephemeral=True)

class PositionRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for p_key, p_data in POSITIONS_CONFIG.items():
            self.add_item(PositionButton(p_key, p_data))

async def create_roles_and_teams_auto(guild):
    roles_ch = discord.utils.get(guild.text_channels, name="roles") or \
               discord.utils.get(guild.text_channels, name="position-roles")
    if not roles_ch:
        roles_ch = await guild.create_text_channel("roles")

    for p_key, p_data in POSITIONS_CONFIG.items():
        if not discord.utils.get(guild.roles, name=p_data["name"]):
            await guild.create_role(name=p_data["name"], color=p_data["color"], mentionable=True)

    async for msg in roles_ch.history(limit=10):
        if msg.author == bot.user and msg.embeds and "Select Your Position" in (msg.embeds[0].title or ""):
            break
    else:
        embed = discord.Embed(
            title="⚽ **Select Your Position(s)!**",
            description=(
                "Click the buttons below to choose your Haxball positions (**Select more than one!**):\n\n"
                "⚽ = **ST** (Striker)\n"
                "🧙‍♂️ = **CM** (Central Midfielder)\n"
                "🧱 = **CB** (Center Back / Defender)\n"
                "🧤 = **GK** (Goalkeeper)\n\n"
                "*Click any position button to toggle it on or off.*"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Skill Issue Prim League | Multi-Position Selection")
        view = PositionRoleView()
        await roles_ch.send(embed=embed, view=view)

    teams_ch = discord.utils.get(guild.text_channels, name="teams")
    if not teams_ch:
        teams_ch = await guild.create_text_channel("teams")

    async for msg in teams_ch.history(limit=10):
        if msg.author == bot.user:
            break
    else:
        sample_teams = [
            {"name": "TE FC", "captain": "ibra", "logo": "https://i.imgur.com/8Q9Z5bX.png", "color": discord.Color.purple()},
            {"name": "Petrojet", "captain": "ibra", "logo": "https://i.imgur.com/U03V7K1.png", "color": discord.Color.red()},
            {"name": "Zamalek", "captain": "Zamalek Stats", "logo": "https://i.imgur.com/L7pW9XQ.png", "color": discord.Color.white()},
            {"name": "Ghazl El Mahalla", "captain": "Ghazl Stats", "logo": "https://i.imgur.com/yV9nK3D.png", "color": discord.Color.gold()},
            {"name": "Makkasa", "captain": "ibra", "logo": "https://i.imgur.com/z4D8M1P.png", "color": discord.Color.green()}
        ]
        for t in sample_teams:
            embed = discord.Embed(
                title=f"🛡️ {t['name']}",
                description=f"**Captain:** `{t['captain']}`\n**Status:** Active League Team",
                color=t["color"],
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=t["logo"])
            embed.set_footer(text="Skill Issue Prim League | Official Team Profile")
            await teams_ch.send(embed=embed)

@bot.event
async def on_ready():
    print(f"==================================================", flush=True)
    print(f"🤖 Haxball Collaborative Bot online as: {bot.user.name} ({bot.user.id})", flush=True)
    bot.add_view(PositionRoleView())
    print(f"Connected to {len(bot.guilds)} server(s):", flush=True)
    for g in bot.guilds:
        print(f" - {g.name} (ID: {g.id})", flush=True)
        await create_roles_and_teams_auto(g)
    print(f"==================================================", flush=True)

@bot.event
async def on_member_join(member):
    guild = member.guild
    member_role = discord.utils.get(guild.roles, name="Member") or \
                  discord.utils.get(guild.roles, name="League Player") or \
                  discord.utils.get(guild.roles, name="Free Agent")
    if member_role:
        try:
            await member.add_roles(member_role)
        except Exception:
            pass

    welcome_ch = discord.utils.get(guild.text_channels, name="welcome") or \
                 discord.utils.get(guild.text_channels, name="general") or \
                 discord.utils.get(guild.text_channels, name="chat") or \
                 guild.text_channels[0]

    if welcome_ch:
        msg = f"# ⚽ **WELCOME {member.mention}! I WISH YOU AIN'T A BIG NOOB!** 🔥"
        await welcome_ch.send(msg)

@bot.command(name='market', aliases=['printmarket', 'postmarket'])
async def print_market_command(ctx):
    await send_market_embeds(ctx)

@bot.command(name='addplayer')
async def add_player(ctx, name: str, pos: str, club: str, price: float):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    new_num = len(players) + 1
    new_p = {
        "num": new_num,
        "name": name,
        "pos": pos.upper(),
        "club": club,
        "price": price * 1000000
    }
    players.append(new_p)
    save_shared_market(players)
    await ctx.send(f"✅ Added player **{name}** ({pos.upper()}) to **{club}** for €{price}M!")

@bot.command(name='setprice')
async def set_price(ctx, name: str, new_price: float):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    for p in players:
        if p.get("name", "").lower() == name.lower():
            p["price"] = new_price * 1000000
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Updated **{name}**'s price to €{new_price}M!")
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

@bot.command(name='setclub')
async def set_club(ctx, name: str, *, new_club: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    for p in players:
        if p.get("name", "").lower() == name.lower():
            p["club"] = new_club
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Transferred **{name}** to **{new_club}**!")
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
    bot.run(TOKEN)

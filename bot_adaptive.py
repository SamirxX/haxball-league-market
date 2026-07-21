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
GITHUB_PAGES_URL = "https://samirxx.github.io/haxball-league-market/players_market.html"

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
    if isinstance(user, discord.Member):
        if user.guild_permissions.administrator:
            return True
        role_names = [r.name.lower() for r in user.roles]
        if any(keyword in role_names for keyword in ['leader', 'admin', 'administrator', 'mod', 'manager', 'co-leader', 'owner']):
            return True
    return False

def build_market_embeds():
    players = load_shared_market()
    if not players:
        embed = discord.Embed(
            title="🏆 SKILL ISSUE PRIM LEAGUE - TRANSFER MARKET",
            description="⚠️ No player data found in market database.",
            color=discord.Color.gold()
        )
        return [embed]

    total_val = sum(float(p.get("price", 0)) for p in players) / 1000000.0
    chunk_size = 10
    chunks = [players[i:i + chunk_size] for i in range(0, len(players), chunk_size)]
    total_parts = len(chunks)
    embeds = []

    for idx, chunk in enumerate(chunks, 1):
        embed = discord.Embed(
            title=f"🏆 SKILL ISSUE PRIM LEAGUE - TRANSFER MARKET (Part {idx}/{total_parts})",
            description=f"Official Roster | Total Players: {len(players)}",
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
            if bot.user and bot.user.avatar:
                embed.set_footer(text=f"Skill Issue Prim League | Live Total Market Value: €{total_val:.1f}M", icon_url=bot.user.avatar.url)
            else:
                embed.set_footer(text=f"Skill Issue Prim League | Live Total Market Value: €{total_val:.1f}M")
            embed.timestamp = datetime.datetime.now()
        embeds.append(embed)
    return embeds

async def update_unified_market_channel(guild):
    # Single #market channel for everyone
    market_ch = discord.utils.get(guild.text_channels, name="market") or \
                discord.utils.get(guild.text_channels, name="transfer-market")
    if not market_ch:
        market_ch = await guild.create_text_channel("market")

    embeds = build_market_embeds()

    # Clean old bot messages and re-post clean link + market
    async for msg in market_ch.history(limit=20):
        if msg.author == bot.user:
            try:
                await msg.delete()
            except Exception:
                pass

    # Post link header
    header_msg = f"🌐 **LIVE INTERACTIVE MARKET WEB LINK:**\n<{GITHUB_PAGES_URL}>\n\n*(Passcode for Leaders: `PRIM-LEADER-2026`)*\n👇 **LIVE TRANSFER MARKET TABLE (Auto-Refreshes Below):**"
    await market_ch.send(header_msg)

    # Post embedded tables
    for emb in embeds:
        await market_ch.send(embed=emb)

async def setup_leader_headquarters(guild):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
    }
    for role in guild.roles:
        if any(k in role.name.lower() for k in ['leader', 'admin', 'administrator', 'mod', 'manager', 'co-leader', 'owner']):
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)

    cat = discord.utils.get(guild.categories, name="👑 LEADER HEADQUARTERS")
    if not cat:
        cat = await guild.create_category("👑 LEADER HEADQUARTERS", overwrites=overwrites)

    # 1. #leader-commands
    cmd_ch = discord.utils.get(guild.text_channels, name="leader-commands")
    if not cmd_ch:
        cmd_ch = await guild.create_text_channel("leader-commands", category=cat, sync_permissions=True)
    else:
        await cmd_ch.edit(category=cat, sync_permissions=True)

    # 2. #leader-commands-list (Manual)
    guide_ch = discord.utils.get(guild.text_channels, name="leader-commands-list")
    if not guide_ch:
        guide_ch = await guild.create_text_channel("leader-commands-list", category=cat, sync_permissions=True)
    else:
        await guide_ch.edit(category=cat, sync_permissions=True)

    # Post updated guide
    async for msg in guide_ch.history(limit=5):
        if msg.author == bot.user:
            break
    else:
        embed = discord.Embed(
            title="👑 **OFFICIAL LEADER & ADMIN COMMANDS MANUAL**",
            description="Use these commands in `#leader-commands` to update the market 24/7. All changes automatically update `#market`!",
            color=0x9B59B6
        )
        embed.add_field(name="1️⃣ `!addplayer <Name> <Pos> <Club> <PriceInM>`", value="Add a player to the market. Example: `!addplayer Ronaldo ST Zamalek 15`", inline=False)
        embed.add_field(name="2️⃣ `!setprice <PlayerName> <NewPriceInM>`", value="Update player price. Example: `!setprice ibra 20`", inline=False)
        embed.add_field(name="3️⃣ `!setclub <PlayerName> <NewClub>`", value="Transfer player to club. Example: `!setclub Messi Petrojet`", inline=False)
        embed.add_field(name="4️⃣ `!createteam <TeamName> <CaptainName>`", value="Create team card & private team chat channel! Example: `!createteam RealMadrid Samir`", inline=False)
        embed.add_field(name="5️⃣ `!market`", value="Manually print current market table.", inline=False)
        embed.set_footer(text="Leader Passcode Key for Web Page: PRIM-LEADER-2026")
        await guide_ch.send(embed=embed)

POSITIONS_CONFIG = {
    "ST": {"emoji": "⚽", "name": "ST", "color": discord.Color.red()},
    "CM": {"emoji": "🧙‍♂️", "name": "CM", "color": discord.Color.green()},
    "CB": {"emoji": "🧱", "name": "CB", "color": discord.Color.blue()},
    "GK": {"emoji": "🧤", "name": "GK", "color": discord.Color.gold()}
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
            role = await guild.create_role(name=role_name, color=self.pos_data["color"], mentionable=True)

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

async def setup_roles_and_teams(guild):
    # Roles channel with multi-selection
    roles_ch = discord.utils.get(guild.text_channels, name="roles")
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
            description="Click the buttons below to pick your positions (**You can select more than one!**):\n\n⚽ = **ST**\n🧙‍♂️ = **CM**\n🧱 = **CB**\n🧤 = **GK**",
            color=discord.Color.gold()
        )
        await roles_ch.send(embed=embed, view=PositionRoleView())

    # Teams public channel
    teams_ch = discord.utils.get(guild.text_channels, name="teams")
    if not teams_ch:
        teams_ch = await guild.create_text_channel("teams")

@bot.event
async def on_ready():
    print(f"🤖 Bot online as: {bot.user.name}", flush=True)
    bot.add_view(PositionRoleView())
    for g in bot.guilds:
        await setup_leader_headquarters(g)
        await setup_roles_and_teams(g)
        await update_unified_market_channel(g)
    print("✅ Initialization complete!", flush=True)

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
                 guild.text_channels[0]

    if welcome_ch:
        msg = f"# ⚽ **WELCOME {member.mention}! I WISH YOU AIN'T A BIG NOOB!** 🔥"
        await welcome_ch.send(msg)

@bot.command(name='market', aliases=['printmarket', 'postmarket'])
async def print_market_command(ctx):
    embeds = build_market_embeds()
    for emb in embeds:
        await ctx.send(embed=emb)

@bot.command(name='createteam')
async def create_team(ctx, team_name: str, captain: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only Leaders/Admins can create teams!")
        return

    guild = ctx.guild

    # 1. Create Team Role
    team_role = discord.utils.get(guild.roles, name=team_name)
    if not team_role:
        team_role = await guild.create_role(name=team_name, color=discord.Color.blue(), mentionable=True)

    # 2. Create Private Team Channel
    cat = discord.utils.get(guild.categories, name="🛡️ TEAM CHANNELS")
    if not cat:
        cat = await guild.create_category("🛡️ TEAM CHANNELS")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
        team_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
    }

    chan_name = f"💬-{team_name.lower().replace(' ', '-')}"
    team_ch = discord.utils.get(guild.text_channels, name=chan_name)
    if not team_ch:
        team_ch = await guild.create_text_channel(chan_name, category=cat, overwrites=overwrites)

    # 3. Post Team Card in #teams
    teams_ch = discord.utils.get(guild.text_channels, name="teams")
    if teams_ch:
        embed = discord.Embed(
            title=f"🛡️ {team_name}",
            description=f"**Captain:** `{captain}`\n**Role:** {team_role.mention}\n**Private Chat:** {team_ch.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Skill Issue Prim League | Registered Team Profile")
        await teams_ch.send(embed=embed)

    await ctx.send(f"✅ Team **{team_name}** created! Role {team_role.mention} & Private Channel {team_ch.mention} ready!")

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
    await update_unified_market_channel(ctx.guild)

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
        await update_unified_market_channel(ctx.guild)
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
        await update_unified_market_channel(ctx.guild)
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
    bot.run(TOKEN)

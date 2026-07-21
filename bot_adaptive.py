import discord
from discord.ext import commands, tasks
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

# Track file last modified time for auto-syncing HTML -> Discord
last_file_mtime = 0

def load_shared_market():
    if os.path.exists(SHARED_MARKET_FILE):
        try:
            with open(SHARED_MARKET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("Error loading shared_market.json:", e)
    return []

def save_shared_market(data):
    global last_file_mtime
    try:
        with open(SHARED_MARKET_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        last_file_mtime = os.path.getmtime(SHARED_MARKET_FILE)
    except Exception as e:
        print("Error saving shared_market.json:", e)

def format_price(raw_price):
    p = float(raw_price)
    if p < 1000:
        return f"€{p:.1f}M"
    else:
        return f"€{(p/1000000.0):.1f}M"

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

    total_val = 0.0
    for p in players:
        p_val = float(p.get("price", 0))
        total_val += p_val if p_val < 1000 else (p_val / 1000000.0)

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
            price_fmt = format_price(p.get('price', 0))
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
    transfer_cat = discord.utils.get(guild.categories, name="▬▬▬ Transfer Hub ▬▬▬")
    
    # Stylized market channel name
    market_ch = discord.utils.get(guild.text_channels, name="『🛒』transfer-market") or \
                discord.utils.get(guild.text_channels, name="『🛒』market") or \
                discord.utils.get(guild.text_channels, name="market")
    
    if not market_ch:
        market_ch = await guild.create_text_channel("『🛒』transfer-market", category=transfer_cat)
    else:
        if market_ch.name != "『🛒』transfer-market" or (transfer_cat and market_ch.category != transfer_cat):
            await market_ch.edit(name="『🛒』transfer-market", category=transfer_cat)

    embeds = build_market_embeds()

    # Clean old bot messages
    async for msg in market_ch.history(limit=20):
        if msg.author == bot.user:
            try:
                await msg.delete()
            except Exception:
                pass

    header_msg = f"🌐 **LIVE INTERACTIVE MARKET WEB LINK:**\n<{GITHUB_PAGES_URL}>\n\n👇 **LIVE TRANSFER MARKET TABLE (Auto-Refreshes on Web Edit):**"
    await market_ch.send(header_msg)

    for emb in embeds:
        await market_ch.send(embed=emb)

@tasks.loop(seconds=3)
async def check_file_changes_and_sync():
    global last_file_mtime
    if os.path.exists(SHARED_MARKET_FILE):
        current_mtime = os.path.getmtime(SHARED_MARKET_FILE)
        if last_file_mtime == 0:
            last_file_mtime = current_mtime
        elif current_mtime > last_file_mtime:
            print("⚡ Detected file update (HTML/Backend edit)! Syncing Discord market...", flush=True)
            last_file_mtime = current_mtime
            for g in bot.guilds:
                try:
                    await update_unified_market_channel(g)
                except Exception as e:
                    print("Error auto-syncing Discord:", e)

async def organize_server_structure(guild):
    general_cat = discord.utils.get(guild.categories, name="▬▬▬ General ▬▬▬")
    transfer_cat = discord.utils.get(guild.categories, name="▬▬▬ Transfer Hub ▬▬▬")
    league_cat = discord.utils.get(guild.categories, name="▬▬▬ Premier League ▬▬▬")

    welcome_ch = discord.utils.get(guild.text_channels, name="『👋』welcome") or discord.utils.get(guild.text_channels, name="welcome")
    if welcome_ch and general_cat and welcome_ch.category != general_cat:
        await welcome_ch.edit(name="『👋』welcome", category=general_cat)

    roles_ch = discord.utils.get(guild.text_channels, name="『👀』roles") or discord.utils.get(guild.text_channels, name="roles")
    if roles_ch and general_cat and roles_ch.category != general_cat:
        await roles_ch.edit(name="『👀』roles", category=general_cat)

    teams_ch = discord.utils.get(guild.text_channels, name="『🛡️』teams") or discord.utils.get(guild.text_channels, name="teams")
    if teams_ch and league_cat and teams_ch.category != league_cat:
        await teams_ch.edit(name="『🛡️』teams", category=league_cat)

    results_ch = discord.utils.get(guild.text_channels, name="『📈』results") or discord.utils.get(guild.text_channels, name="results")
    if results_ch:
        async for msg in results_ch.history(limit=5):
            if msg.author == bot.user:
                break
        else:
            emb = discord.Embed(
                title="🏆 **OFFICIAL MATCH RESULTS ANNOUNCEMENTS**",
                description="Post official league match scores & results in this channel!\n\n**Format Example:**\n`TE FC 3 - 1 Petrojet`\n⚽ Goals: ibra (2), PlayerX (1)\n🧤 Clean Sheet: WallKeeper",
                color=discord.Color.green()
            )
            await results_ch.send(embed=emb)

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

    cmd_ch = discord.utils.get(guild.text_channels, name="leader-commands")
    if not cmd_ch:
        cmd_ch = await guild.create_text_channel("leader-commands", category=cat, sync_permissions=True)

    guide_ch = discord.utils.get(guild.text_channels, name="leader-commands-list")
    if not guide_ch:
        guide_ch = await guild.create_text_channel("leader-commands-list", category=cat, sync_permissions=True)

    async for msg in guide_ch.history(limit=5):
        if msg.author == bot.user:
            break
    else:
        embed = discord.Embed(
            title="👑 **OFFICIAL LEADER & ADMIN COMMANDS MANUAL**",
            description="Use these commands in `#leader-commands` or edit the HTML page. All changes automatically update `#『🛒』transfer-market`!",
            color=0x9B59B6
        )
        embed.add_field(name="1️⃣ `!addplayer <Name> <Pos> <Club> <PriceInM>`", value="Add a player. Example: `!addplayer Ronaldo ST Zamalek 15`", inline=False)
        embed.add_field(name="2️⃣ `!setprice <PlayerName> <NewPriceInM>`", value="Update player price. Example: `!setprice ibra 20`", inline=False)
        embed.add_field(name="3️⃣ `!setclub <PlayerName> <NewClub>`", value="Transfer player to club. Example: `!setclub Messi Petrojet`", inline=False)
        embed.add_field(name="4️⃣ `!createteam <TeamName> <Captain>`", value="Create team, role, private team chat, and post announcement!", inline=False)
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
    roles_ch = discord.utils.get(guild.text_channels, name="『👀』roles") or discord.utils.get(guild.text_channels, name="roles")
    if roles_ch:
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

@bot.event
async def on_ready():
    print(f"🤖 Bot online as: {bot.user.name}", flush=True)
    bot.add_view(PositionRoleView())
    for g in bot.guilds:
        await organize_server_structure(g)
        await setup_leader_headquarters(g)
        await setup_roles_and_teams(g)
        await update_unified_market_channel(g)
    if not check_file_changes_and_sync.is_running():
        check_file_changes_and_sync.start()
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

    welcome_ch = discord.utils.get(guild.text_channels, name="『👋』welcome") or \
                 discord.utils.get(guild.text_channels, name="『💬』general") or \
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

    team_role = discord.utils.get(guild.roles, name=team_name)
    if not team_role:
        team_role = await guild.create_role(name=team_name, color=discord.Color.blue(), mentionable=True)

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

    teams_ch = discord.utils.get(guild.text_channels, name="『🛡️』teams") or discord.utils.get(guild.text_channels, name="teams")
    if teams_ch:
        embed = discord.Embed(
            title=f"🛡️ NEW TEAM REGISTERED: {team_name}",
            description=f"**Captain:** `{captain}`\n**Role:** {team_role.mention}\n**Private Chat:** {team_ch.mention}",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Skill Issue Prim League | New Team Announcement")
        await teams_ch.send(embed=embed)

    gen_ch = discord.utils.get(guild.text_channels, name="『💬』general") or discord.utils.get(guild.text_channels, name="general")
    if gen_ch:
        announcement = f"🎉 ⚽ **NEW TEAM JOINED THE LEAGUE!** ⚽ 🎉\nWelcome **{team_name}** to **Skill Issue Premier League**! Captained by `{captain}`! {team_role.mention}"
        await gen_ch.send(announcement)

    await ctx.send(f"✅ Team **{team_name}** created! Role {team_role.mention}, Announcement sent in {gen_ch.mention}, & Private Chat {team_ch.mention} ready!")

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
        "price": price if price < 1000 else (price * 1000000)
    }
    players.append(new_p)
    save_shared_market(players)
    await ctx.send(f"✅ Added player **{name}** ({pos.upper()}) to **{club}** for {format_price(price)}!")
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
            p["price"] = new_price if new_price < 1000 else (new_price * 1000000)
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Updated **{name}**'s price to {format_price(new_price)}!")
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

@bot.command(name='removeplayer', aliases=['delplayer', 'deleteplayer'])
async def remove_player(ctx, *, name: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    initial_len = len(players)
    players = [p for p in players if p.get("name", "").lower() != name.lower()]
    if len(players) < initial_len:
        save_shared_market(players)
        await ctx.send(f"🗑️ Removed player **{name}** from the market!")
        await update_unified_market_channel(ctx.guild)
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
    bot.run(TOKEN)

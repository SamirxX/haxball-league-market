import discord
from discord.ext import commands, tasks
import json
import datetime
import os
import sys
from github import Github
import asyncio
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

SHARED_MARKET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared_market.json')
GITHUB_PAGES_URL = "https://samirxx.github.io/haxball-league-market/players_market.html"
GITHUB_REPO = "SamirxX/haxball-league-market"

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
    try:
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        with open(SHARED_MARKET_FILE, 'w', encoding='utf-8') as f:
            f.write(json_content)
            
        # Background sync to GitHub if token is present
        gh_token = os.environ.get("GITHUB_TOKEN")
        if gh_token:
            asyncio.create_task(sync_to_github(json_content, gh_token))
            
    except Exception as e:
        print("Error saving shared_market.json:", e)

async def sync_to_github(json_content, token):
    try:
        g = Github(token)
        repo = g.get_repo(GITHUB_REPO)
        contents = repo.get_contents(SHARED_MARKET_FILE)
        # We need to run blocking PyGithub calls in executor, but for simplicity here we just call it
        # as it's a small file and not frequently updated
        repo.update_file(contents.path, "Bot auto-update market data", json_content, contents.sha)
        print("✅ Synced shared_market.json to GitHub successfully!", flush=True)
    except Exception as e:
        print(f"❌ Error syncing to GitHub: {e}", flush=True)

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

async def deduplicate_and_edit_channel(guild, keywords, exclude_keywords, target_name, target_category):
    found_channels = []
    for ch in guild.text_channels:
        ch_name_lower = ch.name.lower()
        if any(k in ch_name_lower for k in keywords) and not any(ek in ch_name_lower for ek in exclude_keywords):
            found_channels.append(ch)

    if not found_channels:
        return await guild.create_text_channel(target_name, category=target_category)

    main_ch = found_channels[0]
    for duplicate in found_channels[1:]:
        try:
            await duplicate.delete()
        except Exception:
            pass

    if main_ch.name != target_name or (target_category and main_ch.category != target_category):
        try:
            await main_ch.edit(name=target_name, category=target_category)
        except Exception:
            pass
    return main_ch

async def update_unified_market_channel(guild):
    transfer_cat = discord.utils.get(guild.categories, name="▬▬▬ Transfer Hub ▬▬▬")
    if not transfer_cat:
        transfer_cat = await guild.create_category("▬▬▬ Transfer Hub ▬▬▬")
        
    market_ch = await deduplicate_and_edit_channel(guild, ["market"], ["black", "marketing", "rules"], "『🛒』transfer-market", transfer_cat)
    
    embeds = build_market_embeds()

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

async def organize_server_structure(guild):
    general_cat = discord.utils.get(guild.categories, name="▬▬▬ General ▬▬▬")
    if not general_cat: general_cat = await guild.create_category("▬▬▬ General ▬▬▬")
        
    transfer_cat = discord.utils.get(guild.categories, name="▬▬▬ Transfer Hub ▬▬▬")
    if not transfer_cat: transfer_cat = await guild.create_category("▬▬▬ Transfer Hub ▬▬▬")
        
    league_cat = discord.utils.get(guild.categories, name="▬▬▬ Premier League ▬▬▬")
    if not league_cat: league_cat = await guild.create_category("▬▬▬ Premier League ▬▬▬")

    # General
    await deduplicate_and_edit_channel(guild, ["welcome"], [], "『👋』welcome", general_cat)
    await deduplicate_and_edit_channel(guild, ["roles"], ["rules"], "『👀』roles", general_cat)
    await deduplicate_and_edit_channel(guild, ["announcement"], [], "『📌』announcements", general_cat)
    await deduplicate_and_edit_channel(guild, ["rule"], ["transfer"], "『📜』rules", general_cat)

    # Premier League
    await deduplicate_and_edit_channel(guild, ["team"], ["search", "free", "registration", "roles"], "『🛡️』teams", league_cat)
    results_ch = await deduplicate_and_edit_channel(guild, ["result", "fixture"], [], "『📈』results", league_cat)
    await deduplicate_and_edit_channel(guild, ["standing", "leaderboard"], [], "『📊』standings", league_cat)

    # Transfer Hub (market is handled in update_unified_market_channel)
    await deduplicate_and_edit_channel(guild, ["transfer-rule", "transfer_rule"], [], "『📕』transfer-rules", transfer_cat)
    await deduplicate_and_edit_channel(guild, ["search-for", "free-agent"], [], "『👤』search-for-teams", transfer_cat)
    await deduplicate_and_edit_channel(guild, ["transfer"], ["market", "rule"], "『🎯』transfers", transfer_cat)
    await deduplicate_and_edit_channel(guild, ["signing"], [], "『📄』signings", transfer_cat)

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
            description="Use these commands in `#leader-commands`. All changes automatically update `#『🛒』transfer-market` and your GitHub website!",
            color=0x9B59B6
        )
        embed.add_field(name="1️⃣ `!addplayer <Name> <Pos> <Club> <PriceInM>`", value="Add a player. Example: `!addplayer Ronaldo ST Zamalek 15`", inline=False)
        embed.add_field(name="2️⃣ `!setprice <PlayerName> <NewPriceInM>`", value="Update player price. Example: `!setprice ibra 20`", inline=False)
        embed.add_field(name="3️⃣ `!setclub <PlayerName> <NewClub>`", value="Transfer player to club. Example: `!setclub Messi Petrojet`", inline=False)
        embed.add_field(name="4️⃣ `!setname <OldName> <NewName>`", value="Rename a player. Example: `!setname ibra Zlatan`", inline=False)
        embed.add_field(name="5️⃣ `!setpos <PlayerName> <NewPos>`", value="Change player position. Example: `!setpos Messi CAM`", inline=False)
        embed.add_field(name="6️⃣ `!setstatus <PlayerName> <Status>`", value="Change player status. Example: `!setstatus Messi Signed`", inline=False)
        embed.add_field(name="7️⃣ `!removeplayer <PlayerName>`", value="Remove player from market. Example: `!removeplayer Ronaldo`", inline=False)
        embed.add_field(name="8️⃣ `!editplayer <PlayerName> <Column> <NewValue>`", value="Universal edit. Columns: name, pos, club, price, status. Example: `!editplayer ibra price 50`", inline=False)
        embed.add_field(name="9️⃣ `!clearmarket`", value="Wipe ALL players from the market.", inline=False)
        embed.add_field(name="🔟 `!createteam <TeamName> <Captain>`", value="Create team, role, private team chat, and post announcement!", inline=False)
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

@bot.command(name='setname')
async def set_name(ctx, old_name: str, new_name: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    for p in players:
        if p.get("name", "").lower() == old_name.lower():
            p["name"] = new_name
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Renamed **{old_name}** to **{new_name}**!")
        await update_unified_market_channel(ctx.guild)
    else:
        await ctx.send(f"❌ Player **{old_name}** not found.")

@bot.command(name='setpos', aliases=['setposition'])
async def set_pos(ctx, name: str, new_pos: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    for p in players:
        if p.get("name", "").lower() == name.lower():
            p["pos"] = new_pos.upper()
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Changed **{name}**'s position to **{new_pos.upper()}**!")
        await update_unified_market_channel(ctx.guild)
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

@bot.command(name='setstatus')
async def set_status(ctx, name: str, *, new_status: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    for p in players:
        if p.get("name", "").lower() == name.lower():
            p["status"] = new_status
            found = True
            break
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Updated **{name}**'s status to **{new_status}**!")
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

@bot.command(name='editplayer')
async def edit_player(ctx, name: str, column: str, *, new_value: str):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
    players = load_shared_market()
    found = False
    col_lower = column.lower()
    valid_cols = ["name", "pos", "club", "price", "status"]
    
    if col_lower not in valid_cols:
        await ctx.send(f"❌ Invalid column! Valid columns are: {', '.join(valid_cols)}")
        return
        
    for p in players:
        if p.get("name", "").lower() == name.lower():
            if col_lower == "price":
                try:
                    val = float(new_value)
                    p["price"] = val if val < 1000 else (val * 1000000)
                except ValueError:
                    await ctx.send("❌ Price must be a number!")
                    return
            elif col_lower == "pos":
                p["pos"] = new_value.upper()
            else:
                p[col_lower] = new_value
            found = True
            break
            
    if found:
        save_shared_market(players)
        await ctx.send(f"✅ Updated **{name}**'s {column} to **{new_value}**!")
        await update_unified_market_channel(ctx.guild)
    else:
        await ctx.send(f"❌ Player **{name}** not found.")

@bot.command(name='clearmarket')
async def clear_market(ctx):
    if not is_leader(ctx.author):
        await ctx.send("❌ Only League Leaders / Admins can edit the market!")
        return
        
    await ctx.send("⚠️ Are you sure you want to WIPE the entire market? Type `confirm` within 10 seconds.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'
        
    try:
        await bot.wait_for('message', check=check, timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send("❌ Market clear cancelled.")
        return
        
    save_shared_market([])
    await ctx.send("🛑 **MARKET CLEARED SUCCESSFULLY.**")
    await update_unified_market_channel(ctx.guild)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
    bot.run(TOKEN)

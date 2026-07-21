import discord
from discord.ext import commands
import json
import datetime
import os

# Set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# In-memory storage (Can be backed by SQLite/JSON file)
DB_FILE = 'league_data.json'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {
        "teams": {},
        "players": {},
        "matches": []
    }

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

league_db = load_data()

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"⚽ HAXBALL PRIM LEAGUE DISCORD BOT IS ONLINE")
    print(f"Logged in as: {bot.user.name} ({bot.user.id})")
    print(f"Prefix: !")
    print(f"==================================================")
    await bot.change_presence(activity=discord.Game(name="Haxball Prim League | !help"))

@bot.command(name='register')
async def register(ctx, haxball_nick: str):
    """Registers a user as a Free Agent in the league"""
    user_id = str(ctx.author.id)
    fa_role = discord.utils.get(ctx.guild.roles, name="Free Agent")
    
    if user_id in league_db["players"]:
        await ctx.send(f"⚠️ **{ctx.author.display_name}**, you are already registered with nick `{league_db['players'][user_id]['haxball_nick']}`!")
        return

    league_db["players"][user_id] = {
        "discord_name": ctx.author.display_name,
        "haxball_nick": haxball_nick,
        "team": None,
        "registered_at": str(datetime.datetime.now())
    }
    save_data(league_db)

    if fa_role:
        await ctx.author.add_roles(fa_role)

    await ctx.send(f"✅ **{ctx.author.display_name}** registered successfully! Assigned Haxball Nick: `{haxball_nick}`. Role: `@Free Agent`")

@bot.command(name='createteam')
@commands.has_any_role("League Director", "League Admin")
async def create_team(ctx, team_name: str, team_tag: str):
    """Creates a new team in the league"""
    if team_name in league_db["teams"]:
        await ctx.send(f"⚠️ Team **{team_name}** already exists!")
        return

    league_db["teams"][team_name] = {
        "tag": team_tag.upper(),
        "captain": None,
        "mp": 0, "w": 0, "d": 0, "l": 0,
        "gf": 0, "ga": 0, "gd": 0, "pts": 0
    }
    save_data(league_db)

    # Create Discord Role for Team
    guild = ctx.guild
    team_role = await guild.create_role(name=team_name, color=discord.Color.blue(), mentionable=True)
    await ctx.send(f"🏆 Team **{team_name}** [{team_tag.upper()}] created successfully with role {team_role.mention}!")

@bot.command(name='sign')
@commands.has_any_role("Team Captain", "League Director")
async def sign_player(ctx, member: discord.Member):
    """Signs a Free Agent to the Captain's team"""
    user_id = str(member.id)
    if user_id not in league_db["players"]:
        await ctx.send(f"⚠️ {member.mention} is not registered in the league! Ask them to type `!register <haxball_nick>` first.")
        return

    fa_role = discord.utils.get(ctx.guild.roles, name="Free Agent")
    # Identify captain's team role
    captain_roles = [r for r in ctx.author.roles if r.name in league_db["teams"]]
    if not captain_roles and not any(r.name in ["League Director", "League Admin"] for r in ctx.author.roles):
        await ctx.send("⚠️ You must be assigned a Team Role to sign players!")
        return

    team_role = captain_roles[0] if captain_roles else None
    if team_role:
        await member.add_roles(team_role)
        if fa_role in member.roles:
            await member.remove_roles(fa_role)
        league_db["players"][user_id]["team"] = team_role.name
        save_data(league_db)
        await ctx.send(f"📝 **OFFICIAL TRANSFER**: {member.mention} has signed for **{team_role.name}**!")

@bot.command(name='report')
@commands.has_any_role("Team Captain", "League Referee", "League Director")
async def report_match(ctx, home_team: str, home_score: int, vs_arg: str, away_score: int, away_team: str):
    """Submits a match score: !report ApexPredators 3 - 1 ShadowStrikers"""
    if home_team not in league_db["teams"] or away_team not in league_db["teams"]:
        await ctx.send("⚠️ One or both of the team names were not found in the league database!")
        return

    ht = league_db["teams"][home_team]
    at = league_db["teams"][away_team]

    ht["mp"] += 1
    at["mp"] += 1
    ht["gf"] += home_score
    ht["ga"] += away_score
    at["gf"] += away_score
    at["ga"] += home_score

    ht["gd"] = ht["gf"] - ht["ga"]
    at["gd"] = at["gf"] - at["ga"]

    if home_score > away_score:
        ht["w"] += 1
        ht["pts"] += 3
        at["l"] += 1
    elif away_score > home_score:
        at["w"] += 1
        at["pts"] += 3
        ht["l"] += 1
    else:
        ht["d"] += 1
        at["d"] += 1
        ht["pts"] += 1
        at["pts"] += 1

    match_entry = {
        "home": home_team, "home_score": home_score,
        "away_score": away_score, "away": away_team,
        "reported_by": ctx.author.display_name,
        "time": str(datetime.datetime.now())
    }
    league_db["matches"].append(match_entry)
    save_data(league_db)

    embed = discord.Embed(
        title="⚽ OFFICIAL HAXBALL MATCH REPORT",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Home", value=f"**{home_team}**\nScore: {home_score}", inline=True)
    embed.add_field(name="VS", value="━━━", inline=True)
    embed.add_field(name="Away", value=f"**{away_team}**\nScore: {away_score}", inline=True)
    embed.set_footer(text=f"Reported by {ctx.author.display_name}")

    await ctx.send(embed=embed)

@bot.command(name='standings')
async def standings(ctx):
    """Outputs current league table"""
    sorted_teams = sorted(league_db["teams"].items(), key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]), reverse=True)
    
    table_str = "```\n#  TEAM             MP   W   D   L   GF  GA  GD  PTS\n"
    table_str += "---------------------------------------------------\n"
    for i, (name, t) in enumerate(sorted_teams, 1):
        gd_fmt = f"+{t['gd']}" if t['gd'] > 0 else str(t['gd'])
        table_str += f"{i:<2} {name:<16} {t['mp']:<4} {t['w']:<3} {t['d']:<3} {t['l']:<3} {t['gf']:<3} {t['ga']:<3} {gd_fmt:<4} {t['pts']:<3}\n"
    table_str += "```"

    embed = discord.Embed(title="📊 HAXBALL PRIM LEAGUE STANDINGS", description=table_str, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name='freeagents')
async def free_agents(ctx):
    """Lists available free agents"""
    fa_list = [p["haxball_nick"] for p in league_db["players"].values() if p["team"] is None]
    if not fa_list:
        await ctx.send("ℹ️ No available Free Agents currently registered.")
        return
    
    fa_formatted = "\n".join([f"• {nick}" for nick in fa_list])
    embed = discord.Embed(title="👤 AVAILABLE FREE AGENTS", description=fa_formatted, color=discord.Color.green())
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Replace token with your bot's token from Discord Developer Portal
    TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
    bot.run(TOKEN)

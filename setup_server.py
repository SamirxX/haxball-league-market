import discord
from discord.ext import commands
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

ROLES_TO_CREATE = [
    {"name": "League Director", "color": discord.Color.from_rgb(229, 184, 66), "hoist": True, "admin": True},
    {"name": "League Referee", "color": discord.Color.from_rgb(230, 126, 34), "hoist": True, "admin": False},
    {"name": "Team Captain", "color": discord.Color.from_rgb(52, 152, 219), "hoist": True, "admin": False},
    {"name": "League Player", "color": discord.Color.from_rgb(46, 204, 113), "hoist": True, "admin": False},
    {"name": "Free Agent", "color": discord.Color.from_rgb(149, 165, 166), "hoist": True, "admin": False},
]

CATEGORIES_AND_CHANNELS = [
    {
        "category": "📌 WELCOME & RULES",
        "channels": [
            {"name": "rules", "type": "text", "read_only": True},
            {"name": "announcements", "type": "text", "read_only": True},
            {"name": "information", "type": "text", "read_only": True}
        ]
    },
    {
        "category": "⚽ LEAGUE OPERATIONS",
        "channels": [
            {"name": "standings", "type": "text", "read_only": True},
            {"name": "fixtures-and-results", "type": "text", "read_only": True},
            {"name": "match-reporting", "type": "text", "read_only": False},
            {"name": "haxball-links", "type": "text", "read_only": False}
        ]
    },
    {
        "category": "🔄 TRANSFERS & TEAMS",
        "channels": [
            {"name": "free-agents", "type": "text", "read_only": False},
            {"name": "transfers", "type": "text", "read_only": False},
            {"name": "team-registration", "type": "text", "read_only": False}
        ]
    },
    {
        "category": "🔊 MATCH ROOMS (VOICE)",
        "channels": [
            {"name": "🔊 Match Room 1 (Red)", "type": "voice"},
            {"name": "🔊 Match Room 1 (Blue)", "type": "voice"}
        ]
    }
]

async def build_server(guild):
    print(f"Building Haxball League structure for server: {guild.name} ({guild.id})...", flush=True)
    
    role_map = {}
    for r_data in ROLES_TO_CREATE:
        existing_role = discord.utils.get(guild.roles, name=r_data["name"])
        if not existing_role:
            perms = discord.Permissions(administrator=r_data["admin"]) if r_data["admin"] else discord.Permissions.none()
            new_role = await guild.create_role(
                name=r_data["name"],
                color=r_data["color"],
                hoist=r_data["hoist"],
                permissions=perms,
                mentionable=True
            )
            role_map[r_data["name"]] = new_role
            print(f"  [+] Created Role: {r_data['name']}", flush=True)
        else:
            role_map[r_data["name"]] = existing_role

    for cat_data in CATEGORIES_AND_CHANNELS:
        category = discord.utils.get(guild.categories, name=cat_data["category"])
        if not category:
            category = await guild.create_category(cat_data["category"])
            print(f"  [+] Created Category: {cat_data['category']}", flush=True)

        for ch_data in cat_data["channels"]:
            ch_name = ch_data["name"]
            ch_type = ch_data["type"]
            
            existing_ch = discord.utils.get(guild.channels, name=ch_name, category=category)
            if not existing_ch:
                if ch_type == "text":
                    overwrites = {}
                    if ch_data.get("read_only"):
                        overwrites[guild.default_role] = discord.PermissionOverwrite(send_messages=False, read_messages=True)
                        if "League Director" in role_map:
                            overwrites[role_map["League Director"]] = discord.PermissionOverwrite(send_messages=True)
                    
                    await guild.create_text_channel(ch_name, category=category, overwrites=overwrites)
                    print(f"  [+] Created Text Channel: #{ch_name}", flush=True)
                elif ch_type == "voice":
                    await guild.create_voice_channel(ch_name, category=category, user_limit=4)
                    print(f"  [+] Created Voice Channel: {ch_name}", flush=True)

    print(f"SUCCESS! SERVER SETUP COMPLETE FOR: {guild.name}", flush=True)

@bot.event
async def on_ready():
    print(f"==================================================", flush=True)
    print(f"Bot connected as: {bot.user.name} ({bot.user.id})", flush=True)
    print(f"Connected to {len(bot.guilds)} server(s):", flush=True)
    for g in bot.guilds:
        print(f" - {g.name} (ID: {g.id})", flush=True)
        await build_server(g)
    print(f"==================================================", flush=True)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    bot.run(TOKEN)

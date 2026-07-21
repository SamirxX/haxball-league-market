// Data & State for Haxball Discord League Visualizer

const serverConfig = {
    name: "SKILL ISSUE PRIM LEAGUE",
    categories: [
        {
            name: "📌 WELCOME & RULES",
            channels: [
                {
                    name: "rules",
                    type: "text",
                    desc: "Official competition rules, fair play guidelines, anti-cheat & lag rules.",
                    perms: ["Read Messages", "Send Messages (Disabled)", "Read Message History"],
                    preview: "📜 **HAXBALL PRIM LEAGUE RULES**\n1. 3v3 / 4v4 Official Map: Real Soccer / Big\n2. Match duration: 7 minutes, max 3 goals limit\n3. Both team captains must record or screenshot match end screen.",
                    tip: "Make this channel read-only for all regular roles."
                },
                {
                    name: "announcements",
                    type: "text",
                    desc: "Official league updates, season starts, transfer windows, and rule changes.",
                    perms: ["Read Messages", "Send Messages (Admins Only)", "Mention Everyone"],
                    preview: "📢 **SEASON 1 ANNOUNCEMENT**\nThe transfer window is officially OPEN! Captains have until Friday 23:59 UTC to register squad rosters.",
                    tip: "Use @everyone or @League Player tags sparingly for major announcements."
                },
                {
                    name: "information",
                    type: "text",
                    desc: "Season calendar, point system, prize pool details, and staff contacts.",
                    perms: ["Read Messages", "Send Messages (Disabled)"],
                    preview: "🏆 **SEASON FORMAT & POINTS SYSTEM**\n- Win: 3 PTS | Draw: 1 PT | Loss: 0 PTS\n- Top 4 advance to Champions Playoffs.",
                    tip: "Include links to the Google Sheet / Web Leaderboard here."
                }
            ]
        },
        {
            name: "⚽ LEAGUE OPERATIONS",
            channels: [
                {
                    name: "standings",
                    type: "text",
                    desc: "Live updated league standings posted by the Haxball Discord Bot.",
                    perms: ["Read Messages", "Send Messages (Bot Only)"],
                    preview: "📊 **LIVE DIVISION 1 STANDINGS**\n1. Apex Predators | 12 PTS | +10 GD\n2. Shadow Strikers  |  9 PTS |  +4 GD\n3. Titan FC          |  4 PTS |  -2 GD",
                    tip: "Let the bot auto-pin the current standings table every matchday."
                },
                {
                    name: "fixtures-and-results",
                    type: "text",
                    desc: "Weekly match pairings, fixture schedule, and official referee score confirmations.",
                    perms: ["Read Messages", "Send Messages (Staff Only)"],
                    preview: "🗓️ **WEEK 3 FIXTURES**\nMatch 1: @Apex Predators vs @Shadow Strikers\nMatch 2: @Titan FC vs @Viper United",
                    tip: "Post match times 48 hours in advance to avoid forfeit disputes."
                },
                {
                    name: "match-reporting",
                    type: "text",
                    desc: "Captains command channel for submitting official scores.",
                    perms: ["Read Messages", "Send Messages (Captains Only)"],
                    preview: "User: !report @ApexPredators 3 - 1 @ShadowStrikers\nBot: ✅ **Match Recorded!**\nApex Predators (+3 PTS) def. Shadow Strikers.",
                    tip: "Only allow Team Captains & Referees permission to type here."
                },
                {
                    name: "haxball-links",
                    type: "text",
                    desc: "Headless room links and official match host servers.",
                    perms: ["Read Messages", "Send Messages (Captains & Hosts Only)"],
                    preview: "🌐 **MATCH ROOM OPEN**\nLink: https://www.haxball.com/play?c=xX99aLz\nHost: EU Central #1 (Password: prim2026)",
                    tip: "Use auto-cleaning bot to delete expired room links after 1 hour."
                }
            ]
        },
        {
            name: "🔄 TRANSFERS & TEAMS",
            channels: [
                {
                    name: "free-agents",
                    type: "text",
                    desc: "Unsigned players post their stats, position (GK/DM/ST), and availability.",
                    perms: ["Read Messages", "Send Messages (Free Agents)"],
                    preview: "👤 **FREE AGENT POST**\nNick: HaxGod99\nPosition: Striker / Playmaker\nAvailability: Mon-Fri 18:00-22:00 UTC\nLF Team for Season 1!",
                    tip: "Provide a template pinned post for free agents to format their application."
                },
                {
                    name: "transfers",
                    type: "text",
                    desc: "Official transfer announcements, player signings, and contract releases.",
                    perms: ["Read Messages", "Send Messages (Captains & Admins)"],
                    preview: "📝 **TRANSFER CONFIRMED**\n@Apex Predators have signed @HaxGod99 on a free transfer!",
                    tip: "Require bot command `!sign @player` for verified transfers."
                },
                {
                    name: "team-registration",
                    type: "text",
                    desc: "New team applications and logo submissions for league approval.",
                    perms: ["Read Messages", "Send Messages (Registered Users)"],
                    preview: "🛡️ **NEW TEAM ENTRY**\nTeam Name: Lunar Vipers\nTag: [LV]\nCaptain: @ViperCap\nRoster: @Player1, @Player2, @Player3",
                    tip: "Set minimum squad requirement (e.g. 4 players minimum)."
                }
            ]
        },
        {
            name: "🔊 MATCH ROOMS (VOICE)",
            channels: [
                {
                    name: "🔊 Match Room 1 (Red)",
                    type: "voice",
                    desc: "Red Team private voice channel during match.",
                    perms: ["Connect", "Speak", "Stream"],
                    preview: "[Voice Channel for 3v3 Red Squad]",
                    tip: "Set user limit to 4 to prevent spectator distractions."
                },
                {
                    name: "🔊 Match Room 1 (Blue)",
                    type: "voice",
                    desc: "Blue Team private voice channel during match.",
                    perms: ["Connect", "Speak", "Stream"],
                    preview: "[Voice Channel for 3v3 Blue Squad]",
                    tip: "Set user limit to 4."
                }
            ]
        }
    ]
};

// Initial Teams State for Simulator
let teams = [
    { name: "Apex Predators", tag: "APX", color: "#e5b842", mp: 4, w: 4, d: 0, l: 0, gf: 14, ga: 3, gd: 11, pts: 12 },
    { name: "Shadow Strikers", tag: "STR", color: "#5865f2", mp: 4, w: 3, d: 0, l: 1, gf: 10, ga: 5, gd: 5, pts: 9 },
    { name: "Titan FC", tag: "TTN", color: "#23a55a", mp: 4, w: 1, d: 1, l: 2, gf: 6, ga: 8, gd: -2, pts: 4 },
    { name: "Viper United", tag: "VPR", color: "#f23f43", mp: 4, w: 1, d: 0, l: 3, gf: 5, ga: 11, gd: -6, pts: 3 },
    { name: "Cyber Knights", tag: "KNT", color: "#9b59b6", mp: 4, w: 0, d: 1, l: 3, gf: 3, ga: 11, gd: -8, pts: 1 }
];

let recentMatches = [
    { home: "Apex Predators", homeScore: 4, awayScore: 1, away: "Viper United" },
    { home: "Shadow Strikers", homeScore: 2, awayScore: 1, away: "Titan FC" }
];

// Role Matrix Data
const rolesData = [
    { name: "League Director", color: "#e5b842", hoist: "Yes", perms: "Administrator, Manage Roles, Manage Server", desc: "Full control over league operations, refereeing, and bans." },
    { name: "League Referee", color: "#e67e22", hoist: "Yes", perms: "Manage Messages, Mute Members, Move Members", desc: "Monitors matches, resolves disputes, and verifies scores." },
    { name: "Team Captain", color: "#3498db", hoist: "Yes", perms: "Mention Roles, Manage Team Channels", desc: "Manages squad rosters, signs players, submits match reports." },
    { name: "League Player", color: "#2ecc71", hoist: "Yes", perms: "Send Messages, Connect Voice", desc: "Registered competitive player eligible to play in matches." },
    { name: "Free Agent", color: "#95a5a6", hoist: "Yes", perms: "Send Messages in #free-agents", desc: "Player seeking a team contract for the upcoming season." },
    { name: "Spectator / Fan", color: "#7f8c8d", hoist: "No", perms: "Read Messages, Watch Streams", desc: "Community visitor or casual fan." }
];

// Python Bot Source Code
const pythonBotCode = `import discord
from discord.ext import commands
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Database / In-Memory State
teams = {}
free_agents = []
matches = []

@bot.event
async def on_ready():
    print(f'⚽ Haxball League Bot online as {bot.user.name}')

@bot.command(name='register')
async def register(ctx, haxball_nick: str):
    """Registers a user into the league as a Free Agent"""
    fa_role = discord.utils.get(ctx.guild.roles, name="Free Agent")
    if fa_role:
        await ctx.author.add_roles(fa_role)
    await ctx.send(f"✅ Registered **{ctx.author.display_name}** (Haxball: \`{haxball_nick}\`) as a Free Agent!")

@bot.command(name='report')
@commands.has_any_role("Team Captain", "League Referee", "League Director")
async def report_match(ctx, home_team: str, home_score: int, vs_str: str, away_score: int, away_team: str):
    """Submits a match score: !report @TeamA 3 - 1 @TeamB"""
    embed = discord.Embed(
        title="⚽ OFFICIAL MATCH RESULT",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="Home Team", value=f"{home_team}\n**{home_score}**", inline=True)
    embed.add_field(name="VS", value="━", inline=True)
    embed.add_field(name="Away Team", value=f"{away_team}\n**{away_score}**", inline=True)
    
    if home_score > away_score:
        winner = home_team
    elif away_score > home_score:
        winner = away_team
    else:
        winner = "Draw"
        
    embed.set_footer(text=f"Submitted by {ctx.author.display_name} | Winner: {winner}")
    await ctx.send(embed=embed)

@bot.command(name='standings')
async def standings(ctx):
    """Outputs live league table"""
    table = "```\\n#  TEAM            MP  W  D  L  GF GA GD PTS\\n"
    table += "1. Apex Predators   4   4  0  0  14  3 +11 12\\n"
    table += "2. Shadow Strikers  4   3  0  1  10  5  +5  9\\n"
    table += "3. Titan FC         4   1  1  2   6  8  -2  4\\n```"
    await ctx.send(f"📊 **CURRENT LEAGUE STANDINGS**\\n{table}")

bot.run('YOUR_DISCORD_BOT_TOKEN_HERE')
`;

// App Initialization
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    renderChannelTree();
    renderStandings();
    renderMatchFeed();
    renderRoleMatrix();
    populateMatchFormSelects();
    initBotCodePreview();
    initFormHandlers();
});

// Tab Navigation
function initNavigation() {
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const tabTitles = {
        "discord-preview": { title: "Discord Server Layout Visualizer", sub: "Preview the structure, categories, and channels designed for competitive Haxball leagues" },
        "league-standings": { title: "Live Standings & Match Reporting", sub: "Simulate match submissions and view dynamic points calculation" },
        "bot-commands": { title: "Discord League Bot Commands", sub: "Automated commands for score reporting, roster updates, and standings" },
        "role-matrix": { title: "Roles & Permission Hierarchy", sub: "Configured roles, permission flags, and visibility settings" },
        "setup-guide": { title: "Step-by-Step Setup Blueprint", sub: "Instructions to build and launch your Haxball Discord server" }
    };

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            navButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(`tab-${targetTab}`).classList.add("active");

            if (tabTitles[targetTab]) {
                pageTitle.textContent = tabTitles[targetTab].title;
                pageSubtitle.textContent = tabTitles[targetTab].sub;
            }
        });
    });
}

// Render Discord Channels Tree
function renderChannelTree() {
    const container = document.getElementById("channel-tree-container");
    container.innerHTML = "";

    serverConfig.categories.forEach((cat, cIdx) => {
        const catGroup = document.createElement("div");
        catGroup.className = "category-group";

        const catHeader = document.createElement("div");
        catHeader.className = "category-header";
        catHeader.innerHTML = `<i class="fa-solid fa-angle-down"></i> ${cat.name}`;

        catGroup.appendChild(catHeader);

        cat.channels.forEach((ch, chIdx) => {
            const chItem = document.createElement("div");
            chItem.className = `channel-item ${cIdx === 1 && chIdx === 2 ? 'active' : ''}`;
            const icon = ch.type === "voice" ? "fa-volume-high" : "fa-hashtag";
            chItem.innerHTML = `<i class="fa-solid ${icon}"></i> ${ch.name}`;

            chItem.addEventListener("click", () => {
                document.querySelectorAll(".channel-item").forEach(i => i.classList.remove("active"));
                chItem.classList.add("active");
                inspectChannel(ch);
            });

            catGroup.appendChild(chItem);
        });

        container.appendChild(catGroup);
    });

    // Default inspect match-reporting
    inspectChannel(serverConfig.categories[1].channels[2]);
}

// Inspect Selected Channel
function inspectChannel(channel) {
    document.getElementById("inspector-channel-name").innerHTML = `<i class="fa-solid ${channel.type === 'voice' ? 'fa-volume-high' : 'fa-hashtag'}"></i> ${channel.name}`;
    document.getElementById("inspector-channel-type").textContent = channel.type.toUpperCase() + " CHANNEL";
    document.getElementById("inspector-channel-desc").textContent = channel.desc;

    const permsContainer = document.getElementById("inspector-permissions");
    permsContainer.innerHTML = channel.perms.map(p => {
        const isDenied = p.includes("Disabled");
        return `<span class="perm-badge ${isDenied ? 'denied' : 'allowed'}">${p}</span>`;
    }).join("");

    document.getElementById("inspector-chat-preview").textContent = channel.preview;
    document.getElementById("inspector-tip").textContent = channel.tip;
}

// Standings & Match Simulator
function renderStandings() {
    const tbody = document.getElementById("standings-tbody");
    tbody.innerHTML = "";

    // Sort teams by PTS, then GD, then GF
    teams.sort((a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf);

    teams.forEach((t, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${index + 1}</strong></td>
            <td>
                <div class="team-cell">
                    <span class="team-badge" style="background:${t.color}">${t.tag}</span>
                    <span>${t.name}</span>
                </div>
            </td>
            <td>${t.mp}</td>
            <td>${t.w}</td>
            <td>${t.d}</td>
            <td>${t.l}</td>
            <td>${t.gf}</td>
            <td>${t.ga}</td>
            <td>${t.gd > 0 ? '+' + t.gd : t.gd}</td>
            <td class="pts-highlight">${t.pts}</td>
        `;
        tbody.appendChild(tr);
    });
}

function populateMatchFormSelects() {
    const homeSel = document.getElementById("home-team-select");
    const awaySel = document.getElementById("away-team-select");

    homeSel.innerHTML = "";
    awaySel.innerHTML = "";

    teams.forEach(t => {
        homeSel.innerHTML += `<option value="${t.name}">${t.name}</option>`;
        awaySel.innerHTML += `<option value="${t.name}">${t.name}</option>`;
    });

    if (teams.length >= 2) {
        awaySel.selectedIndex = 1;
    }
}

function renderMatchFeed() {
    const feed = document.getElementById("match-feed-list");
    feed.innerHTML = recentMatches.map(m => `
        <li class="match-feed-item">
            <span><strong>${m.home}</strong> ${m.homeScore} - ${m.awayScore} <strong>${m.away}</strong></span>
            <span class="channel-type-tag">VERIFIED</span>
        </li>
    `).join("");
}

function initFormHandlers() {
    const form = document.getElementById("match-report-form");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const homeName = document.getElementById("home-team-select").value;
        const awayName = document.getElementById("away-team-select").value;
        const homeScore = parseInt(document.getElementById("home-score").value);
        const awayScore = parseInt(document.getElementById("away-score").value);

        if (homeName === awayName) {
            showToast("⚠️ Home and Away teams must be different!");
            return;
        }

        const homeTeam = teams.find(t => t.name === homeName);
        const awayTeam = teams.find(t => t.name === awayName);

        if (homeTeam && awayTeam) {
            // Update stats
            homeTeam.mp += 1;
            awayTeam.mp += 1;
            homeTeam.gf += homeScore;
            homeTeam.ga += awayScore;
            awayTeam.gf += awayScore;
            awayTeam.ga += homeScore;

            homeTeam.gd = homeTeam.gf - homeTeam.ga;
            awayTeam.gd = awayTeam.gf - awayTeam.ga;

            if (homeScore > awayScore) {
                homeTeam.w += 1;
                homeTeam.pts += 3;
                awayTeam.l += 1;
            } else if (awayScore > homeScore) {
                awayTeam.w += 1;
                awayTeam.pts += 3;
                homeTeam.l += 1;
            } else {
                homeTeam.d += 1;
                awayTeam.d += 1;
                homeTeam.pts += 1;
                awayTeam.pts += 1;
            }

            recentMatches.unshift({ home: homeName, homeScore, awayScore, away: awayName });
            renderStandings();
            renderMatchFeed();
            showToast(`⚽ Match submitted! ${homeName} ${homeScore}-${awayScore} ${awayName}`);
        }
    });

    document.getElementById("reset-stats-btn").addEventListener("click", () => {
        teams = [
            { name: "Apex Predators", tag: "APX", color: "#e5b842", mp: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0, pts: 0 },
            { name: "Shadow Strikers", tag: "STR", color: "#5865f2", mp: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0, pts: 0 },
            { name: "Titan FC", tag: "TTN", color: "#23a55a", mp: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0, pts: 0 },
            { name: "Viper United", tag: "VPR", color: "#f23f43", mp: 0, w: 0, d: 0, l: 0, gf: 0, ga: 0, gd: 0, pts: 0 }
        ];
        recentMatches = [];
        renderStandings();
        renderMatchFeed();
        showToast("Stats reset to zero!");
    });

    document.getElementById("copy-template-btn").addEventListener("click", () => {
        navigator.clipboard.writeText(JSON.stringify(serverConfig, null, 2));
        showToast("Copied server blueprint JSON to clipboard!");
    });

    document.getElementById("export-json-btn").addEventListener("click", () => {
        const blob = new Blob([JSON.stringify(serverConfig, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "haxball_discord_server_config.json";
        a.click();
        showToast("Downloaded haxball_discord_server_config.json");
    });
}

// Render Role Matrix
function renderRoleMatrix() {
    const tbody = document.getElementById("role-matrix-tbody");
    tbody.innerHTML = rolesData.map(r => `
        <tr>
            <td>
                <span class="role-pill" style="background:${r.color}22; color:${r.color}; border:1px solid ${r.color}">
                    ${r.name}
                </span>
            </td>
            <td><code>${r.color}</code></td>
            <td><strong>${r.hoist}</strong></td>
            <td>${r.perms}</td>
            <td style="color:var(--text-muted)">${r.desc}</td>
        </tr>
    `).join("");
}

// Bot Code Preview
function initBotCodePreview() {
    const codeEl = document.getElementById("python-bot-code").querySelector("code");
    codeEl.textContent = pythonBotCode;

    document.getElementById("copy-bot-code-btn").addEventListener("click", () => {
        navigator.clipboard.writeText(pythonBotCode);
        showToast("Copied Python Bot Code to clipboard!");
    });
}

function showToast(msg) {
    const toast = document.getElementById("toast");
    document.getElementById("toast-message").textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3000);
}

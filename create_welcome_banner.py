from PIL import Image, ImageDraw, ImageFont
import os

width, height = 800, 300
bg_color = (15, 17, 23)

# Create background image
img = Image.new("RGBA", (width, height), bg_color)
draw = ImageDraw.Draw(img)

# Draw gold accent borders
gold = (229, 184, 66)
dark_gold = (184, 143, 40)
draw.rectangle([10, 10, width - 10, height - 10], outline=gold, width=4)
draw.rectangle([16, 16, width - 16, height - 16], outline=dark_gold, width=1)

# Paste logo if present
logo_path = r"C:\Users\Lenovo LoQ\.gemini\antigravity\scratch\haxball_discord_league\logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((200, 200), Image.Resampling.LANCZOS)
    img.paste(logo, (40, 50), logo)

# Draw text
try:
    title_font = ImageFont.truetype("arial.ttf", 34)
    subtitle_font = ImageFont.truetype("arialbd.ttf", 26)
    footer_font = ImageFont.truetype("arial.ttf", 20)
except Exception:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    footer_font = ImageFont.load_default()

draw.text((270, 70), "WELCOME TO SKILL ISSUE PRIM LEAGUE!", fill=(229, 184, 66), font=title_font)
draw.text((270, 130), "Hope you're not a total noob! ⚽🔥", fill=(240, 242, 245), font=subtitle_font)
draw.text((270, 190), "Register with !register <haxball_nick> to join a team", fill=(139, 149, 165), font=footer_font)

out_path = r"C:\Users\Lenovo LoQ\.gemini\antigravity\scratch\haxball_discord_league\welcome_banner.png"
img.save(out_path, "PNG")
print("Welcome banner generated successfully at:", out_path)

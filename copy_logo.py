import shutil
import os
from PIL import Image

src = r"C:\Users\Lenovo LoQ\.gemini\antigravity\brain\fdfe8d7f-092d-47c7-bfae-345c33e7cdd3\.user_uploaded\media__1784636170873.jpg"
dest_png = r"C:\Users\Lenovo LoQ\.gemini\antigravity\scratch\haxball_discord_league\logo.png"
dest_brain_png = r"C:\Users\Lenovo LoQ\.gemini\antigravity\brain\fdfe8d7f-092d-47c7-bfae-345c33e7cdd3\logo.png"

# Convert to PNG with PIL
img = Image.open(src)
img.save(dest_png, "PNG")
img.save(dest_brain_png, "PNG")
print("Saved logo.png to project directory and brain directory.")

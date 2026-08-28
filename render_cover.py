import sys
from pathlib import Path

sys.path.insert(0, "/data/.openclaw/tools/two-voice-tts")
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
size = 1400
image = Image.new("RGB", (size, size), "#181b2f")
draw = ImageDraw.Draw(image)
for y in range(size):
    t = y / (size - 1)
    color = tuple(round(a + (b - a) * t) for a, b in zip((24, 27, 47), (56, 78, 116)))
    draw.line((0, y, size, y), fill=color)

gold = "#f5ca5c"
draw.ellipse((430, 230, 970, 770), outline=gold, width=28)
draw.rounded_rectangle((600, 270, 800, 730), radius=95, fill=gold)
draw.arc((510, 430, 890, 840), 0, 180, fill=gold, width=28)
draw.line((700, 810, 700, 935), fill=gold, width=28)
draw.line((585, 935, 815, 935), fill=gold, width=28)

bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
title = ImageFont.truetype(bold, 92)
subtitle = ImageFont.truetype(regular, 42)

def centered(text, y, font, fill):
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((size - (box[2] - box[0])) / 2, y), text, font=font, fill=fill)

centered("HUMAN IN THE LOOP", 1060, title, "white")
centered("PLAYFUL RESEARCH INTERVIEWS", 1180, subtitle, "#dce5f2")
image.save(root / "cover.png", optimize=True)

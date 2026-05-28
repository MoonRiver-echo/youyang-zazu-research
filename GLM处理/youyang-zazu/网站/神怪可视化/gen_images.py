#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为五篇诺皋记故事生成艺术插图。
使用Python Pillow程序生成，每张图标注生成方式。
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

OUT_DIR = Path(__file__).parent / "images"
OUT_DIR.mkdir(exist_ok=True)

# Fonts
FONT_DIR = Path(r"C:\Windows\Fonts")
TITLE_FONT = ImageFont.truetype(str(FONT_DIR / "msyhbd.ttc"), 52)
SUB_FONT = ImageFont.truetype(str(FONT_DIR / "msyh.ttc"), 28)
SMALL_FONT = ImageFont.truetype(str(FONT_DIR / "msyh.ttc"), 16)
POEM_FONT = ImageFont.truetype(str(FONT_DIR / "simsun.ttc"), 36)

W, H = 800, 560  # Image dimensions

STORIES = [
    {
        "pid": "V14-P003",
        "title": "帝江·刑天舞干戚",
        "subtitle": "卷十四 · 诺皋记上",
        "type": "神话异兽",
        "palette": [(26, 26, 46), (22, 33, 62), (15, 52, 96)],  # Deep blue/night
        "accent": (180, 140, 255),  # Purple glow
        "elements": "sixleg_silence",
        "brief_line": "六足重翼无面目 · 操干戚而舞",
    },
    {
        "pid": "V14-P006",
        "title": "天翁张坚窃车登天",
        "subtitle": "卷十四 · 诺皋记上",
        "type": "神仙志怪",
        "palette": [(45, 27, 0), (92, 61, 46), (139, 94, 60)],  # Gold/amber
        "accent": (255, 220, 120),  # Golden
        "elements": "ascension",
        "brief_line": "乘白龙登天 · 封白雀为上卿",
    },
    {
        "pid": "V14-P010",
        "title": "灶神名隗状如美女",
        "subtitle": "卷十四 · 诺皋记上",
        "type": "民俗神灵",
        "palette": [(27, 58, 27), (45, 90, 45), (62, 122, 62)],  # Green
        "accent": (200, 230, 180),  # Light green
        "elements": "hearth",
        "brief_line": "月晦上天白人罪 · 家宅神灵",
    },
    {
        "pid": "V14-P014",
        "title": "古龟兹国王降伏毒龙",
        "subtitle": "卷十四 · 诺皋记上",
        "type": "降妖伏魔",
        "palette": [(61, 12, 2), (107, 29, 14), (139, 37, 0)],  # Deep red
        "accent": (255, 160, 80),  # Orange fire
        "elements": "dragon_taming",
        "brief_line": "持剑降龙 · 乘龙而行",
    },
    {
        "pid": "V15-P001",
        "title": "刘录事食鱼骨珠化人",
        "subtitle": "卷十五 · 诺皋记下",
        "type": "妖怪变形",
        "palette": [(42, 26, 62), (74, 42, 110), (107, 63, 160)],  # Purple
        "accent": (200, 170, 255),  # Lavender
        "elements": "transformation",
        "brief_line": "骨珠化人 · 触合成一",
    },
]


def draw_radial_glow(draw, cx, cy, inner_color, radius, steps=30):
    """Draw a radial glow effect."""
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        alpha = max(0, int(80 * (1 - i / steps)))
        color = (
            min(255, inner_color[0]),
            min(255, inner_color[1]),
            min(255, inner_color[2]),
        )
        # Blend with dark
        fade = i / steps
        blended = tuple(int(c * (1 - fade * 0.7)) for c in color)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=blended)


def draw_sixleg_beast(draw, cx, cy, size, color):
    """Draw a symbolic six-legged winged creature (帝江)."""
    # Body - oblong shape
    bw, bh = size, size // 2
    draw.ellipse([cx - bw, cy - bh, cx + bw, cy + bh], fill=color, outline=color)
    # Six legs
    leg_color = tuple(max(0, c - 40) for c in color)
    for i, angle_offset in enumerate([-60, -30, 0, 0, 30, 60]):
        side = -1 if i < 3 else 1
        lx = cx + side * bw // 2 + side * 10
        ly = cy + (i - 2.5) * 20
        end_x = lx + side * size // 2
        end_y = ly + 30 + abs(angle_offset) // 3
        draw.line([(lx, ly + bh // 3), (end_x, end_y)], fill=leg_color, width=3)
    # Wings
    wing_color = tuple(min(255, c + 30) for c in color)
    draw.polygon([
        (cx - bw, cy - bh),
        (cx - bw - size // 2, cy - size),
        (cx - bw // 2, cy - bh - 10),
    ], fill=wing_color)
    draw.polygon([
        (cx + bw, cy - bh),
        (cx + bw + size // 2, cy - size),
        (cx + bw // 2, cy - bh - 10),
    ], fill=wing_color)


def draw_dancing_figure(draw, cx, cy, size, color):
    """Draw a simplified dancing figure (刑天)."""
    # Headless - no head circle
    # Body
    draw.ellipse([cx - size // 4, cy - size // 3, cx + size // 4, cy + size // 3], fill=color)
    # Arms raised with shield and axe
    draw.line([(cx - size // 4, cy), (cx - size, cy - size // 2)], fill=color, width=4)
    draw.line([(cx + size // 4, cy), (cx + size, cy - size // 2)], fill=color, width=4)
    # Shield (left)
    draw.ellipse([cx - size - 15, cy - size // 2 - 20, cx - size + 15, cy - size // 2 + 20], outline=color, width=2)
    # Axe (right)
    draw.line([(cx + size, cy - size // 2 - 30), (cx + size, cy - size // 2 + 30)], fill=color, width=3)
    # Eyes on chest (nipples as eyes)
    eye_color = (255, 200, 100)
    draw.ellipse([cx - 12, cy - size // 6 - 6, cx - 4, cy - size // 6 + 6], fill=eye_color)
    draw.ellipse([cx + 4, cy - size // 6 - 6, cx + 12, cy - size // 6 + 6], fill=eye_color)
    # Navel mouth
    draw.ellipse([cx - 8, cy + 5, cx + 8, cy + 18], outline=eye_color, width=2)
    # Legs
    draw.line([(cx - 8, cy + size // 3), (cx - size // 3, cy + size)], fill=color, width=4)
    draw.line([(cx + 8, cy + size // 3), (cx + size // 3, cy + size)], fill=color, width=4)


def draw_dragon_flying(draw, cx, cy, size, color):
    """Draw a stylized ascending dragon."""
    pts = []
    for t in range(0, 360, 5):
        rad = math.radians(t)
        x = cx + size * math.cos(rad) * 0.8
        y = cy + size * math.sin(rad) * 0.4 - t * 0.3
        pts.append((x, y))
    # Draw as connected segments
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=4)
    # Dragon head
    draw.ellipse([cx + size - 25, cy - size - 20, cx + size + 25, cy - size + 10], fill=color)


def draw_bone_transformation(draw, cx, cy, size, color):
    """Draw bone→bead→figure transformation sequence."""
    # Three stages: bone bead -> growing form -> human shape
    stages = [0.3, 0.6, 1.0]
    for i, s in enumerate(stages):
        sx = cx - size + i * size
        sy = cy
        r = int(size * 0.3 * s)
        alpha = int(180 + 75 * s)
        stage_color = tuple(min(255, int(c * s)) for c in color)
        if s < 0.5:
            # Small bead
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=stage_color, outline=color)
        elif s < 0.8:
            # Growing form
            draw.ellipse([sx - r, sy - int(r * 1.5), sx + r, sy + int(r * 0.5)], fill=stage_color, outline=color)
        else:
            # Human-like outline
            # Head
            hr = int(r * 0.35)
            hy = sy - int(r * 1.2)
            draw.ellipse([sx - hr, hy - hr, sx + hr, hy + hr], fill=stage_color, outline=color)
            # Body
            draw.rectangle([sx - int(r * 0.4), hy + hr, sx + int(r * 0.4), sy + int(r * 0.3)], fill=stage_color, outline=color)
    # Arrow connectors
    for i in range(2):
        ax = cx - size // 2 + i * size
        draw.line([(ax + 10, cy), (ax + size // 3 - 10, cy)], fill=(200, 200, 200), width=2)
        # Arrowhead
        draw.polygon([(ax + size // 3 - 10, cy), (ax + size // 3 - 20, cy - 5), (ax + size // 3 - 20, cy + 5)], fill=(200, 200, 200))


def draw_hearth_flame(draw, cx, cy, size, color):
    """Draw a stylized hearth with flame (灶神)."""
    # Hearth base
    base_color = tuple(max(0, c - 60) for c in color)
    draw.rectangle([cx - size, cy, cx + size, cy + size // 2], fill=base_color, outline=color)
    # Flame
    flame_colors = [(255, 100, 20), (255, 160, 40), (255, 220, 100)]
    for i, fc in enumerate(flame_colors):
        fh = size - i * 8
        fw = size // 2 - i * 5
        draw.polygon([
            (cx - fw, cy + 5),
            (cx, cy - fh),
            (cx + fw, cy + 5),
        ], fill=fc)
    # Smoke wisps
    for j in range(3):
        sx = cx + (j - 1) * 15
        draw.arc([sx - 8, cy - size - 20 - j * 10, sx + 8, cy - size + 5 - j * 10],
                 start=0, end=180, fill=(200, 200, 200), width=2)


def generate_image(story, idx):
    """Generate an artistic illustration for a story."""
    random.seed(idx * 42 + 7)  # Deterministic per story

    img = Image.new("RGB", (W, H), story["palette"][0])
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(H):
        t = y / H
        r = int(story["palette"][0][0] * (1 - t) + story["palette"][2][0] * t)
        g = int(story["palette"][0][1] * (1 - t) + story["palette"][2][1] * t)
        b = int(story["palette"][0][2] * (1 - t) + story["palette"][2][2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Central glow
    draw_radial_glow(draw, W // 2, H // 2 - 30, story["accent"], 180)

    # Decorative border pattern (classical Chinese cloud motif)
    border_color = tuple(min(255, c + 40) for c in story["accent"])
    for i in range(0, W, 40):
        # Top border cloud dots
        draw.ellipse([i, 8, i + 12, 20], fill=None, outline=border_color, width=1)
        # Bottom border cloud dots
        draw.ellipse([i, H - 20, i + 12, H - 8], fill=None, outline=border_color, width=1)

    # Story-specific illustration
    accent_dim = tuple(max(0, c - 60) for c in story["accent"])

    if story["elements"] == "sixleg_silence":
        # 帝江 (six-legged creature) + 刑天 (dancing decapitated figure)
        draw_sixleg_beast(draw, W // 2 - 80, H // 2 - 20, 50, accent_dim)
        draw_dancing_figure(draw, W // 2 + 100, H // 2 - 10, 40, story["accent"])
    elif story["elements"] == "ascension":
        # Flying dragon ascending
        draw_dragon_flying(draw, W // 2, H // 2 + 20, 80, story["accent"])
        # White sparrow
        draw.ellipse([W // 2 - 130, H // 2 - 60, W // 2 - 100, H // 2 - 40],
                      fill=(255, 255, 255), outline=story["accent"])
        # Small wings on sparrow
        draw.polygon([
            (W // 2 - 115, H // 2 - 55),
            (W // 2 - 145, H // 2 - 70),
            (W // 2 - 110, H // 2 - 45),
        ], fill=(240, 240, 240))
    elif story["elements"] == "hearth":
        draw_hearth_flame(draw, W // 2, H // 2 - 20, 50, story["accent"])
    elif story["elements"] == "dragon_taming":
        # Warrior on dragon
        draw_dragon_flying(draw, W // 2, H // 2 + 30, 70, story["accent"])
        # Warrior figure on top
        warrior_color = story["accent"]
        wx, wy = W // 2 + 60, H // 2 - 40
        draw.ellipse([wx - 8, wy - 18, wx + 8, wy - 2], fill=warrior_color)  # head
        draw.line([(wx, wy), (wx, wy + 25)], fill=warrior_color, width=3)  # body
        draw.line([(wx, wy + 8), (wx - 15, wy + 20)], fill=warrior_color, width=2)  # left arm
        draw.line([(wx, wy + 8), (wx + 15, wy + 15)], fill=warrior_color, width=2)  # right arm with sword
        draw.line([(wx - 12, wy + 15), (wx + 15, wy + 5)], fill=(255, 200, 100), width=2)  # sword
    elif story["elements"] == "transformation":
        draw_bone_transformation(draw, W // 2, H // 2 - 20, 70, story["accent"])

    # Decorative corner patterns (回纹 simplified)
    corner_size = 30
    cc = tuple(min(255, c + 20) for c in story["accent"])
    for cx_off, cy_off in [(15, 30), (W - 15, 30), (15, H - 50), (W - 15, H - 50)]:
        draw.rectangle([cx_off - corner_size // 4, cy_off, cx_off + corner_size // 4, cy_off + corner_size // 2],
                        outline=cc, width=1)
        draw.rectangle([cx_off, cy_off - corner_size // 4, cx_off + corner_size // 2, cy_off + corner_size // 4],
                        outline=cc, width=1)

    # Story type label (top left)
    draw.rounded_rectangle([20, 30, 140, 58], radius=12, fill=(*story["accent"], 40), outline=story["accent"], width=1)
    draw.text((30, 34), story["type"], fill=story["accent"], font=SMALL_FONT)

    # Volume label (top right)
    vol_text = story["subtitle"]
    draw.text((W - 200, 35), vol_text, fill=(200, 200, 200), font=SMALL_FONT)

    # Title (center, large)
    title = story["title"]
    draw.text((W // 2, H // 2 + 80), title, fill=(255, 255, 255), font=TITLE_FONT, anchor="mm")

    # Brief line below title
    draw.text((W // 2, H // 2 + 130), story["brief_line"], fill=(200, 200, 200), font=SUB_FONT, anchor="mm")

    # Generation attribution (bottom right)
    draw.text((W - 260, H - 35), "程序生成 · Python Pillow", fill=(140, 140, 140), font=SMALL_FONT)

    # Slight blur for dreamy effect
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    return img


def main():
    for i, story in enumerate(STORIES):
        img = generate_image(story, i)
        out_path = OUT_DIR / f"{story['pid']}.png"
        img.save(str(out_path), "PNG")
        print(f"  Generated: {out_path.name} ({img.size})")

    print(f"\nDone. Images saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
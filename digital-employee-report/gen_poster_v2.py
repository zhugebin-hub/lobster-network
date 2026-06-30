#!/usr/bin/env python3
"""直播宣传海报 - 重新布局 + 文档二维码 + 小龙虾&Manus logo"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

W, H = 1080, 1920

# Colors
BG_TOP = (8, 18, 36)
BG_MID = (12, 32, 64)
BG_BOT = (14, 20, 44)
WHITE = (240, 244, 248)
MUTED = (140, 158, 180)
ACCENT = (59, 130, 246)
ACCENT_LIGHT = (96, 165, 250)
PURPLE = (167, 139, 250)
GREEN = (16, 185, 129)
ORANGE = (245, 158, 11)
RED = (239, 68, 68)
CARD_BG = (15, 35, 68)
CARD_BORDER = (40, 80, 140)

# Load fonts
font_path = "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc"
font_hero = ImageFont.truetype(font_path, 64)
font_title = ImageFont.truetype(font_path, 48)
font_large = ImageFont.truetype(font_path, 38)
font_medium = ImageFont.truetype(font_path, 32)
font_small = ImageFont.truetype(font_path, 26)
font_tiny = ImageFont.truetype(font_path, 20)
font_xsmall = ImageFont.truetype(font_path, 17)
font_bold = ImageFont.truetype(font_path, 40)
font_number = ImageFont.truetype(font_path, 52)

# Create image
img = Image.new('RGB', (W, H), BG_TOP)
draw = ImageDraw.Draw(img)

# === GRADIENT BACKGROUND ===
for y in range(H):
    ratio = y / H
    if ratio < 0.5:
        r = int(BG_TOP[0] * (1 - ratio*2) + BG_MID[0] * ratio*2)
        g = int(BG_TOP[1] * (1 - ratio*2) + BG_MID[1] * ratio*2)
        b = int(BG_TOP[2] * (1 - ratio*2) + BG_MID[2] * ratio*2)
    else:
        r2 = (ratio - 0.5) * 2
        r = int(BG_MID[0] * (1 - r2) + BG_BOT[0] * r2)
        g = int(BG_MID[1] * (1 - r2) + BG_BOT[1] * r2)
        b = int(BG_MID[2] * (1 - r2) + BG_BOT[2] * r2)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

pad = 60

# === DECORATIVE ELEMENTS ===
# Top right glow
for r in range(200, 0, -8):
    alpha = 0.03 * (r / 200)
    cx, cy = W - 100, 150
    for dy in range(-r, r, 6):
        for dx in range(-r, r, 6):
            if dx*dx + dy*dy <= r*r:
                px, py = int(cx+dx), int(cy+dy)
                if 0 <= px < W and 0 <= py < H:
                    c = img.getpixel((px, py))
                    img.putpixel((px, py), (
                        min(255, int(c[0] * (1-alpha) + ACCENT[0] * alpha)),
                        min(255, int(c[1] * (1-alpha) + ACCENT[1] * alpha)),
                        min(255, int(c[2] * (1-alpha) + ACCENT[2] * alpha)),
                    ))

# Bottom left glow
for r in range(160, 0, -8):
    alpha = 0.025 * (r / 160)
    cx, cy = 80, H - 200
    for dy in range(-r, r, 6):
        for dx in range(-r, r, 6):
            if dx*dx + dy*dy <= r*r:
                px, py = int(cx+dx), int(cy+dy)
                if 0 <= px < W and 0 <= py < H:
                    c = img.getpixel((px, py))
                    img.putpixel((px, py), (
                        min(255, int(c[0] * (1-alpha) + GREEN[0] * alpha)),
                        min(255, int(c[1] * (1-alpha) + GREEN[1] * alpha)),
                        min(255, int(c[2] * (1-alpha) + GREEN[2] * alpha)),
                    ))

# === TOP BADGE ===
y = 50
badge_text = "清华大学出版社 · 重磅新书"
# Measure text width roughly
badge_w = 480
badge_h = 48
badge_x = (W - badge_w) // 2
draw.rounded_rectangle([badge_x, y, badge_x + badge_w, y + badge_h], radius=24,
                       fill=(59, 130, 246, 30), outline=(59, 130, 246, 80), width=1)
draw.text((W//2, y + badge_h//2), badge_text, fill=ACCENT_LIGHT, font=font_small, anchor="mm")
y += 80

# === LOGOS: Lobster + Manus ===
# Draw "🦞" lobster emoji large
draw.text((W//2, y), "🦞", font=ImageFont.truetype(font_path, 44), anchor="mm")
y += 48

# Manus text logo
draw.text((W//2, y), "Manus", fill=ACCENT_LIGHT, font=ImageFont.truetype(font_path, 56, encoding='unic'), anchor="mm")
y += 10

# === MAIN TITLE ===
title = "智能体赋能高校教学新范式"
draw.text((W//2, y), title, fill=WHITE, font=font_hero, anchor="mt")
y += 72

# Subtitle
subtitle = "小龙虾 + Manus 一站式解决方案"
draw.text((W//2, y), subtitle, fill=MUTED, font=font_large, anchor="mt")
y += 20

# Divider line
draw.line([(W//2 - 80, y), (W//2 + 80, y)], fill=ACCENT, width=3)
# Gradient dots on divider
for i in range(-80, 81, 8):
    alpha = 1.0 - abs(i) / 80 * 0.5
    dot_r = 2 + abs(i) / 80 * 2
    draw.ellipse([W//2 + i - dot_r, y - dot_r, W//2 + i + dot_r, y + dot_r],
                 fill=(int(ACCENT[0]*alpha), int(ACCENT[1]*alpha), int(ACCENT[2]*alpha)))
y += 40

# === LIVE HIGHLIGHTS SECTION ===
# Section header
draw.text((W//2, y), "直播亮点", fill=ACCENT_LIGHT, font=font_medium, anchor="mt")
y += 8
draw.text((W//2, y), "五大教学场景 · 现场实操", fill=MUTED, font=font_tiny, anchor="mt")
y += 32

# Five scenario cards
scenarios = [
    ("", "课件智能生成", '"小龙虾三部曲"精品课件', ACCENT),
    ("🌿", "教学案例开发", "烟草数据挖掘、网络课程动画、微信小程序等", GREEN),
    ("✍️", "论文协作写作", "从选题到IEEE成稿全流程", PURPLE),
    ("🎬", "教学视频制作", "PPT自动转教学视频", ORANGE),
    ("📊", "数据可视化", "一键生成可发表图表", RED),
]

card_h = 70
for i, (icon, title_text, desc, color) in enumerate(scenarios):
    cy = y + i * (card_h + 12)
    # Card
    draw.rounded_rectangle([pad, cy, W - pad, cy + card_h], radius=14,
                           fill=(15, 35, 68, 180), outline=(40, 80, 140, 100), width=1)
    # Number badge
    num = str(i + 1).zfill(2)
    draw.rounded_rectangle([pad + 10, cy + 12, pad + 46, cy + 48], radius=10, fill=color, outline=color, width=1)
    draw.text((pad + 28, cy + 30), num, fill=WHITE, font=font_small, anchor="mm")
    # Title
    draw.text((pad + 60, cy + 14), title_text, fill=WHITE, font=font_medium, anchor="lt")
    # Desc
    draw.text((pad + 60, cy + 44), desc, fill=MUTED, font=font_tiny, anchor="lt")

y += 5 * (card_h + 12) + 20

# === BENEFITS SECTION ===
draw.text((W//2, y), "入群福利", fill=GREEN, font=font_medium, anchor="mt")
y += 8
draw.text((W//2, y), "扫码加入读者服务群", fill=WHITE, font=font_large, anchor="mt")
y += 28

# Benefits grid 2x2
benefits = [
    ("🦞", "小龙虾AI体验", "群内实时体验课件生成、教案制作"),
    ("", "教学资料包", "全套Manus实战案例一键领取"),
    ("🎁", "免费样书赠送", "直播间抽10本《Manus智能体全攻略》"),
    ("💬", "教学交流社区", "高校教师AI教学实践交流答疑"),
]

bw = (W - 2*pad - 16) // 2
bh = 100
for i, (icon, name, desc) in enumerate(benefits):
    row = i // 2
    col = i % 2
    bx = pad + col * (bw + 16)
    by = y + row * (bh + 16)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12,
                           fill=(15, 35, 68, 120), outline=(40, 80, 140, 60), width=1)
    draw.text((bx + 18, by + 16), icon, font=ImageFont.truetype(font_path, 34), anchor="lt")
    draw.text((bx + 56, by + 14), name, fill=WHITE, font=font_small, anchor="lt")
    draw.text((bx + 18, by + 56), desc, fill=MUTED, font=font_tiny, anchor="lt")

y += 2 * (bh + 16) + 30

# === BOTTOM: Author + Date + QR ===
# Author photo
author_path = "/home/admin/.openclaw/workspace/digital-employee-report/author_from_doc.png"
author_y = y
if os.path.exists(author_path):
    author_img = Image.open(author_path).resize((70, 70), Image.LANCZOS)
    # Circular mask
    mask = Image.new('L', (70, 70), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, 70, 70], fill=255)
    img.paste(author_img, (pad, author_y), mask)
    # Border
    bd = ImageDraw.Draw(img)
    bd.ellipse([pad - 3, author_y - 3, pad + 73, author_y + 73], outline=(59, 130, 246, 100), width=2)

    draw.text((pad + 86, author_y + 6), "诸葛斌 教授", fill=WHITE, font=font_small, anchor="lt")
    draw.text((pad + 86, author_y + 38), "浙江工商大学 · 萨塞克斯人工智能学院", fill=MUTED, font=font_tiny, anchor="lt")
    draw.text((pad + 86, author_y + 62), "2025全国高校人工智能教育大会优秀案例一等奖", fill=ORANGE, font=font_xsmall, anchor="lt")

# Date center
draw.text((W//2, author_y + 8), "6月24日 下午 3:00-4:00", fill=ACCENT_LIGHT, font=font_medium, anchor="mt")

# QR code
qr_path = "/home/admin/.openclaw/workspace/digital-employee-report/qr_from_doc.png"
if os.path.exists(qr_path):
    qr_size = 120
    qr_img = Image.open(qr_path).resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = W - pad - qr_size
    qr_y = author_y
    # White bg
    draw.rounded_rectangle([qr_x - 6, qr_y - 6, qr_x + qr_size + 6, qr_y + qr_size + 6],
                           radius=12, fill=(255, 255, 255), outline=(59, 130, 246, 80), width=2)
    img.paste(qr_img, (qr_x, qr_y))
    draw.text((qr_x + qr_size//2, qr_y + qr_size + 10), "扫码加群", fill=MUTED, font=font_tiny, anchor="mt")

# === SAVE ===
output = "/home/admin/.openclaw/workspace/digital-employee-report/poster_v2.png"
img.save(output, 'PNG', quality=95)
print(f'✅ Poster saved: {output}')
print(f'   Size: {os.path.getsize(output)} bytes')

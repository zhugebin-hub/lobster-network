#!/usr/bin/env python3
"""生成直播宣传海报图片"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1920

# Colors
BG = (10, 22, 40)
BG2 = (15, 40, 71)
WHITE = (232, 236, 241)
MUTED = (122, 139, 163)
ACCENT = (59, 130, 246)
ACCENT_LIGHT = (96, 165, 250)
PURPLE = (167, 139, 250)
GREEN = (16, 185, 129)
ORANGE = (245, 158, 11)
RED = (239, 68, 68)

# Create image with gradient background
img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img)

# Draw gradient manually (top to bottom)
for y in range(H):
    ratio = y / H
    r = int(10 * (1 - ratio) + 15 * ratio)
    g = int(22 * (1 - ratio) + 40 * ratio)
    b = int(40 * (1 - ratio) + 71 * ratio)
    # Add some purple at bottom
    if ratio > 0.7:
        purple_ratio = (ratio - 0.7) / 0.3
        r = int(r * (1 - purple_ratio * 0.3) + 26 * purple_ratio * 0.3)
        b = int(b * (1 - purple_ratio * 0.3) + 40 * purple_ratio * 0.3)
    for x in range(0, W, 4):
        draw.line([(x, y), (x+3, y)], fill=(r, g, b))

# Decorative circles
def draw_circle(cx, cy, r, color, alpha=0.06):
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            if dx*dx + dy*dy <= r*r:
                px, py = int(cx+dx), int(cy+dy)
                if 0 <= px < W and 0 <= py < H:
                    current = img.getpixel((px, py))
                    r_new = int(current[0] * (1-alpha) + color[0] * alpha)
                    g_new = int(current[1] * (1-alpha) + color[1] * alpha)
                    b_new = int(current[2] * (1-alpha) + color[2] * alpha)
                    img.putpixel((px, py), (r_new, g_new, b_new))

# Try to load Chinese font
try:
    font_hero = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 68)
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 42)
    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 34)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 26)
    font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 20)
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 38)
except:
    font_hero = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_tiny = ImageFont.load_default()
    font_bold = ImageFont.load_default()

pad_x = 56
y = 70

# Badge
badge_text = "清华大学出版社 · 重磅新书"
badge_w = 520
badge_h = 52
badge_x = (W - badge_w) // 2
# Badge background
draw.rounded_rectangle([badge_x, y, badge_x + badge_w, y + badge_h], radius=26, fill=(59, 130, 246, 38), outline=(59, 130, 246, 77), width=1)
draw.text((badge_x + badge_w//2, y + badge_h//2), badge_text, fill=ACCENT_LIGHT, font=font_small, anchor="mm")
y += 90

# Main title
title = "智能体赋能高校教学新范式"
draw.text((W//2, y), title, fill=ACCENT_LIGHT, font=font_hero, anchor="mt")
y += 80

# Subtitle
subtitle = "小龙虾 + Manus 一站式解决方案"
draw.text((W//2, y), subtitle, fill=MUTED, font=font_large, anchor="mt")
y += 50

# Divider
draw.rectangle([W//2 - 70, y, W//2 + 70, y + 4], fill=ACCENT)
y += 30

y += 4

# Five scenarios
scenarios = [
    ("", "课件智能生成", '"小龙虾三部曲"精品课件', ACCENT),
    ("🌿", "教学案例开发", "烟草数据挖掘、网络课程动画、微信小程序等", GREEN),
    ("✍️", "论文协作写作", "从选题到IEEE成稿全流程", PURPLE),
    ("🎬", "教学视频制作", "PPT自动转教学视频", ORANGE),
    ("📊", "数据可视化", "一键生成可发表图表", RED),
]

for icon, title_text, desc, color in scenarios:
    card_y = y
    card_h = 76
    # Card background
    draw.rounded_rectangle([pad_x, card_y, W - pad_x, card_y + card_h], radius=16, fill=(59, 130, 246, 20), outline=(59, 130, 246, 50), width=1)
    # Icon
    draw.text((pad_x + 28, card_y + card_h//2), icon, font=font_large, anchor="lm")
    # Color line
    draw.rectangle([pad_x + 90, card_y + 14, pad_x + 94, card_y + card_h - 14], fill=color)
    # Title
    draw.text((pad_x + 116, card_y + 20), title_text, fill=WHITE, font=font_bold, anchor="lt")
    # Desc
    draw.text((pad_x + 116, card_y + 46), desc, fill=MUTED, font=font_small, anchor="lt")
    y += card_h + 20

# Benefits section
y += 10
draw.text((W//2, y), "入 群 福 利", fill=GREEN, font=font_tiny, anchor="mt")
y += 30
draw.text((W//2, y), "扫码加入读者服务群", fill=WHITE, font=font_large, anchor="mt")
y += 40

# Benefits grid
benefits = [
    ("🦞", "小龙虾AI体验", "群内部署OpenClaw智能体，实时体验课件生成、教案制作等AI能力"),
    ("📚", "教学资料包", "小龙虾三部曲课件、数据挖掘案例、16章教学动画、微信小程序等全套Manus实战案例"),
    ("🎁", "免费样书赠送", "直播间专享10本《Manus智能体全攻略》免费样书（名额有限，抽奖获得）"),
    ("💬", "教学交流社区", "高校教师AI教学实践交流、问题解答、经验分享"),
]

benefit_grid_x = pad_x
benefit_w = (W - 2*pad_x - 20) // 2
for i, (icon, name, desc) in enumerate(benefits):
    row = i // 2
    col = i % 2
    bx = benefit_grid_x + col * (benefit_w + 20)
    by = y + row * 130
    draw.rounded_rectangle([bx, by, bx + benefit_w, by + 116], radius=14, fill=(59, 130, 246, 15), outline=(59, 130, 246, 38), width=1)
    draw.text((bx + 20, by + 18), icon, font=font_medium, anchor="lt")
    draw.text((bx + 60, by + 18), name, fill=WHITE, font=font_medium, anchor="lt")
    # Wrap desc
    draw.text((bx + 20, by + 56), desc, fill=MUTED, font=font_tiny, anchor="lt")

y += 280

# Bottom section: author, date, QR
# Author
author_photo_path = "/home/admin/.openclaw/workspace/digital-employee-report/author_photo.png"
if os.path.exists(author_photo_path):
    author_img = Image.open(author_photo_path).resize((80, 80), Image.LANCZOS)
    # Create circular mask
    mask = Image.new('L', (80, 80), 0)
    from PIL import ImageDraw as ID2
    mask_draw = ID2.Draw(mask)
    mask_draw.ellipse([0, 0, 80, 80], fill=255)
    img.paste(author_img, (pad_x, y), mask)
    
    # Author border circle
    border_draw = ImageDraw.Draw(img)
    border_draw.ellipse([pad_x - 3, y - 3, pad_x + 83, y + 83], outline=(59, 130, 246, 100), width=3)
    
    draw.text((pad_x + 100, y + 8), "诸葛斌 教授", fill=WHITE, font=font_medium, anchor="lt")
    draw.text((pad_x + 100, y + 48), "浙江工商大学 · 萨塞克斯人工智能学院", fill=MUTED, font=font_tiny, anchor="lt")
    draw.text((pad_x + 100, y + 74), "2025全国高校人工智能教育大会优秀案例一等奖", fill=ORANGE, font=ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 16), anchor="lt")

# Date center
date_x = W // 2
draw.text((date_x, y + 8), "6月24日", fill=ACCENT_LIGHT, font=ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 56, encoding='unic'), anchor="mt")
draw.text((date_x, y + 72), "下午 3:00-4:00", fill=MUTED, font=font_small, anchor="mt")

# QR code
qr_path = "/home/admin/.openclaw/workspace/digital-employee-report/qr_code.png"
if os.path.exists(qr_path):
    qr_img = Image.open(qr_path).resize((140, 140), Image.LANCZOS)
    qr_x = W - pad_x - 140
    # White background with rounded corners
    draw.rounded_rectangle([qr_x - 8, y - 8, qr_x + 148, y + 148], radius=14, fill=(255, 255, 255), outline=(59, 130, 246, 77), width=2)
    img.paste(qr_img, (qr_x, y))
    draw.text((qr_x + 70, y + 156), "扫码加群", fill=MUTED, font=font_tiny, anchor="mt")

# Save
output = "/home/admin/.openclaw/workspace/digital-employee-report/poster.png"
img.save(output, 'PNG')
print(f'✅ Poster saved: {output}')
print(f'   Size: {os.path.getsize(output)} bytes')

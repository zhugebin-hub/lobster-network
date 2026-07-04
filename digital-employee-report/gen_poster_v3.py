#!/usr/bin/env python3
"""直播宣传海报 - 全新布局，简洁清晰"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1920

# === Colors ===
BG = (8, 16, 32)
BG_LIGHT = (12, 24, 48)
BG_CARD = (16, 32, 56)
WHITE = (245, 248, 252)
MUTED = (130, 150, 175)
ACCENT = (59, 130, 246)
ACCENT_LIGHT = (100, 170, 255)
GREEN = (16, 185, 129)
ORANGE = (245, 158, 11)
PURPLE = (167, 139, 250)
RED = (239, 68, 68)
CYAN = (56, 189, 248)
DIVIDER = (30, 60, 100)

# === Fonts ===
fp = "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc"
f_hero    = ImageFont.truetype(fp, 60)
f_title   = ImageFont.truetype(fp, 46)
f_sub     = ImageFont.truetype(fp, 34)
f_body    = ImageFont.truetype(fp, 28)
f_small   = ImageFont.truetype(fp, 24)
f_tiny    = ImageFont.truetype(fp, 20)
f_xsmall  = ImageFont.truetype(fp, 17)
f_num     = ImageFont.truetype(fp, 36)

# === Create ===
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

pad_x = 64

# ── Gradient background (subtle) ──
for y in range(H):
    t = y / H
    r = int(8 + t * 8)
    g = int(16 + t * 12)
    b = int(32 + t * 20)
    # Bottom gets slight purple tint
    if t > 0.75:
        pt = (t - 0.75) * 4
        r = int(r * (1 - pt * 0.15) + 20 * pt * 0.15)
        b = int(b * (1 - pt * 0.15) + 50 * pt * 0.15)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ── Decorative top accent bar ──
d.rectangle([(0, 0), (W, 6)], fill=ACCENT)

# ═══════════════════════════════════════
# SECTION 1: Brand + Title (y: 24 ~ 200)
# ═══════════════════════════════════════
y = 24

# Publisher badge
d.text((W//2, y), "清华大学出版社 · 重磅新书", fill=ACCENT_LIGHT, font=f_tiny, anchor="mt")
y += 28

# Lobster + Manus brand
d.text((W//2, y), "", font=ImageFont.truetype(fp, 40), anchor="mm")
y += 42
d.text((W//2, y), "Manus", fill=ACCENT_LIGHT, font=ImageFont.truetype(fp, 48, encoding='unic'), anchor="mm")
y += 36

# Main title
d.text((W//2, y), "智能体赋能高校教学新范式", fill=WHITE, font=f_hero, anchor="mt")
y += 68

# Subtitle
d.text((W//2, y), "小龙虾 + Manus 一站式解决方案", fill=MUTED, font=f_sub, anchor="mt")
y += 40

# Divider
d.line([(pad_x, y), (W - pad_x, y)], fill=DIVIDER, width=1)
y += 24

# ═══════════════════════════════════════
# SECTION 2: Author info (y: ~200 ~ 270)
# ══════════════════════════════════════
author_y = y

author_path = "/home/admin/.openclaw/workspace/digital-employee-report/author_from_doc.png"
if os.path.exists(author_path):
    aimg = Image.open(author_path).resize((56, 56), Image.LANCZOS)
    mask = Image.new('L', (56, 56), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, 56, 56], fill=255)
    img.paste(aimg, (pad_x, author_y), mask)
    # Border
    ImageDraw.Draw(img).ellipse([pad_x-2, author_y-2, pad_x+58, author_y+58],
                                 outline=(59, 130, 246, 90), width=2)

d.text((pad_x + 72, author_y + 2), "诸葛斌 教授", fill=WHITE, font=f_body, anchor="lt")
d.text((pad_x + 72, author_y + 30), "浙江工商大学 · 萨塞克斯人工智能学院", fill=MUTED, font=f_tiny, anchor="lt")
d.text((pad_x + 72, author_y + 50), "2025全国高校人工智能教育大会优秀案例一等奖", fill=ORANGE, font=f_xsmall, anchor="lt")

y = author_y + 70

# ═══════════════════════════════════════
# SECTION 3: Five Scenarios (y: ~280 ~ 620)
# ═══════════════════════════════════════
y += 10
d.text((W//2, y), "直播亮点", fill=ACCENT_LIGHT, font=f_sub, anchor="mt")
y += 8
d.text((W//2, y), "五大教学场景 · 现场实操", fill=MUTED, font=f_tiny, anchor="mt")
y += 28

scenarios = [
    ("",  "课件智能生成",  '"小龙虾三部曲"精品课件',           ACCENT),
    ("🌿", "教学案例开发",  "烟草数据挖掘、网络课程动画、微信小程序",  GREEN),
    ("✍️", "论文协作写作",  "从选题到IEEE成稿全流程",           PURPLE),
    ("", "教学视频制作",  "PPT自动转教学视频",                ORANGE),
    ("",  "数据可视化",    "一键生成可发表图表",               CYAN),
]

card_h = 60
gap = 10
for i, (icon, title_text, desc, color) in enumerate(scenarios):
    cy = y + i * (card_h + gap)
    
    # Card bg
    d.rounded_rectangle([pad_x, cy, W - pad_x, cy + card_h], radius=12,
                        fill=BG_CARD, outline=(40, 80, 140, 80), width=1)
    
    # Left color accent bar
    d.rectangle([(pad_x, cy), (pad_x + 4, cy + card_h)], fill=color)
    
    # Number circle
    ncx = pad_x + 36
    ncy = cy + card_h // 2
    d.ellipse([ncx - 16, ncy - 16, ncx + 16, ncy + 16], fill=color)
    d.text((ncx, ncy), str(i + 1), fill=WHITE, font=f_num, anchor="mm")
    
    # Title + desc
    tx = pad_x + 72
    d.text((tx, cy + 14), title_text, fill=WHITE, font=f_body, anchor="lt")
    d.text((tx, cy + 40), desc, fill=MUTED, font=f_tiny, anchor="lt")

y += 5 * (card_h + gap) + 20

# ═══════════════════════════════════════
# SECTION 4: Benefits (y: ~630 ~ 960)
# ═══════════════════════════════════════
d.text((W//2, y), "入群福利", fill=GREEN, font=f_sub, anchor="mt")
y += 8
d.text((W//2, y), "扫码加入读者服务群", fill=WHITE, font=f_title, anchor="mt")
y += 24

benefits = [
    ("🦞", "小龙虾AI体验",     "群内实时体验课件生成、教案制作"),
    ("",  "全套教学资料包",   "小龙虾三部曲课件、16章网络课程动画"),
    ("", "直播间抽奖赠书",   "10本《Manus智能体全攻略》样书"),
    ("💬", "教学交流社区",     "高校教师AI教学实践交流答疑"),
]

bw = (W - 2*pad_x - 16) // 2
bh = 96
for i, (icon, name, desc) in enumerate(benefits):
    row = i // 2
    col = i % 2
    bx = pad_x + col * (bw + 16)
    by = y + row * (bh + 16)
    
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12,
                        fill=BG_CARD, outline=(40, 80, 140, 50), width=1)
    
    d.text((bx + 16, by + 16), icon, font=ImageFont.truetype(fp, 30), anchor="lt")
    d.text((bx + 50, by + 14), name, fill=WHITE, font=f_small, anchor="lt")
    d.text((bx + 16, by + 52), desc, fill=MUTED, font=f_tiny, anchor="lt")

y += 2 * (bh + 16) + 36

# ══════════════════════════════════════
# SECTION 5: Bottom - Date + QR (y: ~970 ~ end)
# ═══════════════════════════════════════

# Date/time block (centered, prominent)
d.line([(pad_x, y), (W - pad_x, y)], fill=DIVIDER, width=1)
y += 30

d.text((W//2, y), "直播时间", fill=MUTED, font=f_tiny, anchor="mt")
y += 20
d.text((W//2, y), "6月24日  下午 3:00-4:00", fill=ACCENT_LIGHT, font=f_title, anchor="mt")
y += 50

# QR code area
qr_path = "/home/admin/.openclaw/workspace/digital-employee-report/qr_from_doc.png"
if os.path.exists(qr_path):
    qr_size = 140
    qr_img = Image.open(qr_path).resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = (W - qr_size) // 2
    
    # White card bg for QR
    card_pad = 16
    d.rounded_rectangle([qr_x - card_pad - 6, y - card_pad,
                         qr_x + qr_size + card_pad + 6, y + qr_size + card_pad + 30],
                        radius=20, fill=(255, 255, 255), outline=(59, 130, 246, 100), width=2)
    img.paste(qr_img, (qr_x, y))
    
    d.text((W//2, y + qr_size + 16), "扫码加入读者服务群", fill=ACCENT, font=f_small, anchor="mt")

# Bottom accent bar
d.rectangle([(0, H - 6), (W, H)], fill=ACCENT)

# ═════════════════════════════════════
# SAVE
# ═══════════════════════════════════════
output = "/home/admin/.openclaw/workspace/digital-employee-report/poster_v3.png"
img.save(output, 'PNG', quality=95)
print(f'✅ Poster v3 saved: {output}')
print(f'   Size: {os.path.getsize(output)} bytes')
print(f'   Dimensions: {W}x{H}')

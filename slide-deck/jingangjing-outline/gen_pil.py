#!/usr/bin/env python3
"""Generate slide PNGs using PIL/Pillow - no browser needed."""
import os
from PIL import Image, ImageDraw, ImageFont

SLIDE_DIR = "/home/admin/.openclaw/workspace/slide-deck/jingangjing-outline"
OUTPUT_DIR = SLIDE_DIR
W, H = 1280, 720

BG_COLOR = "#FAF8F0"
INK_BLACK = "#2D2D2D"
CHARCOAL = "#5D5D5D"
LIGHT_GRAY = "#9D9D9D"
GOLD = "#D4A84B"
CORAL = "#F4A261"
SAGE = "#87A96B"
SKY = "#7EC8E3"
LAVENDER = "#C5B4E3"
ROSE = "#E8A0A0"

def get_font(size, bold=False):
    """Try to find a good CJK font."""
    candidates = [
        "/usr/share/fonts/google-noto-cjk/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSerifCJKsc-Regular.otf",
        "/usr/share/fonts/noto-cjk/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto-cjk/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto-cjk/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto-cjk/NotoSerifCJKsc-Regular.otf",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
    ]
    for path in candidates:
        try:
            if path.endswith(".ttc"):
                return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)
            return ImageFont.truetype(path, size)
        except:
            continue
    # fallback
    try:
        return ImageFont.load_default()
    except:
        return None

def make_gradient_bg(draw, w, h, color1=BG_COLOR, color2=BG_COLOR):
    """Simple solid bg (gradient too slow in PIL)."""
    draw.rectangle([0, 0, w, h], fill=color1)

def draw_wash_circle(draw, cx, cy, r, color, opacity=0.2):
    """Draw a soft blurred circle (approximation)."""
    for i in range(5):
        rr = r - i * 8
        if rr > 0:
            alpha = int(255 * opacity * (1 - i * 0.15))
            draw.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=color + f"{alpha:02x}")

def draw_text_centered(draw, text, y, font, color, w=W, offset=0):
    """Draw text centered horizontally."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (w - tw) // 2 + offset
    draw.text((x, y), text, font=font, fill=color)

def draw_text(draw, text, x, y, font, color):
    draw.text((x, y), text, font=font, fill=color)

def draw_stroke_line(draw, y, x1=100, x2=1180, color=INK_BLACK, alpha=30):
    """Draw a fading horizontal line."""
    for i in range(x2 - x1):
        a = int(alpha * (1 - abs(i - (x2-x1)/2) / ((x2-x1)/2)))
        if a > 0:
            draw.point((x1+i, y), fill=f"{INK_BLACK}{a:02x}")

def draw_zen_circle(draw, cx, cy, r, color=INK_BLACK, alpha=30):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color+f"{alpha:02x}", width=2)

def draw_mountain_bg(draw, w, h, color=INK_BLACK, alpha=10):
    """Draw simple mountain silhouette at bottom."""
    points = []
    step = 20
    for x in range(0, w+step, step):
        import math
        y = h - 60 + int(40 * math.sin(x * 0.008) + 25 * math.sin(x * 0.015 + 1) + 15 * math.cos(x * 0.02))
        points.append((x, y))
    points.append((w, h))
    points.append((0, h))
    draw.polygon(points, fill=color + f"{alpha:02x}")

def draw_lotus(draw, x, y, scale=1, alpha=80):
    """Draw simple lotus flower."""
    petals = 5
    for i in range(petals):
        angle = (i - petals//2) * 20
        px = x
        py = y + scale * 15
        prx = int(8 * scale)
        pry = int(22 * scale)
        draw.ellipse([px-prx, py-pry, px+prx, py+pry], fill=ROSE + f"{alpha:02x}")

def draw_dissolving_circle(draw, cx, cy, color=INK_BLACK):
    """Draw a circle that dissolves into particles."""
    for i in range(4):
        r = 80 + i * 25
        a = int(25 * (1 - i * 0.2))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color + f"{a:02x}", width=1)
    # particles
    import random
    random.seed(42)
    for _ in range(20):
        px = cx + 100 + random.randint(0, 200)
        py = cy + random.randint(-60, 60)
        pr = random.randint(1, 4)
        a = random.randint(5, 25)
        draw.ellipse([px-pr, py-pr, px+pr, py+pr], fill=color + f"{a:02x}")

def draw_card(draw, x, y, w, h, bg_color, text_color, title, body, font_title, font_body):
    """Draw a rounded card with title and body."""
    r = 8
    # Simple rounded rect
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=bg_color)
    draw.text((x+20, y+18), title, font=font_title, fill=text_color)
    draw.text((x+20, y+58), body, font=font_body, fill=CHARCOAL)

def gen_all():
    font_title = get_font(42)
    font_large = get_font(56)
    font_verse = get_font(52)
    font_quote = get_font(32)
    font_body = get_font(22)
    font_body2 = get_font(20)
    font_small = get_font(18)
    font_cover = get_font(72)
    font_back = get_font(80)
    font_tag = get_font(18)
    font_note = get_font(16)
    font_eyes = get_font(16)

    print(f"Font title: {font_title}")

    # === Slide 1: Cover ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_mountain_bg(draw, W, H, INK_BLACK, 8)
    draw_wash_circle(draw, 1100, 600, 150, SAGE, 0.15)
    draw_text_centered(draw, "金刚般若波罗蜜经", H*0.30, font_cover, INK_BLACK)
    draw_text_centered(draw, "三十二品整体脉络", H*0.52, font_title, CHARCOAL)
    draw_text_centered(draw, "水墨禅风讲义", H*0.88, font_note, LIGHT_GRAY)
    draw_lotus(draw, 1100, 600, 2, 60)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "01-slide-cover.png"))
    print("✓ 01-slide-cover.png")

    # === Slide 2: 缘起 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_wash_circle(draw, 640, 80, 120, SAGE, 0.12)
    draw_text(draw, "第一品 · 法会因由分", 100, 60, font_tag, LIGHT_GRAY)
    draw_text(draw, "讲经缘起：日常生活中的般若", 100, 120, font_title, INK_BLACK)
    draw_stroke_line(draw, 200, 100, 750, INK_BLACK, 25)
    # quote box
    draw.rectangle([100, 230, 680, 340], fill=GOLD + "14")
    draw.rectangle([100, 230, 103, 340], fill=GOLD)
    draw_text(draw, "佛陀日常乞食、洗足、敷座而坐", 120, 240, font_quote, INK_BLACK)
    draw_text(draw, "行住坐卧皆是般若道场", 120, 290, font_quote, INK_BLACK)
    draw_text(draw, "以平常心示现，于日常中见佛法", 100, 420, font_body, CHARCOAL)
    # bowl illustration
    draw.ellipse([960, 460, 1160, 620], outline=INK_BLACK + "40", width=2)
    draw.ellipse([980, 480, 1140, 590], fill=GOLD + "15")
    draw_text(draw, "钵", 1030, 520, get_font(48), INK_BLACK + "30")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "02-slide-yuanqi.png"))
    print("✓ 02-slide-yuanqi.png")

    # === Slide 3: 发问 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_wash_circle(draw, 600, 200, 200, GOLD, 0.08)
    draw_text(draw, "第二品 · 善现启请分", 100, 60, font_tag, LIGHT_GRAY)
    draw_text(draw, "须菩提发问", 100, 120, font_title, INK_BLACK)
    # quote box
    draw.rectangle([100, 220, 1180, 400], fill=GOLD + "1A")
    draw.rectangle([100, 220, 104, 400], fill=GOLD + "80")
    draw_text(draw, "善男子善女人，发菩提心者", 140, 240, get_font(38), INK_BLACK)
    draw_text(draw, "应云何住？云何降伏其心？", 140, 300, get_font(38), INK_BLACK)
    draw_text(draw, "全经问答，由此一问展开", 100, 520, font_body2, LIGHT_GRAY)
    # question marks
    draw_text(draw, "？？", 1050, 540, get_font(100), INK_BLACK + "20")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "03-slide-fawen.png"))
    print("✓ 03-slide-fawen.png")

    # === Slide 4: 总纲 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "第三品 · 大乘正宗分", 100, 60, font_tag, LIGHT_GRAY)
    draw_text_centered(draw, "应无所住而生其心", 160, font_large, INK_BLACK)
    # decorative stroke
    draw_stroke_line(draw, 320, 250, 1030, GOLD, 60)
    draw_text_centered(draw, "度一切众生，而实无众生可度", 380, font_body, CHARCOAL)
    draw_text_centered(draw, "破除我相、人相、众生相、寿者相", 440, font_body, CHARCOAL)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "04-slide-zonggang.png"))
    print("✓ 04-slide-zonggang.png")

    # === Slide 5: 破相 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "第五品 · 如理实见分 / 第六品 · 正信希有分", 100, 60, font_tag, LIGHT_GRAY)
    draw_text(draw, "破相：凡所有相，皆是虚妄", 60, 120, font_title, INK_BLACK)
    # quote box
    draw.rectangle([60, 220, 680, 320], fill=GOLD + "14")
    draw.rectangle([60, 220, 63, 320], fill=GOLD)
    draw_text(draw, "凡所有相，皆是虚妄。", 80, 230, font_quote, INK_BLACK)
    draw_text(draw, "若见诸相非相，即见如来。", 80, 280, font_quote, INK_BLACK)
    draw_text(draw, "一切外在形相，都非真实本体", 60, 380, font_body, CHARCOAL)
    draw_text(draw, "不执着四相：我相、人相、众生相、寿者相", 60, 430, font_body, CHARCOAL)
    draw_text(draw, "般若空义难信稀有，受持此经消无量业障", 60, 480, font_body, CHARCOAL)
    # dissolving circle
    draw_dissolving_circle(draw, 1000, 350, INK_BLACK)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "05-slide-poxiang.png"))
    print("✓ 05-slide-poxiang.png")

    # === Slide 6: 无得无说 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, "第七品 · 无得无说分 / 第八品 · 依法出生分", 50, font_tag, LIGHT_GRAY)
    draw_text_centered(draw, "无得无说 · 依法出生", 90, font_title, INK_BLACK)
    draw_stroke_line(draw, 180, 100, 1180, INK_BLACK, 20)
    # left card
    draw_card(draw, 50, 220, 530, 400, CORAL + "1A", CORAL, "无得无说", "没有固定不变的\u201c无上菩提法\u201d\n如来也无固定法可说\n一切圣贤依无为法修行，深浅有别", get_font(28), font_body)
    # right card
    draw_card(draw, 700, 220, 530, 400, GOLD + "1A", GOLD, "依法出生", "一切诸佛、一切菩提法\n皆从般若生出\n持诵四句偈，福德远超七宝布施", get_font(28), font_body)
    # zen circle
    draw_zen_circle(draw, 640, 420, 30, INK_BLACK, 20)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "06-slide-wude.png"))
    print("✓ 06-slide-wude.png")

    # === Slide 7: 果位无相 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, "第九品 · 一相无相分 / 第十品 · 庄严净土分", 50, font_tag, LIGHT_GRAY)
    draw_text_centered(draw, "果位无相 · 庄严净土", 90, font_title, INK_BLACK)
    # 4 cards
    draw_card(draw, 50, 200, 560, 180, CORAL + "1A", CORAL, "四果假名", "须陀洹至阿罗汉，皆无实有可得", get_font(24), font_body2)
    draw_card(draw, 670, 200, 560, 180, SAGE + "1A", SAGE, "果位只是假名", "不可执着修行果位之相", get_font(24), font_body2)
    draw_card(draw, 50, 430, 560, 180, GOLD + "1A", GOLD, "庄严佛土", "心净则国土净，非外求可得", get_font(24), font_body2)
    draw_card(draw, 670, 430, 560, 180, SKY + "1A", SKY, "即非庄严", "庄严佛土者，即非庄严，是名庄严", get_font(24), font_body2)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "07-slide-guowei.png"))
    print("✓ 07-slide-guowei.png")

    # === Slide 8: 福德对比 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, "第十一品 · 无为福胜分 / 第十二品 · 尊重正教分", 50, font_tag, LIGHT_GRAY)
    draw_text_centered(draw, "无为福胜 · 尊重正教", 90, font_title, INK_BLACK)
    draw_stroke_line(draw, 180, 100, 1180, INK_BLACK, 20)
    # left column
    draw_text_centered(draw, "有为福报", 220, get_font(32), CORAL, offset=0)
    draw_text_centered(draw, "七宝布施", 290, font_body, CHARCOAL)
    draw_text_centered(draw, "短暂有漏，终有尽时", 330, font_body, CHARCOAL)
    # down arrow
    for y in range(380, 440, 8):
        a = int(40 * (1 - (y-380)/60))
        draw.point((170, y), fill=CORAL + f"{a:02x}")
        draw.point((172, y), fill=CORAL + f"{a:02x}")
    # right column
    draw_text_centered(draw, "无为福报", 220, get_font(32), SAGE, offset=640)
    draw_text_centered(draw, "受持般若、悟无住无相", 290, font_body, CHARCOAL, offset=640)
    draw_text_centered(draw, "无漏大福，无量倍胜", 330, font_body, CHARCOAL, offset=640)
    # up arrow
    for y in range(440, 380, -8):
        a = int(40 * (1 - (440-y)/60))
        draw.point((810, y), fill=SAGE + f"{a:02x}")
        draw.point((812, y), fill=SAGE + f"{a:02x}")
    # bottom
    draw_text_centered(draw, "无论在家出家，受持此经，一切天人皆应供养", 600, font_small, LIGHT_GRAY)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "08-slide-fude.png"))
    print("✓ 08-slide-fude.png")

    # === Slide 9: 离相寂灭 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text(draw, "第十四品 · 离相寂灭分 / 第十五品 · 持经功德分", 100, 60, font_tag, LIGHT_GRAY)
    draw_text(draw, "离相寂灭 · 持经功德", 60, 110, font_title, INK_BLACK)
    # quote
    draw.rectangle([60, 200, 650, 270], fill=GOLD + "14")
    draw.rectangle([60, 200, 63, 270], fill=GOLD)
    draw_text(draw, "离一切诸相，即名诸佛", 80, 210, font_quote, INK_BLACK)
    # body
    draw_text(draw, "发菩提心须远离四相：我、人、众生、寿者", 60, 310, font_body, CHARCOAL)
    draw_text(draw, "诸法无实亦无虚", 60, 360, font_body, CHARCOAL)
    draw_text(draw, "恒河沙数身命布施，不及受持四句偈之功德", 60, 410, font_body, CHARCOAL)
    # water reflection area
    draw.rectangle([750, 180, 1200, 600], fill=SKY + "0A")
    for y in range(250, 550, 25):
        a = int(15 * (1 - (y-250)/300))
        draw.line([(780, y), (950 + (y%40), y)], fill=INK_BLACK + f"{a:02x}", width=1)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "09-slide-lixing.png"))
    print("✓ 09-slide-lixing.png")

    # === Slide 10: 究竟无我 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, "第十七品 · 究竟无我分 / 第十八品 · 一体同观分", 50, font_tag, LIGHT_GRAY)
    draw_text_centered(draw, "究竟无我 · 一体同观", 90, font_title, INK_BLACK)
    draw_stroke_line(draw, 180, 100, 1180, INK_BLACK, 20)
    # left: no-self
    draw_text(draw, "通达无我法", 60, 220, get_font(28), INK_BLACK)
    draw_text(draw, '菩萨度生、成佛', 60, 280, font_body2, CHARCOAL)
    draw_text(draw, '皆不可执"我能度', 60, 315, font_body2, CHARCOAL)
    draw_text(draw, '众生可度"', 60, 350, font_body2, CHARCOAL)
    draw_zen_circle(draw, 130, 460, 35, INK_BLACK, 20)
    # center: five eyes
    draw_text(draw, "如来五眼", 500, 220, get_font(28), SAGE)
    eyes = [("肉眼", SAGE, 50), ("天眼", SKY, 60), ("慧眼", GOLD, 70), ("法眼", LAVENDER, 80), ("佛眼", CORAL, 90)]
    yy = 290
    for label, color, size in eyes:
        draw.ellipse([640-size//2, yy-size//2, 640+size//2, yy+size//2], fill=color + "20", outline=color + "60", width=1)
        bbox = draw.textbbox((0, 0), label, font=font_eyes)
        tw = bbox[2] - bbox[0]
        draw.text((640 - tw//2, yy - size//4), label, font=font_eyes, fill=color)
        yy += size + 15
    # right: three minds
    draw_text(draw, "三心皆空", 920, 220, get_font(28), GOLD)
    draw_text(draw, "过去心不可得", 920, 280, font_body2, CHARCOAL)
    draw_text(draw, "现在心不可得", 920, 320, font_body2, CHARCOAL)
    draw_text(draw, "未来心不可得", 920, 360, font_body2, CHARCOAL)
    # dissolving hearts
    for i in range(3):
        r = 12 - i * 4
        a = 50 - i * 15
        draw.ellipse([960-r, 450-r, 960+r, 450+r], fill=ROSE + f"{a:02x}")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "10-slide-wuwo.png"))
    print("✓ 10-slide-wuwo.png")

    # === Slide 11: 核心偈颂 ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    # mountain bg
    draw_mountain_bg(draw, W, H, INK_BLACK, 5)
    draw_mountain_bg(draw, W, H-50, INK_BLACK, 3)
    draw_wash_circle(draw, 500, 300, 250, SAGE, 0.05)
    draw_wash_circle(draw, 900, 250, 200, GOLD, 0.04)
    # tag
    draw_text_centered(draw, "第三十二品 · 应化非真分", 50, font_small, LIGHT_GRAY)
    # verse
    draw_text_centered(draw, "一切有为法", 180, font_verse, INK_BLACK)
    draw_text_centered(draw, "如梦幻泡影", 260, font_verse, INK_BLACK)
    draw_text_centered(draw, "如露亦如电", 340, font_verse, INK_BLACK)
    draw_text_centered(draw, "应作如是观", 420, font_verse, INK_BLACK)
    # bubbles
    bubbles = [(100,100,15,SKY),(200,150,8,GOLD),(1100,200,12,SAGE),(1050,600,10,ROSE),(150,650,6,GOLD),(1150,100,18,SKY)]
    for bx, by, br, bc in bubbles:
        draw.ellipse([bx-br, by-br, bx+br, by+br], outline=bc + "30", width=1)
    # note
    draw_text_centered(draw, "说法不取诸相，如如不动", 620, font_note, LIGHT_GRAY)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "11-slide-jieyu.png"))
    print("✓ 11-slide-jieyu.png")

    # === Slide 12: Back Cover ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_mountain_bg(draw, W, H-30, INK_BLACK, 4)
    draw_text_centered(draw, "信受奉行", 200, font_back, INK_BLACK)
    draw_stroke_line(draw, 320, 540, 740, INK_BLACK, 25)
    draw_text_centered(draw, "大众闻法开悟，信受奉行", 370, font_body2, CHARCOAL)
    draw_text_centered(draw, "金刚般若波罗蜜经 · 三十二品脉络讲义", 620, font_note, LIGHT_GRAY)
    # petal
    draw.ellipse([50, 590, 70, 640], fill=ROSE + "20")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "12-slide-back-cover.png"))
    print("✓ 12-slide-back-cover.png")

    print("\nAll 12 slides generated successfully!")

if __name__ == "__main__":
    gen_all()

#!/usr/bin/env python3
"""Generate slide PNGs using PIL/Pillow with proper CJK fonts."""
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

CJK_FONT = "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc"

def gf(size):
    try:
        return ImageFont.truetype(CJK_FONT, size)
    except:
        return ImageFont.load_default()

def draw_stroke_line(draw, y, x1=100, x2=1180, color=INK_BLACK, alpha=30):
    for i in range(x2 - x1):
        a = int(alpha * (1 - abs(i - (x2-x1)/2) / ((x2-x1)/2)))
        if a > 0:
            draw.point((x1+i, y), fill=INK_BLACK + f"{a:02x}")

def draw_zen_circle(draw, cx, cy, r, color=INK_BLACK, alpha=30):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color+f"{alpha:02x}", width=2)

def draw_mountain_bg(draw, w, h, color=INK_BLACK, alpha=10):
    import math
    points = []
    for x in range(0, w+20, 20):
        y = h - 60 + int(40*math.sin(x*0.008) + 25*math.sin(x*0.015+1) + 15*math.cos(x*0.02))
        points.append((x, y))
    points.append((w, h))
    points.append((0, h))
    draw.polygon(points, fill=color+f"{alpha:02x}")

def draw_wash(draw, cx, cy, r, color, opacity=0.2):
    for i in range(5):
        rr = r - i*8
        if rr > 0:
            a = int(255*opacity*(1-i*0.15))
            draw.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=color+f"{a:02x}")

def gen_all():
    ft72 = gf(72); ft56 = gf(56); ft52 = gf(52); ft42 = gf(42); ft38 = gf(38)
    ft32 = gf(32); ft28 = gf(28); ft24 = gf(24); ft22 = gf(22); ft20 = gf(20)
    ft18 = gf(18); ft16 = gf(16); ft14 = gf(14); ft12 = gf(12)

    # === Slide 1: Cover ===
    img = Image.new("RGBA", (W, H), BG_COLOR)
    d = ImageDraw.Draw(img)
    draw_mountain_bg(d, W, H, INK_BLACK, 8)
    draw_wash(d, 1100, 600, 150, SAGE, 0.15)
    # Title centered
    txt = "金刚般若波罗蜜经"
    bbox = d.textbbox((0,0), txt, font=ft72)
    tw = bbox[2]-bbox[0]
    d.text(((W-tw)//2, int(H*0.30)), txt, font=ft72, fill=INK_BLACK)
    txt2 = "三十二品整体脉络"
    bbox2 = d.textbbox((0,0), txt2, font=ft42)
    d.text(((W-bbox2[2])//2, int(H*0.52)), txt2, font=ft42, fill=CHARCOAL)
    txt3 = "水墨禅风讲义"
    bbox3 = d.textbbox((0,0), txt3, font=ft18)
    d.text(((W-bbox3[2])//2, int(H*0.88)), txt3, font=ft18, fill=LIGHT_GRAY)
    # Lotus
    for angle in [-40,-20,0,20,40]:
        d.ellipse([1080,570,1120,630], fill=ROSE+"50")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "01-slide-cover.png"))
    print("01 ok")

    # === Slide 2 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    draw_wash(d, 640, 80, 120, SAGE, 0.12)
    d.text((100, 60), "第一品 · 法会因由分", font=ft18, fill=LIGHT_GRAY)
    d.text((100, 115), "讲经缘起：日常生活中的般若", font=ft42, fill=INK_BLACK)
    draw_stroke_line(d, 200, 100, 750)
    # Quote box
    d.rectangle([100, 230, 680, 340], fill=GOLD+"14")
    d.rectangle([100, 230, 103, 340], fill=GOLD)
    d.text((120, 245), "佛陀日常乞食、洗足、敷座而坐", font=ft32, fill=INK_BLACK)
    d.text((120, 295), "行住坐卧皆是般若道场", font=ft32, fill=INK_BLACK)
    d.text((100, 400), "以平常心示现，于日常中见佛法", font=ft22, fill=CHARCOAL)
    d.ellipse([960, 460, 1160, 620], outline=INK_BLACK+"40", width=2)
    d.ellipse([980, 480, 1140, 590], fill=GOLD+"15")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "02-slide-yuanqi.png"))
    print("02 ok")

    # === Slide 3 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    draw_wash(d, 600, 200, 200, GOLD, 0.08)
    d.text((100, 60), "第二品 · 善现启请分", font=ft18, fill=LIGHT_GRAY)
    d.text((100, 115), "须菩提发问", font=ft42, fill=INK_BLACK)
    d.rectangle([100, 220, 1180, 410], fill=GOLD+"1A")
    d.rectangle([100, 220, 104, 410], fill=GOLD+"80")
    d.text((140, 240), "善男子善女人，发菩提心者", font=ft38, fill=INK_BLACK)
    d.text((140, 300), "应云何住？云何降伏其心？", font=ft38, fill=INK_BLACK)
    d.text((100, 500), "全经问答，由此一问展开", font=ft20, fill=LIGHT_GRAY)
    d.text((1050, 540), "？？", font=gf(100), fill=INK_BLACK+"20")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "03-slide-fawen.png"))
    print("03 ok")

    # === Slide 4 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    d.text((100, 60), "第三品 · 大乘正宗分", font=ft18, fill=LIGHT_GRAY)
    txt = "应无所住而生其心"
    bbox = d.textbbox((0,0), txt, font=ft56)
    d.text(((W-bbox[2])//2, 160), txt, font=ft56, fill=INK_BLACK)
    draw_stroke_line(d, 320, 250, 1030, GOLD, 60)
    txt2 = "度一切众生，而实无众生可度"
    bbox2 = d.textbbox((0,0), txt2, font=ft24)
    d.text(((W-bbox2[2])//2, 380), txt2, font=ft24, fill=CHARCOAL)
    txt3 = "破除我相、人相、众生相、寿者相"
    bbox3 = d.textbbox((0,0), txt3, font=ft24)
    d.text(((W-bbox3[2])//2, 430), txt3, font=ft24, fill=CHARCOAL)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "04-slide-zonggang.png"))
    print("04 ok")

    # === Slide 5 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    d.text((100, 60), "第五品 · 如理实见分 / 第六品 · 正信希有分", font=ft18, fill=LIGHT_GRAY)
    d.text((60, 115), "破相：凡所有相，皆是虚妄", font=ft42, fill=INK_BLACK)
    d.rectangle([60, 220, 680, 330], fill=GOLD+"14")
    d.rectangle([60, 220, 63, 330], fill=GOLD)
    d.text((80, 235), "凡所有相，皆是虚妄。", font=ft32, fill=INK_BLACK)
    d.text((80, 285), "若见诸相非相，即见如来。", font=ft32, fill=INK_BLACK)
    d.text((60, 380), "一切外在形相，都非真实本体", font=ft22, fill=CHARCOAL)
    d.text((60, 425), "不执着四相：我相、人相、众生相、寿者相", font=ft22, fill=CHARCOAL)
    d.text((60, 470), "般若空义难信稀有，受持此经消无量业障", font=ft22, fill=CHARCOAL)
    # Dissolving circle
    for i in range(4):
        r = 80+i*25; a = int(25*(1-i*0.2))
        d.ellipse([1000-r, 350-r, 1000+r, 350+r], outline=INK_BLACK+f"{a:02x}", width=1)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "05-slide-poxiang.png"))
    print("05 ok")

    # === Slide 6 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    txt = "第七品 · 无得无说分 / 第八品 · 依法出生分"
    bbox = d.textbbox((0,0), txt, font=ft18)
    d.text(((W-bbox[2])//2, 50), txt, font=ft18, fill=LIGHT_GRAY)
    txt2 = "无得无说 · 依法出生"
    bbox2 = d.textbbox((0,0), txt2, font=ft42)
    d.text(((W-bbox2[2])//2, 90), txt2, font=ft42, fill=INK_BLACK)
    draw_stroke_line(d, 180)
    # Left card
    d.rounded_rectangle([50, 220, 580, 620], radius=8, fill=CORAL+"1A")
    d.text((75, 240), "无得无说", font=ft28, fill=CORAL)
    d.text((75, 290), "没有固定不变的\u201c无上菩提法\u201d", font=ft22, fill=CHARCOAL)
    d.text((75, 330), "如来也无固定法可说", font=ft22, fill=CHARCOAL)
    d.text((75, 370), "一切圣贤依无为法修行，深浅有别", font=ft22, fill=CHARCOAL)
    # Right card
    d.rounded_rectangle([650, 220, 1180, 620], radius=8, fill=GOLD+"1A")
    d.text((675, 240), "依法出生", font=ft28, fill=GOLD)
    d.text((675, 290), "一切诸佛、一切菩提法", font=ft22, fill=CHARCOAL)
    d.text((675, 330), "皆从般若生出", font=ft22, fill=CHARCOAL)
    d.text((675, 370), "持诵四句偈，福德远超七宝布施", font=ft22, fill=CHARCOAL)
    draw_zen_circle(d, 640, 420, 30, INK_BLACK, 20)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "06-slide-wude.png"))
    print("06 ok")

    # === Slide 7 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    txt = "第九品 · 一相无相分 / 第十品 · 庄严净土分"
    bbox = d.textbbox((0,0), txt, font=ft18)
    d.text(((W-bbox[2])//2, 50), txt, font=ft18, fill=LIGHT_GRAY)
    txt2 = "果位无相 · 庄严净土"
    bbox2 = d.textbbox((0,0), txt2, font=ft42)
    d.text(((W-bbox2[2])//2, 90), txt2, font=ft42, fill=INK_BLACK)
    # 4 cards
    cards = [
        (50, 200, CORAL, "四果假名", "须陀洹至阿罗汉，皆无实有可得"),
        (670, 200, SAGE, "果位只是假名", "不可执着修行果位之相"),
        (50, 420, GOLD, "庄严佛土", "心净则国土净，非外求可得"),
        (670, 420, SKY, "即非庄严", "庄严佛土者，即非庄严，是名庄严"),
    ]
    for x, y, c, title, body in cards:
        d.rounded_rectangle([x, y, x+560, y+180], radius=8, fill=c+"1A")
        d.text((x+25, y+20), title, font=ft24, fill=c)
        d.text((x+25, y+60), body, font=ft20, fill=CHARCOAL)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "07-slide-guowei.png"))
    print("07 ok")

    # === Slide 8 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    txt = "第十一品 · 无为福胜分 / 第十二品 · 尊重正教分"
    bbox = d.textbbox((0,0), txt, font=ft18)
    d.text(((W-bbox[2])//2, 50), txt, font=ft18, fill=LIGHT_GRAY)
    txt2 = "无为福胜 · 尊重正教"
    bbox2 = d.textbbox((0,0), txt2, font=ft42)
    d.text(((W-bbox2[2])//2, 90), txt2, font=ft42, fill=INK_BLACK)
    draw_stroke_line(d, 180)
    # Left
    txt_l = "有为福报"
    bbox_l = d.textbbox((0,0), txt_l, font=ft32)
    d.text(((560-bbox_l[2])//2, 220), txt_l, font=ft32, fill=CORAL)
    d.text(((560-d.textbbox((0,0),"七宝布施",font=ft22)[2])//2, 290), "七宝布施", font=ft22, fill=CHARCOAL)
    d.text(((560-d.textbbox((0,0),"短暂有漏，终有尽时",font=ft22)[2])//2, 330), "短暂有漏，终有尽时", font=ft22, fill=CHARCOAL)
    # Right
    txt_r = "无为福报"
    bbox_r = d.textbbox((0,0), txt_r, font=ft32)
    d.text((640+(560-bbox_r[2])//2, 220), txt_r, font=ft32, fill=SAGE)
    d.text((640+(560-d.textbbox((0,0),"受持般若、悟无住无相",font=ft22)[2])//2, 290), "受持般若、悟无住无相", font=ft22, fill=CHARCOAL)
    d.text((640+(560-d.textbbox((0,0),"无漏大福，无量倍胜",font=ft22)[2])//2, 330), "无漏大福，无量倍胜", font=ft22, fill=CHARCOAL)
    # Bottom
    txt_b = "无论在家出家，受持此经，一切天人皆应供养"
    bbox_b = d.textbbox((0,0), txt_b, font=ft18)
    d.text(((W-bbox_b[2])//2, 600), txt_b, font=ft18, fill=LIGHT_GRAY)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "08-slide-fude.png"))
    print("08 ok")

    # === Slide 9 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    d.text((100, 60), "第十四品 · 离相寂灭分 / 第十五品 · 持经功德分", font=ft18, fill=LIGHT_GRAY)
    d.text((60, 115), "离相寂灭 · 持经功德", font=ft42, fill=INK_BLACK)
    d.rectangle([60, 200, 650, 270], fill=GOLD+"14")
    d.rectangle([60, 200, 63, 270], fill=GOLD)
    d.text((80, 215), "离一切诸相，即名诸佛", font=ft32, fill=INK_BLACK)
    d.text((60, 310), "发菩提心须远离四相：我、人、众生、寿者", font=ft22, fill=CHARCOAL)
    d.text((60, 355), "诸法无实亦无虚", font=ft22, fill=CHARCOAL)
    d.text((60, 400), "恒河沙数身命布施，不及受持四句偈之功德", font=ft22, fill=CHARCOAL)
    # Water area
    d.rectangle([750, 180, 1200, 600], fill=SKY+"0A")
    for y in range(250, 550, 25):
        a = int(15*(1-(y-250)/300))
        d.line([(780, y), (950+(y%40), y)], fill=INK_BLACK+f"{a:02x}", width=1)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "09-slide-lixing.png"))
    print("09 ok")

    # === Slide 10 ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    txt = "第十七品 · 究竟无我分 / 第十八品 · 一体同观分"
    bbox = d.textbbox((0,0), txt, font=ft18)
    d.text(((W-bbox[2])//2, 50), txt, font=ft18, fill=LIGHT_GRAY)
    txt2 = "究竟无我 · 一体同观"
    bbox2 = d.textbbox((0,0), txt2, font=ft42)
    d.text(((W-bbox2[2])//2, 90), txt2, font=ft42, fill=INK_BLACK)
    draw_stroke_line(d, 180)
    # Left
    d.text((60, 220), "通达无我法", font=ft28, fill=INK_BLACK)
    d.text((60, 275), "菩萨度生、成佛", font=ft20, fill=CHARCOAL)
    d.text((60, 310), '\u7686\u4e0d\u53ef\u6267"\u6211\u80fd\u5ea6', font=ft20, fill=CHARCOAL)
    d.text((60, 345), '\u4f17\u751f\u53ef\u5ea6"', font=ft20, fill=CHARCOAL)
    draw_zen_circle(d, 130, 460, 35, INK_BLACK, 20)
    # Center: five eyes
    d.text((500, 220), "如来五眼", font=ft28, fill=SAGE)
    eyes = [("肉眼", SAGE, 50), ("天眼", SKY, 60), ("慧眼", GOLD, 70), ("法眼", LAVENDER, 80), ("佛眼", CORAL, 90)]
    yy = 290
    for label, color, size in eyes:
        d.ellipse([640-size//2, yy-size//2, 640+size//2, yy+size//2], fill=color+"20", outline=color+"60", width=1)
        lb = d.textbbox((0,0), label, font=ft16)
        d.text((640-lb[2]//2, yy-size//4), label, font=ft16, fill=color)
        yy += size + 15
    # Right
    d.text((920, 220), "三心皆空", font=ft28, fill=GOLD)
    d.text((920, 280), "过去心不可得", font=ft20, fill=CHARCOAL)
    d.text((920, 320), "现在心不可得", font=ft20, fill=CHARCOAL)
    d.text((920, 360), "未来心不可得", font=ft20, fill=CHARCOAL)
    for i in range(3):
        r = 12-i*4; a = 50-i*15
        d.ellipse([960-r, 450-r, 960+r, 450+r], fill=ROSE+f"{a:02x}")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "10-slide-wuwo.png"))
    print("10 ok")

    # === Slide 11: Verse ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    draw_mountain_bg(d, W, H, INK_BLACK, 5)
    draw_mountain_bg(d, W, H-50, INK_BLACK, 3)
    draw_wash(d, 500, 300, 250, SAGE, 0.05)
    draw_wash(d, 900, 250, 200, GOLD, 0.04)
    txt = "第三十二品 · 应化非真分"
    bbox = d.textbbox((0,0), txt, font=ft16)
    d.text(((W-bbox[2])//2, 50), txt, font=ft16, fill=LIGHT_GRAY)
    # Verse lines centered
    lines = ["一切有为法", "如梦幻泡影", "如露亦如电", "应作如是观"]
    y_start = 180
    for line in lines:
        bbox = d.textbbox((0,0), line, font=ft52)
        d.text(((W-bbox[2])//2, y_start), line, font=ft52, fill=INK_BLACK)
        y_start += 80
    # Bubbles
    bubbles = [(100,100,15,SKY),(200,150,8,GOLD),(1100,200,12,SAGE),(1050,600,10,ROSE),(150,650,6,GOLD),(1150,100,18,SKY)]
    for bx, by, br, bc in bubbles:
        d.ellipse([bx-br, by-br, bx+br, by+br], outline=bc+"30", width=1)
    txt_n = "说法不取诸相，如如不动"
    bbox_n = d.textbbox((0,0), txt_n, font=ft16)
    d.text(((W-bbox_n[2])//2, 620), txt_n, font=ft16, fill=LIGHT_GRAY)
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "11-slide-jieyu.png"))
    print("11 ok")

    # === Slide 12: Back Cover ===
    img = Image.new("RGBA", (W, H), BG_COLOR); d = ImageDraw.Draw(img)
    draw_mountain_bg(d, W, H-30, INK_BLACK, 4)
    txt = "信受奉行"
    bbox = d.textbbox((0,0), txt, font=ft72)
    d.text(((W-bbox[2])//2, 200), txt, font=ft72, fill=INK_BLACK)
    draw_stroke_line(d, 320, 540, 740, INK_BLACK, 25)
    txt2 = "大众闻法开悟，信受奉行"
    bbox2 = d.textbbox((0,0), txt2, font=ft22)
    d.text(((W-bbox2[2])//2, 370), txt2, font=ft22, fill=CHARCOAL)
    txt3 = "金刚般若波罗蜜经 · 三十二品脉络讲义"
    bbox3 = d.textbbox((0,0), txt3, font=ft16)
    d.text(((W-bbox3[2])//2, 620), txt3, font=ft16, fill=LIGHT_GRAY)
    d.ellipse([50, 590, 70, 640], fill=ROSE+"20")
    img.convert("RGB").save(os.path.join(OUTPUT_DIR, "12-slide-back-cover.png"))
    print("12 ok")

    print("\nAll 12 slides regenerated with CJK fonts!")

if __name__ == "__main__":
    gen_all()

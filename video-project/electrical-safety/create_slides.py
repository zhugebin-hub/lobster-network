#!/usr/bin/env python3
"""Create content slides for the electrical safety video."""

from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1920, 1080
OUT_DIR = "/home/admin/.openclaw/workspace/video-project/electrical-safety"

# Color scheme - bright, kid-friendly
BG_COLOR = "#FFF8E7"       # warm cream
TEXT_COLOR = "#333333"      # dark gray
ACCENT_COLOR = "#FF6B35"    # orange
ACCENT2_COLOR = "#4A90D9"   # blue
BORDER_COLOR = "#E8D5B7"    # light brown

def create_slide(title, lines, filename, accent=ACCENT_COLOR, icon="⚡"):
    """Create a slide with title and bullet points."""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Add decorative border
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=BORDER_COLOR, width=4)
    
    # Top accent bar
    draw.rectangle([20, 20, WIDTH-20, 100], fill=accent)
    
    # Title
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 64)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 44)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 64)
            text_font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 44)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
    # Draw icon and title
    draw.text((80, 35), f"{icon} {title}", fill="white", font=title_font)
    
    # Draw content lines
    y = 180
    line_height = 75
    for i, line in enumerate(lines):
        # Add number/bullet
        if i < 9:
            bullet = f"{i+1}."
            draw.text((80, y), bullet, fill=accent, font=text_font)
            draw.text((150, y), line, fill=TEXT_COLOR, font=text_font)
        else:
            draw.text((80, y), line, fill=TEXT_COLOR, font=text_font)
        y += line_height
    
    img.save(os.path.join(OUT_DIR, filename), "JPEG", quality=95)
    print(f"Created: {filename}")

# Slide 1: Title card
create_slide(
    "暑假用电安全小常识",
    [
        "小朋友们，暑假要注意用电安全哦！",
        "下面是几个重要的安全小知识，",
        "让我们一起学习吧！",
    ],
    "slide1.jpg",
    accent="#FF6B35",
    icon="🏠"
)

# Slide 2: 不要湿手碰电器
create_slide(
    "不要湿手碰电器",
    [
        "不要用湿手去碰开关和插座",
        "水会导电，非常危险！",
        "洗手之后要先擦干手，",
        "再去碰电器和开关。",
    ],
    "slide2.jpg",
    accent="#E74C3C",
    icon="💧"
)

# Slide 3: 不要乱插乱拔
create_slide(
    "不要乱插乱拔",
    [
        "不要随便把电线插头拔出来",
        "不要往插座里塞东西",
        "电线破了、露出来了，",
        "千万不要用手去摸！",
        "要赶紧告诉爸爸妈妈。",
    ],
    "slide3.jpg",
    accent="#E67E22",
    icon="🔌"
)

# Slide 4: 电器用完要关掉
create_slide(
    "电器用完要关掉",
    [
        "看完电视要关掉电源",
        "充电器不用时要拔下来",
        "不要同时用太多大功率电器",
        "这样容易引发电路故障。",
    ],
    "slide4.jpg",
    accent="#27AE60",
    icon="📺"
)

# Slide 5: 雷雨天气注意
create_slide(
    "雷雨天气要注意",
    [
        "打雷下雨的时候，",
        "要关掉电视和电脑。",
        "不要靠近窗户和金属物品，",
        "不要在室内给手机充电。",
    ],
    "slide5.jpg",
    accent="#8E44AD",
    icon="⛈️"
)

# Slide 6: 紧急情况
create_slide(
    "紧急情况怎么办",
    [
        "电器冒烟或有焦味，",
        "千万不要用水去泼！",
        "赶紧告诉大人，",
        "拨打119火警电话。",
        "安全第一，预防为主！",
    ],
    "slide6.jpg",
    accent="#C0392B",
    icon="🚨"
)

print("All slides created!")

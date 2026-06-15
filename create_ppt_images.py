#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

# 创建输出目录
os.makedirs('/home/admin/.openclaw/workspace/ppt_images', exist_ok=True)

# 幻灯片尺寸 1920x1080 (16:9)
WIDTH, HEIGHT = 1920, 1080

# 配色方案
COLORS = {
    'primary': (102, 187, 106),
    'primary_dark': (76, 161, 80),
    'secondary': (66, 165, 245),
    'accent': (255, 167, 38),
    'warm': (255, 204, 128),
    'text_dark': (51, 51, 51),
    'text_light': (102, 102, 102),
    'white': (255, 255, 255),
    'bg_light': (245, 250, 245),
}

# 尝试加载字体
def load_font(size, bold=False):
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

font_title = load_font(72, True)
font_subtitle = load_font(36)
font_content = load_font(32)
font_small = load_font(24)

def create_slide(slide_num, title, draw_func):
    """创建幻灯片"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    # 绘制背景
    draw_func(draw, img)
    
    # 保存
    filename = f'/home/admin/.openclaw/workspace/ppt_images/slide_{slide_num:02d}.png'
    img.save(filename, 'PNG', quality=95)
    print(f"生成：{filename}")
    return img

def draw_title_slide(draw, img):
    """标题页"""
    # 渐变背景
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(245 + (255 - 245) * ratio)
        g = int(250 + (255 - 250) * ratio)
        b = int(245 + (255 - 245) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # 装饰圆
    draw.ellipse([(-100, -100), (300, 300)], fill=(*COLORS['primary'], 30))
    draw.ellipse([(1600, 800), (2000, 1200)], fill=(*COLORS['accent'], 40))
    
    # 主标题
    title = "潮潮姐智能体"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 400), title, font=font_title, fill=COLORS['primary_dark'])
    
    # 副标题
    subtitle = "海宁市王国维小学教育集团 · AI 心理伙伴"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - subtitle_w) / 2, 550), subtitle, font=font_subtitle, fill=COLORS['text_light'])
    
    # 底部装饰线
    draw.rectangle([(400, 900), (1520, 910)], fill=COLORS['primary'])

def draw_who_slide(draw, img):
    """潮潮姐是谁"""
    # 顶部色块
    draw.rectangle([(0, 0), (WIDTH, 150)], fill=COLORS['primary'])
    
    # 标题
    title = "潮潮姐是谁？"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 45), title, font=font_title, fill=COLORS['white'])
    
    # 内容背景
    draw.rounded_rectangle([(100, 180), (1820, 1000)], radius=30, fill=COLORS['bg_light'], outline=COLORS['primary'], width=4)
    
    # 内容项
    items = [
        "🤖 学校专属的 AI 心理健康伙伴",
        "🎨 基于学校吉祥物'潮娃'设计",
        "☀️ 形象亲切阳光，像贴心大朋友",
        "🛡️ 使命：陪伴孩子，守护心理健康",
        "👦 做校园里随时在线的心理小卫士",
    ]
    
    y = 250
    for item in items:
        draw.text((200, y), item, font=font_content, fill=COLORS['text_dark'])
        y += 130

def draw_scene_slide(draw, img):
    """使用场景"""
    # 顶部色块
    draw.rectangle([(0, 0), (WIDTH, 150)], fill=COLORS['secondary'])
    
    title = "使用场景"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 45), title, font=font_title, fill=COLORS['white'])
    
    # 内容背景
    draw.rounded_rectangle([(100, 180), (1820, 1000)], radius=30, fill=COLORS['bg_light'], outline=COLORS['secondary'], width=4)
    
    items = [
        "📍 部署位置：心理健康教室专用平板",
        "⏰ 使用时间：课间、午休、课后随时可用",
        "🔒 隐私保护：一对一平板交互",
        "💡 适合所有孩子，包括内向害羞的孩子",
        "👩‍🏫 定位：心理老师的辅助工具",
    ]
    
    y = 250
    for item in items:
        draw.text((200, y), item, font=font_content, fill=COLORS['text_dark'])
        y += 130

def draw_features_slide(draw, img):
    """三大核心功能"""
    # 顶部色块
    draw.rectangle([(0, 0), (WIDTH, 150)], fill=COLORS['primary'])
    
    title = "三大核心功能"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 45), title, font=font_title, fill=COLORS['white'])
    
    # 三个卡片
    card_colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    features = [
        ("🌳 情绪树洞", ["• 倾诉烦恼、不开心", "• 共情安慰", "• 情绪支持"]),
        ("📚 心理小课堂", ["• 趣味科普心理知识", "• 教情绪调节小技巧", "• 寓教于乐"]),
        ("🌱 成长陪伴", ["• 记录成长", "• 正向激励", "• 提供亲子沟通建议"]),
    ]
    
    card_w = 540
    card_h = 700
    card_y = 200
    spacing = 50
    start_x = 140
    
    for i, (feat_title, feat_desc) in enumerate(features):
        x = start_x + i * (card_w + spacing)
        
        # 卡片背景
        draw.rounded_rectangle([(x, card_y), (x + card_w, card_y + card_h)], radius=20, 
                               fill=COLORS['white'], outline=card_colors[i], width=5)
        
        # 卡片顶部色条
        draw.rounded_rectangle([(x, card_y), (x + card_w, card_y + 100)], radius=20, fill=card_colors[i])
        
        # 功能标题
        draw.text((x + 30, card_y + 30), feat_title, font=font_content, fill=COLORS['white'])
        
        # 功能描述
        y = card_y + 140
        for line in feat_desc:
            draw.text((x + 30, y), line, font=font_small, fill=COLORS['text_dark'])
            y += 50

def draw_examples_slide(draw, img):
    """互动示例"""
    # 顶部色块
    draw.rectangle([(0, 0), (WIDTH, 150)], fill=COLORS['primary'])
    
    title = "互动示例"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 45), title, font=font_title, fill=COLORS['white'])
    
    examples = [
        ("场景一：考试没考好", [
            '孩子："潮潮姐姐，我今天考试没考好，很难过"',
            '',
            '潮潮姐："抱抱你，没考好心里肯定不好受吧，我能理解这种感觉"',
            '',
            '潮潮姐："你已经很努力了，一次的成绩不代表全部哦，'
        ]),
        ("场景二：上课走神", [
            '孩子："潮潮姐姐，我上课总是容易走神，注意力不集中"',
            '',
            '潮潮姐："这是很普遍的现象，别担心"',
            '',
            '潮潮姐："推荐番茄学习法——专注听课 20 分钟，休息 5 分钟"'
        ]),
    ]
    
    for i, (scene, dialog) in enumerate(examples):
        x = 100 + i * 880
        
        # 场景标题
        draw.text((x, 180), scene, font=font_content, fill=COLORS['primary_dark'])
        
        # 对话背景
        draw.rounded_rectangle([(x, 230), (x + 840, 950)], radius=20, fill=COLORS['bg_light'], 
                               outline=COLORS['primary'], width=3)
        
        # 对话内容
        y = 260
        for line in dialog:
            draw.text((x + 30, y), line, font=font_small, fill=COLORS['text_dark'])
            y += 45

def draw_value_slide(draw, img):
    """价值与未来"""
    # 顶部色块
    draw.rectangle([(0, 0), (WIDTH, 150)], fill=COLORS['accent'])
    
    title = "价值与未来规划"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 45), title, font=font_title, fill=COLORS['white'])
    
    # 内容背景
    draw.rounded_rectangle([(100, 180), (1820, 1000)], radius=30, fill=COLORS['bg_light'], outline=COLORS['accent'], width=4)
    
    items = [
        "💪 当前价值",
        "   • 随时在线的心理支持，不用等老师有空",
        "   • 减轻心理老师工作压力，提升教育效率",
        "   • 构建家校协同的心理健康教育新模式",
        "",
        "🚀 未来规划",
        "   • 优化对话能力，提供更精准的个性化辅导",
        "   • 拓展更多互动形式：心理小游戏、小故事",
        "   • 让孩子在玩中学到心理知识",
    ]
    
    y = 250
    for item in items:
        if item:
            draw.text((200, y), item, font=font_content, fill=COLORS['text_dark'])
        y += 100

def draw_end_slide(draw, img):
    """结束页"""
    # 渐变背景
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(245 + (255 - 245) * ratio)
        g = int(250 + (255 - 250) * ratio)
        b = int(245 + (255 - 245) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # 装饰
    draw.ellipse([(-100, -100), (300, 300)], fill=(*COLORS['primary'], 30))
    draw.ellipse([(1600, 800), (2000, 1200)], fill=(*COLORS['warm'], 40))
    
    # 主标题
    title = "谢谢大家！"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 400), title, font=font_title, fill=COLORS['primary_dark'])
    
    # 副标题
    subtitle = "潮潮姐——孩子身边随时能找到的心理小卫士"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - subtitle_w) / 2, 550), subtitle, font=font_subtitle, fill=COLORS['text_light'])

# 生成所有幻灯片
slides = [
    (1, "封面", draw_title_slide),
    (2, "潮潮姐是谁", draw_who_slide),
    (3, "使用场景", draw_scene_slide),
    (4, "三大功能", draw_features_slide),
    (5, "互动示例", draw_examples_slide),
    (6, "价值与未来", draw_value_slide),
    (7, "结束页", draw_end_slide),
]

for num, name, draw_func in slides:
    create_slide(num, name, draw_func)

print("\n✅ 所有幻灯片生成完成！")
print("输出目录：/home/admin/.openclaw/workspace/ppt_images/")

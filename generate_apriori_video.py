#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大数据关联规则技术教学视频生成器
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

COLORS = {
    'bg': (15, 25, 45),
    'primary': (41, 128, 185),
    'secondary': (52, 152, 219),
    'accent': (230, 126, 34),
    'success': (39, 174, 96),
    'white': (255, 255, 255),
    'gray': (150, 160, 180),
    'yellow': (243, 156, 18),
}

def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size)
    except:
        return ImageFont.load_default()

def create_title_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 背景装饰
    for i in range(20):
        x = i * 100
        draw.line([(x, 0), (x+50, VIDEO_HEIGHT)], fill=(50, 80, 120, 100), width=1)
    
    font_big = get_font(64)
    font_medium = get_font(36)
    font_small = get_font(24)
    
    draw.text((VIDEO_WIDTH//2, 280), "大数据关联规则技术", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 400), "Apriori 算法详解", fill=COLORS['white'], font=font_medium, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 700), "中职/高职计算机专业", fill=COLORS['gray'], font=font_small, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 760), "大数据技术基础课程", fill=COLORS['gray'], font=font_small, anchor="mm")
    
    return img

def create_intro_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(32)
    
    draw.text((100, 100), "什么是关联规则？", fill=COLORS['accent'], font=font_title)
    
    content = [
        "",
        "关联规则 (Association Rules)",
        "",
        "从大量数据中发现项集之间有趣的关联",
        "",
        "经典案例：啤酒与尿布",
    ]
    
    y = 200
    for line in content:
        if line:
            draw.text((150, y), line, fill=COLORS['white'], font=font_content)
        y += 60
    
    return img

def create_beer_diaper_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "经典案例：啤酒与尿布", fill=COLORS['accent'], font=font_title)
    
    # 左侧啤酒图标（简单绘制）
    draw.rectangle([(200, 250), (350, 550)], fill=(180, 140, 80), outline=(100, 80, 40), width=3)
    draw.text((225, 380), "啤酒", fill=COLORS['white'], font=get_font(28))
    
    # 右侧尿布图标
    draw.rectangle([(700, 250), (850, 550)], fill=(200, 200, 220), outline=(120, 120, 140), width=3)
    draw.text((725, 380), "尿布", fill=COLORS['dark'] if 'dark' in COLORS else (30, 30, 40), font=get_font(28))
    
    # 箭头
    draw.line([(400, 400), (650, 400)], fill=COLORS['success'], width=5)
    draw.polygon([(650, 380), (650, 420), (700, 400)], fill=COLORS['success'])
    
    # 说明文字
    desc = [
        "沃尔玛超市发现：",
        "周五下午，啤酒和尿布经常一起被购买",
        "",
        "年轻父亲们买完尿布后顺手买啤酒",
        "",
        "启示：看似不相关的商品存在隐藏关联！"
    ]
    
    y = 600
    for line in desc:
        draw.text((150, y), line, fill=COLORS['white'], font=font_content)
        y += 50
    
    return img

def create_metrics_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(26)
    font_formula = get_font(24)
    
    draw.text((100, 80), "三个核心指标", fill=COLORS['accent'], font=font_title)
    
    # 支持度
    draw.rectangle([(100, 180), (600, 340)], outline=COLORS['secondary'], width=2)
    draw.text((120, 200), "1. 支持度 (Support)", fill=COLORS['secondary'], font=get_font(28))
    draw.text((120, 250), "Support(A→B) = P(A∩B)", fill=COLORS['white'], font=font_formula)
    draw.text((120, 290), "包含 A 和 B 的交易数 / 总交易数", fill=COLORS['gray'], font=font_content)
    
    # 置信度
    draw.rectangle([(100, 360), (600, 520)], outline=COLORS['yellow'], width=2)
    draw.text((120, 380), "2. 置信度 (Confidence)", fill=COLORS['yellow'], font=get_font(28))
    draw.text((120, 430), "Confidence(A→B) = P(B|A)", fill=COLORS['white'], font=font_formula)
    draw.text((120, 470), "Support(A∩B) / Support(A)", fill=COLORS['gray'], font=font_content)
    
    # 提升度
    draw.rectangle([(100, 540), (600, 700)], outline=COLORS['success'], width=2)
    draw.text((120, 560), "3. 提升度 (Lift)", fill=COLORS['success'], font=get_font(28))
    draw.text((120, 610), "Lift(A→B) = Confidence / Support(B)", fill=COLORS['white'], font=font_formula)
    draw.text((120, 650), ">1 正相关  =1 独立  <1 负相关", fill=COLORS['gray'], font=font_content)
    
    # 右侧示例
    draw.text((680, 200), "示例计算：", fill=COLORS['accent'], font=get_font(28))
    examples = [
        "100 笔交易中 10 笔同时买啤酒和尿布",
        "支持度 = 10/100 = 10%",
        "",
        "买啤酒的 20 人中有 10 人也买了尿布",
        "置信度 = 10/20 = 50%",
        "",
        "尿布的购买率是 30%",
        "提升度 = 50%/30% = 1.67 > 1",
        "说明啤酒和尿布正相关"
    ]
    
    y = 260
    for line in examples:
        draw.text((680, y), line, fill=COLORS['white'], font=font_content)
        y += 45
    
    return img

def create_apriori_intro_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(30)
    
    draw.text((100, 100), "Apriori 算法原理", fill=COLORS['accent'], font=font_title)
    
    content = [
        "",
        "Apriori 算法 - 经典关联规则挖掘算法",
        "",
        "核心思想：",
        "• 如果一个项集是频繁的，那么它的所有子集也是频繁的",
        "• 如果一个项集是非频繁的，那么它的所有超集也是非频繁的",
        "",
        "剪枝策略：大幅减少计算量！"
    ]
    
    y = 200
    for line in content:
        draw.text((150, y), line, fill=COLORS['white'], font=font_content)
        y += 55
    
    return img

def create_apriori_example_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(44)
    font_content = get_font(24)
    
    draw.text((100, 80), "Apriori 算法执行流程", fill=COLORS['accent'], font=font_title)
    
    # 交易数据库
    draw.text((100, 160), "交易数据库：", fill=COLORS['secondary'], font=get_font(28))
    transactions = [
        "T1: {牛奶，面包，啤酒}",
        "T2: {牛奶，尿布，啤酒，可乐}",
        "T3: {牛奶，尿布，啤酒}",
        "T4: {面包，尿布，啤酒}"
    ]
    
    y = 210
    for t in transactions:
        draw.text((130, y), t, fill=COLORS['white'], font=font_content)
        y += 40
    
    # 频繁 1 项集
    draw.text((100, 340), "频繁 1 项集（最小支持度 50%）：", fill=COLORS['yellow'], font=get_font(26))
    itemsets1 = [
        "牛奶：3/4 = 75% ✓",
        "尿布：3/4 = 75% ✓",
        "啤酒：4/4 = 100% ✓",
        "面包：2/4 = 50% ✓"
    ]
    
    y = 390
    for item in itemsets1:
        draw.text((130, y), item, fill=COLORS['white'], font=font_content)
        y += 35
    
    # 频繁 2 项集
    draw.text((700, 160), "频繁 2 项集：", fill=COLORS['success'], font=get_font(28))
    itemsets2 = [
        "{牛奶，尿布}: 2/4 = 50% ✓",
        "{牛奶，啤酒}: 3/4 = 75% ✓",
        "{尿布，啤酒}: 3/4 = 75% ✓",
        "{面包，啤酒}: 2/4 = 50% ✓"
    ]
    
    y = 210
    for item in itemsets2:
        draw.text((730, y), item, fill=COLORS['white'], font=font_content)
        y += 40
    
    # 关联规则
    draw.text((700, 400), "关联规则示例：", fill=COLORS['accent'], font=get_font(26))
    rules = [
        "牛奶 → 啤酒",
        "置信度 = 3/3 = 100%",
        "",
        "尿布 → 啤酒",
        "置信度 = 3/3 = 100%"
    ]
    
    y = 450
    for rule in rules:
        draw.text((730, y), rule, fill=COLORS['white'], font=font_content)
        y += 35
    
    return img

def create_application_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "应用场景", fill=COLORS['accent'], font=font_title)
    
    apps = [
        ("电商推荐", "买了手机的人，常买手机壳和贴膜"),
        ("超市布局", "啤酒 + 尿布 → 相邻货架"),
        ("医疗诊断", "症状 A + 症状 B → 疾病 C"),
        ("金融风控", "异常交易模式检测"),
        ("社交网络", "好友推荐、内容推荐"),
    ]
    
    y = 200
    for title, desc in apps:
        draw.rectangle([(100, y), (900, y+80)], outline=COLORS['secondary'], width=2)
        draw.text((130, y+15), title, fill=COLORS['secondary'], font=get_font(26))
        draw.text((300, y+20), desc, fill=COLORS['white'], font=font_content)
        y += 100
    
    return img

def create_summary_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "知识总结", fill=COLORS['accent'], font=font_title)
    
    summary = [
        "核心概念：",
        "• 支持度 - 同时出现的概率",
        "• 置信度 - 条件概率",
        "• 提升度 - 相关性强弱",
        "",
        "Apriori 算法：",
        "• 基于频繁项集挖掘",
        "• 剪枝策略减少计算",
        "",
        "应用：推荐系统、货架布局、风控等"
    ]
    
    y = 200
    for line in summary:
        draw.text((150, y), line, fill=COLORS['white'], font=font_content)
        y += 50
    
    return img

def create_end_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_big = get_font(64)
    font_medium = get_font(32)
    
    draw.text((VIDEO_WIDTH//2, 350), "感谢观看", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 480), "敬请批评指正", fill=COLORS['white'], font=font_medium, anchor="mm")
    
    return img

def main():
    output_dir = "/home/admin/.openclaw/workspace/apriori_video_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    scenes = [
        ("片头", 5, create_title_frame),
        ("什么是关联规则", 6, create_intro_frame),
        ("啤酒与尿布案例", 8, create_beer_diaper_frame),
        ("三个核心指标", 10, create_metrics_frame),
        ("Apriori 算法原理", 7, create_apriori_intro_frame),
        ("算法执行流程", 10, create_apriori_example_frame),
        ("应用场景", 6, create_application_frame),
        ("知识总结", 5, create_summary_frame),
        ("结束页", 3, create_end_frame),
    ]
    
    frame_count = 0
    for name, duration, create_func in scenes:
        print(f"生成场景：{name} ({duration}秒)")
        img = create_func()
        
        for _ in range(duration * FPS):
            frame_path = f"{output_dir}/frame_{frame_count:05d}.png"
            img.save(frame_path)
            frame_count += 1
    
    print(f"共生成 {frame_count} 帧图像")
    
    # 合成视频
    print("正在合成视频...")
    video_path = "/home/admin/.openclaw/workspace/大数据关联规则技术教学视频.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', f'{output_dir}/frame_%05d.png',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-r', str(FPS),
        video_path
    ]
    
    subprocess.run(cmd, check=True)
    
    print(f"视频已生成：{video_path}")
    print(f"视频时长：{frame_count/FPS:.1f}秒")

if __name__ == "__main__":
    main()

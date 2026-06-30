#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新信息技术赛道参赛项目视频生成器
使用 PIL 创建帧，ffmpeg 合成视频
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

COLORS = {
    'bg': (10, 15, 40),
    'primary': (26, 35, 126),
    'secondary': (67, 97, 238),
    'accent': (0, 210, 255),
    'white': (255, 255, 255),
    'gray': (150, 160, 180),
}

def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size)
    except:
        return ImageFont.load_default()

def create_title_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 粒子效果背景
    import random
    random.seed(42)
    for _ in range(100):
        x = random.randint(0, VIDEO_WIDTH)
        y = random.randint(0, VIDEO_HEIGHT)
        size = random.randint(1, 3)
        draw.ellipse([(x, y), (x+size, y+size)], fill=(100, 150, 255, 150))
    
    # 标题
    font_big = get_font(72)
    font_medium = get_font(36)
    
    draw.text((VIDEO_WIDTH//2, 350), "智学助手", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 480), "基于 AI 的个性化学习推荐系统", fill=COLORS['white'], font=font_medium, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 800), "新信息技术赛道参赛项目", fill=COLORS['gray'], font=get_font(24), anchor="mm")
    draw.text((VIDEO_WIDTH//2, 850), "绍兴柯桥区高级技工学校", fill=COLORS['gray'], font=get_font(24), anchor="mm")
    
    return img

def create_pain_point_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(32)
    
    draw.text((100, 100), "学习痛点", fill=COLORS['accent'], font=font_title)
    
    points = [
        "学习资源过载 - 海量资源难以选择",
        "学习路径单一 - 无法满足个性化需求",
        "学习效果难评估 - 缺乏精准诊断",
        "学习动力不足 - 缺少针对性推荐",
    ]
    
    for i, point in enumerate(points):
        y = 250 + i * 120
        draw.text((150, y), point, fill=COLORS['white'], font=font_content)
    
    return img

def create_product_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "产品介绍", fill=COLORS['accent'], font=font_title)
    
    intro = "智学助手是一款面向中职学生的 AI 个性化学习推荐系统"
    draw.text((100, 200), intro, fill=COLORS['white'], font=get_font(32))
    
    features = [
        "学情精准诊断",
        "学习资源智能推荐",
        "学习路径个性化规划",
        "学习效果实时反馈",
    ]
    
    for i, feature in enumerate(features):
        x = 150 + (i % 2) * 450
        y = 350 + (i // 2) * 200
        draw.rounded_rectangle([(x, y), (x+350, y+120)], radius=15, outline=COLORS['secondary'], width=3)
        draw.text((x+175, y+60), feature, fill=COLORS['white'], font=get_font(24), anchor="mm")
    
    return img

def create_tech_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(22)
    
    draw.text((100, 80), "技术架构", fill=COLORS['accent'], font=font_title)
    
    layers = [
        ("应用层", "Web/APP/小程序/管理后台", COLORS['secondary']),
        ("服务层", "推荐引擎/用户画像/学情分析", COLORS['accent']),
        ("算法层", "协同过滤/知识图谱/NLP", COLORS['success'] if 'success' in COLORS else (0, 255, 127)),
        ("数据层", "MySQL/MongoDB/Redis", COLORS['warning'] if 'warning' in COLORS else (255, 193, 7)),
        ("基础设施", "云服务器/容器/CDN", COLORS['primary']),
    ]
    
    for i, (title, content, color) in enumerate(layers):
        y = 180 + i * 160
        draw.rounded_rectangle([(200, y), (1720, y+130)], radius=10, fill=(*color, 180), outline=color, width=2)
        draw.text((250, y+30), title, fill=COLORS['white'], font=get_font(28))
        draw.text((450, y+40), content, fill=COLORS['white'], font=font_content)
    
    return img

def create_result_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_num = get_font(56)
    font_label = get_font(24)
    
    draw.text((100, 100), "应用成效", fill=COLORS['accent'], font=font_title)
    draw.text((100, 180), "试点学校：绍兴柯桥区高级技工学校", fill=COLORS['gray'], font=get_font(24))
    
    results = [
        ("1200", "注册用户"),
        ("450", "日活跃用户"),
        ("35 分钟", "平均使用时长"),
        ("15%", "成绩提升"),
        ("92%", "用户满意度"),
    ]
    
    for i, (num, label) in enumerate(results):
        x = 200 + i * 320
        y = 350
        draw.rounded_rectangle([(x, y), (x+280, y+200)], radius=15, outline=COLORS['secondary'], width=3)
        draw.text((x+140, y+80), num, fill=COLORS['accent'], font=font_num, anchor="mm")
        draw.text((x+140, y+150), label, fill=COLORS['white'], font=font_label, anchor="mm")
    
    return img

def create_team_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "团队介绍", fill=COLORS['accent'], font=font_title)
    
    members = [
        "项目负责人 - XXX（计算机应用）",
        "技术总监 - XXX（软件工程）",
        "产品总监 - XXX（电子商务）",
        "运营总监 - XXX（市场营销）",
    ]
    
    for i, member in enumerate(members):
        y = 250 + i * 100
        draw.text((150, y), member, fill=COLORS['white'], font=font_content)
    
    draw.text((150, 650), "指导教师：何永胜（高级讲师，信息技术）", fill=COLORS['gray'], font=font_content)
    
    return img

def create_end_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_big = get_font(72)
    font_medium = get_font(36)
    font_small = get_font(24)
    
    draw.text((VIDEO_WIDTH//2, 350), "感谢观看", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 480), "敬请批评指正", fill=COLORS['white'], font=font_medium, anchor="mm")
    
    draw.text((VIDEO_WIDTH//2, 700), "智学助手", fill=COLORS['gray'], font=font_small, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 750), "绍兴柯桥区高级技工学校", fill=COLORS['gray'], font=font_small, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 800), "2026 年 4 月", fill=COLORS['gray'], font=font_small, anchor="mm")
    
    return img

def main():
    output_dir = "/home/admin/.openclaw/workspace/video_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    scenes = [
        ("片头", 5, create_title_frame),
        ("痛点引入", 8, create_pain_point_frame),
        ("产品介绍", 10, create_product_frame),
        ("技术架构", 12, create_tech_frame),
        ("应用成效", 8, create_result_frame),
        ("团队介绍", 7, create_team_frame),
        ("结束页", 5, create_end_frame),
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
    video_path = "/home/admin/.openclaw/workspace/新信息技术赛道项目演示.mp4"
    
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

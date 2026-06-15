#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能小车废弃物分拣课堂实践视频生成器
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
    'green': (46, 204, 113),
    'yellow': (243, 156, 18),
}

def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size)
    except:
        return ImageFont.load_default()

def draw_smart_car(draw, x, y, scale=1.0):
    """绘制智能小车"""
    s = scale
    # 车身
    draw.rectangle([(x, y+int(20*s)), (x+int(120*s), y+int(80*s))], fill=(60, 70, 90), outline=(100, 120, 150), width=2)
    # 车轮
    wheel_positions = [(x+int(15*s), y+int(15*s)), (x+int(105*s), y+int(15*s)), (x+int(15*s), y+int(85*s)), (x+int(105*s), y+int(85*s))]
    for wx, wy in wheel_positions:
        draw.ellipse([(wx, wy), (wx+int(20*s), wy+int(20*s))], fill=(40, 40, 50), outline=(80, 80, 90))
    # 传感器
    draw.rectangle([(x+int(110*s), y+int(40*s)), (x+int(130*s), y+int(60*s))], fill=(100, 150, 200))
    # 机械臂
    draw.line([(x+int(60*s), y+int(50*s)), (x+int(60*s), y+int(20*s))], fill=(120, 120, 130), width=int(4*s))
    draw.line([(x+int(60*s), y+int(20*s)), (x+int(90*s), y+int(10*s))], fill=(120, 120, 130), width=int(3*s))

def draw_waste(draw, x, y, waste_type):
    """绘制废弃物"""
    if waste_type == 'recyclable':
        # 可回收物（蓝色）
        draw.rectangle([(x, y), (x+30, y+30)], fill=(52, 152, 219), outline=(255, 255, 255))
    elif waste_type == 'hazardous':
        # 有害垃圾（红色）
        draw.ellipse([(x, y), (x+30, y+30)], fill=(231, 76, 60), outline=(255, 255, 255))
    elif waste_type == 'kitchen':
        # 厨余垃圾（绿色）
        draw.polygon([(x+15, y), (x+30, y+30), (x, y+30)], fill=(39, 174, 96), outline=(255, 255, 255))
    else:
        # 其他垃圾（灰色）
        draw.rectangle([(x, y), (x+30, y+30)], fill=(150, 150, 150), outline=(255, 255, 255))

def create_title_frame():
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 背景装饰
    for i in range(30):
        x = i * 70
        draw.line([(x, 0), (x+30, VIDEO_HEIGHT)], fill=(50, 80, 120, 80), width=1)
    
    font_big = get_font(56)
    font_medium = get_font(32)
    
    draw.text((VIDEO_WIDTH//2, 280), "智能小车废弃物分拣", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 380), "课堂实践展示", fill=COLORS['white'], font=font_medium, anchor="mm")
    
    # 绘制小车
    draw_smart_car(draw, VIDEO_WIDTH//2 - 80, 500, scale=1.2)
    
    # 废弃物
    draw_waste(draw, VIDEO_WIDTH//2 - 150, 600, 'recyclable')
    draw_waste(draw, VIDEO_WIDTH//2 - 50, 600, 'hazardous')
    draw_waste(draw, VIDEO_WIDTH//2 + 50, 600, 'kitchen')
    draw_waste(draw, VIDEO_WIDTH//2 + 150, 600, 'other')
    
    draw.text((VIDEO_WIDTH//2, 750), "编程教学变革 × 育人逻辑重构", fill=COLORS['gray'], font=font_medium, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 820), "绍兴柯桥职校 · 2026 年 4 月", fill=COLORS['gray'], font=get_font(24), anchor="mm")
    
    return img

def create_scene1_frame():
    """双真驱动场景"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(28)
    
    draw.text((100, 100), "双真驱动 · 打破认知壁垒", fill=COLORS['accent'], font=font_title)
    
    # 左侧：真实场景
    draw.rectangle([(100, 200), (550, 550)], outline=COLORS['secondary'], width=3)
    draw.text((120, 220), "真实场景", fill=COLORS['secondary'], font=get_font(32))
    draw.text((120, 280), "• 垃圾分类实际场景", fill=COLORS['white'], font=font_content)
    draw.text((120, 330), "• 环保政策背景", fill=COLORS['white'], font=font_content)
    draw.text((120, 380), "• 社会现实需求", fill=COLORS['white'], font=font_content)
    
    # 右侧：真实任务
    draw.rectangle([(650, 200), (1100, 550)], outline=COLORS['success'], width=3)
    draw.text((670, 220), "真实任务", fill=COLORS['success'], font=get_font(32))
    draw.text((670, 280), "• 智能小车编程", fill=COLORS['white'], font=font_content)
    draw.text((670, 330), "• 传感器应用", fill=COLORS['white'], font=font_content)
    draw.text((670, 380), "• 机械臂控制", fill=COLORS['white'], font=font_content)
    
    # 中间箭头
    draw.polygon([(600, 350), (630, 375), (600, 400)], fill=COLORS['accent'])
    
    # 底部小车
    draw_smart_car(draw, 1200, 600, scale=1.0)
    
    return img

def create_scene2_frame():
    """支架迭代场景"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(26)
    
    draw.text((100, 100), "支架迭代 · 铺就成长阶梯", fill=COLORS['accent'], font=font_title)
    
    # 阶梯图
    steps = [
        ("基础认知", "Python 语法基础", COLORS['primary']),
        ("传感器应用", "红外/超声波传感器", COLORS['secondary']),
        ("逻辑编程", "条件判断/循环", COLORS['accent']),
        ("综合应用", "完整项目实现", COLORS['success']),
    ]
    
    for i, (title, desc, color) in enumerate(steps):
        x = 200 + i * 280
        y = 600 - i * 100
        draw.rectangle([(x, y), (x+250, y+80)], fill=(*color, 150), outline=color, width=2)
        draw.text((x+125, y+25), title, fill=COLORS['white'], font=get_font(24), anchor="mm")
        draw.text((x+125, y+55), desc, fill=COLORS['gray'], font=font_content, anchor="mm")
        
        # 阶梯连接线
        if i < len(steps) - 1:
            draw.line([(x+250, y+40), (x+280, y+40)], fill=color, width=3)
            draw.polygon([(x+280, y+30), (x+300, y+40), (x+280, y+50)], fill=color)
    
    draw.text((100, 200), "层层递进 · 步步提升", fill=COLORS['gray'], font=get_font(32))
    
    return img

def create_scene3_frame():
    """点线融通场景"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_content = get_font(26)
    
    draw.text((100, 100), "点线融通 · 重塑价值坐标", fill=COLORS['accent'], font=font_title)
    
    # 知识点
    points = [
        "编程逻辑",
        "硬件控制",
        "算法思维",
        "团队协作",
        "问题解决",
        "创新意识",
    ]
    
    for i, point in enumerate(points):
        x = 200 + (i % 3) * 300
        y = 250 + (i // 3) * 150
        draw.ellipse([(x, y), (x+120, y+120)], outline=COLORS['secondary'], width=2)
        draw.text((x+60, y+50), point, fill=COLORS['white'], font=get_font(20), anchor="mm")
    
    # 连接线
    draw.line([(260, 310), (560, 310)], fill=COLORS['accent'], width=2)
    draw.line([(560, 310), (860, 310)], fill=COLORS['accent'], width=2)
    draw.line([(260, 460), (560, 460)], fill=COLORS['accent'], width=2)
    draw.line([(560, 460), (860, 460)], fill=COLORS['accent'], width=2)
    draw.line([(560, 310), (560, 460)], fill=COLORS['accent'], width=2)
    
    draw.text((100, 600), "从知识点 → 能力线 → 素养面", fill=COLORS['gray'], font=font_content)
    draw.text((100, 660), "培养全面发展的高素质技术技能人才", fill=COLORS['success'], font=get_font(28))
    
    return img

def create_code_frame():
    """代码与温度"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(48)
    font_code = get_font(20)
    font_text = get_font(32)
    
    draw.text((100, 100), "编程不止于逻辑", fill=COLORS['accent'], font=font_title)
    
    # 代码框
    draw.rectangle([(100, 180), (900, 600)], outline=COLORS['secondary'], width=2)
    
    code = """
# 智能小车废弃物分拣程序
def sort_waste(waste_type):
    \"\"\"让每一行代码都有温度\"\"\"
    if waste_type == 'recyclable':
        move_to_bin('blue')    # 可回收物
    elif waste_type == 'hazardous':
        move_to_bin('red')     # 有害垃圾
    elif waste_type == 'kitchen':
        move_to_bin('green')   # 厨余垃圾
    else:
        move_to_bin('gray')    # 其他垃圾
    
    # 每一个小车的转向，都指向未来
    return "环保未来"
"""
    
    draw.text((130, 210), code, fill=COLORS['success'], font=font_code)
    
    # 右侧文字
    draw.text((950, 250), "教育不止于课堂", fill=COLORS['white'], font=font_text)
    draw.text((950, 350), "让每一行代码都有温度", fill=COLORS['accent'], font=font_text)
    draw.text((950, 450), "让每一个小车的转向", fill=COLORS['secondary'], font=font_text)
    draw.text((950, 550), "都指向未来", fill=COLORS['success'], font=font_text)
    
    return img

def create_ending_frame():
    """结语"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    font_big = get_font(52)
    font_medium = get_font(36)
    font_small = get_font(24)
    
    # 背景装饰
    for i in range(20):
        x = i * 100
        draw.line([(x, 0), (x+50, VIDEO_HEIGHT)], fill=(50, 80, 120, 60), width=1)
    
    # 主标题
    draw.text((VIDEO_WIDTH//2, 200), "以码为阶", fill=COLORS['accent'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 300), "封装未来", fill=COLORS['success'], font=font_big, anchor="mm")
    
    # 小车
    draw_smart_car(draw, VIDEO_WIDTH//2 - 60, 400, scale=1.0)
    
    # 结语文字
    lines = [
        "《智能小车废弃物分拣》的课堂实践",
        "不仅是一场编程教学的精心变革",
        "更是一次育人逻辑的深度重构",
        "",
        "双真驱动 · 支架迭代 · 点线融通",
        "",
        "编程不止于逻辑，教育不止于课堂",
    ]
    
    y = 580
    for line in lines:
        if line:
            draw.text((VIDEO_WIDTH//2, y), line, fill=COLORS['white'], font=font_small, anchor="mm")
        y += 45
    
    draw.text((VIDEO_WIDTH//2, 900), "绍兴柯桥职校", fill=COLORS['gray'], font=get_font(20), anchor="mm")
    draw.text((VIDEO_WIDTH//2, 940), "2026 年 4 月", fill=COLORS['gray'], font=get_font(20), anchor="mm")
    
    return img

def main():
    output_dir = "/home/admin/.openclaw/workspace/smart_car_video_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    scenes = [
        ("片头", 5, create_title_frame),
        ("双真驱动", 6, create_scene1_frame),
        ("支架迭代", 6, create_scene2_frame),
        ("点线融通", 6, create_scene3_frame),
        ("代码温度", 6, create_code_frame),
        ("结语", 6, create_ending_frame),
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
    video_path = "/home/admin/.openclaw/workspace/智能小车废弃物分拣课堂实践.mp4"
    
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

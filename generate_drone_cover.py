#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无人机操控与维护专业建设方案封面图生成器
"""

from PIL import Image, ImageDraw, ImageFont
import math

# 图片参数
WIDTH = 1920
HEIGHT = 1080

# 颜色定义
COLORS = {
    'sky_dark': (15, 32, 60),        # 深空蓝
    'sky_light': (41, 128, 185),     # 天空蓝
    'accent_orange': (230, 126, 34), # 橙色
    'white': (255, 255, 255),        # 白色
    'gray': (180, 190, 200),         # 灰色
    'green': (39, 174, 96),          # 绿色
}

def get_font(size):
    """获取字体"""
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", size)
        except:
            return ImageFont.load_default()

def draw_drone_silhouette(draw, center_x, center_y, scale=1.0):
    """绘制无人机剪影"""
    s = scale  # 缩放因子
    
    # 无人机主体（俯视图）
    # 中心机身
    body_points = [
        (center_x - 15*s, center_y - 40*s),
        (center_x + 15*s, center_y - 40*s),
        (center_x + 20*s, center_y),
        (center_x + 15*s, center_y + 40*s),
        (center_x - 15*s, center_y + 40*s),
        (center_x - 20*s, center_y),
    ]
    draw.polygon(body_points, fill=(60, 70, 90), outline=(100, 120, 150))
    
    # 四个机臂
    arm_length = 120 * s
    arm_width = 12 * s
    
    # 左上机臂
    draw.line([
        (center_x - 10*s, center_y - 20*s),
        (center_x - arm_length*0.7, center_y - arm_length*0.7)
    ], fill=(80, 90, 110), width=int(arm_width))
    
    # 右上机臂
    draw.line([
        (center_x + 10*s, center_y - 20*s),
        (center_x + arm_length*0.7, center_y - arm_length*0.7)
    ], fill=(80, 90, 110), width=int(arm_width))
    
    # 左下机臂
    draw.line([
        (center_x - 10*s, center_y + 20*s),
        (center_x - arm_length*0.7, center_y + arm_length*0.7)
    ], fill=(80, 90, 110), width=int(arm_width))
    
    # 右下机臂
    draw.line([
        (center_x + 10*s, center_y + 20*s),
        (center_x + arm_length*0.7, center_y + arm_length*0.7)
    ], fill=(80, 90, 110), width=int(arm_width))
    
    # 四个电机/螺旋桨
    motor_positions = [
        (center_x - arm_length*0.7, center_y - arm_length*0.7),
        (center_x + arm_length*0.7, center_y - arm_length*0.7),
        (center_x - arm_length*0.7, center_y + arm_length*0.7),
        (center_x + arm_length*0.7, center_y + arm_length*0.7),
    ]
    
    for mx, my in motor_positions:
        # 电机
        draw.ellipse([
            (mx - 15*s, my - 15*s),
            (mx + 15*s, my + 15*s)
        ], fill=(50, 60, 80), outline=(90, 100, 120))
        
        # 螺旋桨（半透明效果）
        draw.ellipse([
            (mx - 25*s, my - 25*s),
            (mx + 25*s, my + 25*s)
        ], fill=(100, 120, 150, 180), outline=(130, 150, 180))

def draw_grid_lines(draw, width, height):
    """绘制网格线"""
    # 水平线
    for i in range(0, height, 60):
        alpha = 30 if i % 120 == 0 else 15
        draw.line([(0, i), (width, i)], fill=(100, 150, 200, alpha), width=1)
    
    # 垂直线
    for i in range(0, width, 80):
        alpha = 30 if i % 160 == 0 else 15
        draw.line([(i, 0), (i, height)], fill=(100, 150, 200, alpha), width=1)

def draw_decorative_elements(draw, width, height):
    """绘制装饰元素"""
    # 左上角六边形
    hex_center = (80, 80)
    hex_size = 40
    hex_points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = hex_center[0] + hex_size * math.cos(angle)
        y = hex_center[1] + hex_size * math.sin(angle)
        hex_points.append((x, y))
    draw.polygon(hex_points, outline=(100, 180, 255), width=2)
    
    # 右上角六边形
    hex_center = (width - 80, 80)
    hex_points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        x = hex_center[0] + hex_size * math.cos(angle)
        y = hex_center[1] + hex_size * math.sin(angle)
        hex_points.append((x, y))
    draw.polygon(hex_points, outline=(100, 180, 255), width=2)
    
    # 左下角装饰线
    draw.line([(50, height-50), (150, height-50)], fill=(230, 126, 34), width=3)
    draw.line([(50, height-30), (120, height-30)], fill=(230, 126, 34), width=2)
    
    # 右下角装饰线
    draw.line([(width-150, height-50), (width-50, height-50)], fill=(230, 126, 34), width=3)
    draw.line([(width-120, height-30), (width-50, height-30)], fill=(230, 126, 34), width=2)
    
    # 散落的点装饰
    import random
    random.seed(42)  # 固定随机种子
    for _ in range(30):
        x = random.randint(100, width-100)
        y = random.randint(100, height-100)
        size = random.randint(2, 5)
        draw.ellipse([(x, y), (x+size, y+size)], fill=(100, 180, 255, 150))

def create_cover():
    """创建封面图"""
    # 创建背景（渐变）
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['sky_dark'])
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLORS['sky_dark'][0] + (COLORS['sky_light'][0] - COLORS['sky_dark'][0]) * ratio * 0.5)
        g = int(COLORS['sky_dark'][1] + (COLORS['sky_light'][1] - COLORS['sky_dark'][1]) * ratio * 0.5)
        b = int(COLORS['sky_dark'][2] + (COLORS['sky_light'][2] - COLORS['sky_dark'][2]) * ratio * 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # 绘制网格
    draw_grid_lines(draw, WIDTH, HEIGHT)
    
    # 绘制装饰元素
    draw_decorative_elements(draw, WIDTH, HEIGHT)
    
    # 绘制无人机剪影（中央）
    draw_drone_silhouette(draw, WIDTH//2, HEIGHT//2 - 50, scale=1.5)
    
    # 绘制底部色块
    draw.rectangle([(0, HEIGHT-200), (WIDTH, HEIGHT)], fill=(10, 20, 40))
    
    # 添加文字
    font_title = get_font(72)
    font_subtitle = get_font(36)
    font_info = get_font(28)
    font_small = get_font(22)
    
    # 主标题
    title = "无人机操控与维护"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    draw.text((title_x, 120), title, fill=COLORS['white'], font=font_title)
    
    # 副标题
    subtitle = "专业建设方案"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2
    draw.text((subtitle_x, 220), subtitle, fill=COLORS['accent_orange'], font=font_subtitle)
    
    # 装饰线
    line_start = (WIDTH - 400) // 2
    draw.line([(line_start, 290), (line_start + 400, 290)], fill=COLORS['accent_orange'], width=3)
    
    # 底部信息
    info_lines = [
        "中职/高职装备制造大类专业",
        "专业代码：710305",
        "绍兴柯桥职业学校 · 2026 年 4 月",
    ]
    
    for i, info in enumerate(info_lines):
        info_bbox = draw.textbbox((0, 0), info, font=font_info)
        info_width = info_bbox[2] - info_bbox[0]
        info_x = (WIDTH - info_width) // 2
        y_pos = HEIGHT - 140 + i * 40
        draw.text((info_x, y_pos), info, fill=COLORS['gray'], font=font_info)
    
    # 右下角版本号
    version = "V1.0"
    draw.text((WIDTH - 100, HEIGHT - 40), version, fill=COLORS['gray'], font=font_small)
    
    # 保存文件
    output_path = '/home/admin/.openclaw/workspace/无人机专业建设方案封面.png'
    img.save(output_path, 'PNG', quality=95)
    print(f"封面图已生成：{output_path}")
    print(f"尺寸：{WIDTH}x{HEIGHT}")
    
    return output_path

if __name__ == "__main__":
    create_cover()

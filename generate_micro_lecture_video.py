#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大数据关联规则技术微课视频生成器
生成 MP4 格式微课视频
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

# 视频参数
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# 颜色定义
COLORS = {
    'bg': (245, 247, 250),        # 浅灰背景
    'primary': (41, 128, 185),     # 蓝色
    'dark': (44, 62, 80),          # 深蓝灰
    'white': (255, 255, 255),      # 白色
    'accent': (231, 76, 60),       # 红色
    'success': (39, 174, 96),      # 绿色
    'gray': (127, 140, 141),       # 灰色
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

def create_frame(text_lines, title="", bg_color=COLORS['bg'], highlight=None):
    """创建单帧图像"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 顶部标题栏
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 100)], fill=COLORS['primary'])
    
    # 标题
    font_title = get_font(40)
    draw.text((50, 30), title, fill=COLORS['white'], font=font_title)
    
    # 内容
    font_content = get_font(32)
    font_small = get_font(24)
    
    y = 150
    for i, line in enumerate(text_lines):
        if isinstance(line, dict):
            # 特殊格式
            if line.get('type') == 'formula':
                # 公式框
                x1, y1 = 100, y
                x2, y2 = VIDEO_WIDTH - 100, y + 80
                draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=10, fill=COLORS['white'], outline=COLORS['primary'], width=3)
                draw.text((VIDEO_WIDTH//2, y + 40), line['text'], fill=COLORS['dark'], font=font_content, anchor="mm")
                y += 100
            elif line.get('type') == 'highlight':
                draw.text((100, y), line['text'], fill=COLORS['accent'], font=font_content)
                y += 60
            elif line.get('type') == 'success':
                draw.text((100, y), line['text'], fill=COLORS['success'], font=font_content)
                y += 60
        else:
            draw.text((100, y), line, fill=COLORS['dark'], font=font_content)
            y += 55
    
    # 页码
    draw.text((VIDEO_WIDTH - 100, VIDEO_HEIGHT - 40), "大数据关联规则技术", fill=COLORS['gray'], font=font_small, anchor="rm")
    
    return img

def create_title_frame():
    """创建封面帧"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['primary'])
    draw = ImageDraw.Draw(img)
    
    font_big = get_font(72)
    font_medium = get_font(40)
    font_small = get_font(28)
    
    # 主标题
    draw.text((VIDEO_WIDTH//2, 300), "大数据关联规则技术", fill=COLORS['white'], font=font_big, anchor="mm")
    
    # 副标题
    subtitle = "—— 发现数据中的购物秘密"
    draw.text((VIDEO_WIDTH//2, 420), subtitle, fill=COLORS['white'], font=font_medium, anchor="mm")
    
    # 装饰线
    draw.line([(VIDEO_WIDTH//2 - 300, 500), (VIDEO_WIDTH//2 + 300, 500)], fill=COLORS['white'], width=3)
    
    # 底部信息
    draw.text((VIDEO_WIDTH//2, 700), "微课时长：8 分钟", fill=COLORS['white'], font=font_small, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 760), "适用对象：中职/高职计算机专业", fill=COLORS['white'], font=font_small, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 820), "2026 年 4 月", fill=COLORS['white'], font=font_small, anchor="mm")
    
    return img

def create_end_frame():
    """创建结束帧"""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), COLORS['primary'])
    draw = ImageDraw.Draw(img)
    
    font_big = get_font(72)
    font_medium = get_font(40)
    
    draw.text((VIDEO_WIDTH//2, 400), "感谢观看", fill=COLORS['white'], font=font_big, anchor="mm")
    draw.text((VIDEO_WIDTH//2, 520), "敬请批评指正", fill=COLORS['white'], font=font_medium, anchor="mm")
    
    return img

def main():
    output_dir = "/home/admin/.openclaw/workspace/video_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义所有场景
    scenes = [
        # 场景 1: 封面 (5 秒)
        {
            "title": "封面",
            "duration": 5,
            "create": lambda: create_title_frame()
        },
        
        # 场景 2: 情境导入 (1 分钟)
        {
            "title": "情境导入 - 啤酒与尿布",
            "duration": 8,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "经典案例：啤酒与尿布"},
                "",
                "沃尔玛超市发现：",
                "- 周五下午，啤酒和尿布经常一起被购买",
                "- 年轻父亲们买完尿布后顺手买啤酒",
                "",
                {"type": "success", "text": "启示：看似不相关的商品存在隐藏关联！"},
            ], "1. 情境导入")
        },
        
        {
            "title": "什么是关联规则",
            "duration": 6,
            "create": lambda: create_frame([
                "关联规则 (Association Rules)",
                "",
                "定义：从大量数据中发现项集之间有趣的关联",
                "",
                "典型应用场景：",
                "- 购物篮分析 - 商品推荐",
                "- 网页推荐 - 看了又看",
                "- 医疗诊断 - 症状与疾病关联",
                "- 金融风控 - 异常交易检测",
            ], "1. 情境导入")
        },
        
        # 场景 3: 核心概念 (2 分钟)
        {
            "title": "核心概念 - 支持度",
            "duration": 7,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "三个核心指标"},
                "",
                "1 支持度 (Support)",
                "",
                {"type": "formula", "text": "Support(A->B) = P(A 交 B) = 包含 A 和 B 的交易数 / 总交易数"},
                "",
                "含义：A 和 B 同时出现的概率",
                "例：100 笔交易中 10 笔同时买啤酒和尿布",
                {"type": "success", "text": "支持度 = 10/100 = 10%"},
            ], "2. 核心概念")
        },
        
        {
            "title": "核心概念 - 置信度",
            "duration": 7,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "三个核心指标"},
                "",
                "2 置信度 (Confidence)",
                "",
                {"type": "formula", "text": "Confidence(A->B) = P(B|A) = Support(A 交 B) / Support(A)"},
                "",
                "含义：买了 A 的人中有多少也买了 B",
                "例：买啤酒的 20 人中有 10 人也买了尿布",
                {"type": "success", "text": "置信度 = 10/20 = 50%"},
            ], "2. 核心概念")
        },
        
        {
            "title": "核心概念 - 提升度",
            "duration": 7,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "三个核心指标"},
                "",
                "3 提升度 (Lift)",
                "",
                {"type": "formula", "text": "Lift(A->B) = Confidence(A->B) / Support(B)"},
                "",
                "含义：A 的出现对 B 出现概率的提升程度",
                "- Lift > 1：正相关（有促进作用）",
                "- Lift = 1：独立（无关联）",
                "- Lift < 1：负相关（有抑制作用）",
            ], "2. 核心概念")
        },
        
        # 场景 4: Apriori 算法 (3 分钟)
        {
            "title": "Apriori 算法原理",
            "duration": 8,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "Apriori 算法 - 经典关联规则挖掘算法"},
                "",
                "核心思想：",
                "- 如果一个项集是频繁的，那么它的所有子集也是频繁的",
                "- 如果一个项集是非频繁的，那么它的所有超集也是非频繁的",
                "",
                {"type": "success", "text": "剪枝策略：大幅减少计算量！"},
                "",
                "算法步骤：",
                "1. 找出所有频繁项集  2. 生成关联规则",
            ], "3. Apriori 算法")
        },
        
        {
            "title": "Apriori 算法流程",
            "duration": 8,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "算法执行流程"},
                "",
                "交易数据库：",
                "T1: {牛奶，面包，啤酒}",
                "T2: {牛奶，尿布，啤酒，可乐}",
                "T3: {牛奶，尿布，啤酒}",
                "T4: {面包，尿布，啤酒}",
                "",
                "最小支持度 = 50%",
                {"type": "success", "text": "频繁 1 项集：牛奶 (75%), 尿布 (75%), 啤酒 (100%)"},
            ], "3. Apriori 算法")
        },
        
        {
            "title": "Apriori 算法流程 2",
            "duration": 8,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "生成频繁 2 项集"},
                "",
                "候选 2 项集：",
                "- {牛奶，尿布}: 50% 通过",
                "- {牛奶，啤酒}: 75% 通过",
                "- {尿布，啤酒}: 75% 通过",
                "",
                {"type": "success", "text": "所有候选都满足最小支持度！"},
                "",
                "继续生成 3 项集...",
            ], "3. Apriori 算法")
        },
        
        # 场景 5: 应用案例 (1.5 分钟)
        {
            "title": "应用案例 - 电商推荐",
            "duration": 7,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "应用场景 1：电商推荐系统"},
                "",
                "淘宝/京东的猜你喜欢：",
                "- 买了手机的人，常买手机壳和贴膜",
                "- 买了奶粉的人，常买纸尿裤",
                "",
                "推荐策略：",
                "- 捆绑销售：手机 + 壳 + 膜 套餐优惠",
                "- 交叉推荐：购物车页面推荐相关商品",
                "- 精准营销：根据历史行为推送优惠券",
            ], "4. 应用案例")
        },
        
        {
            "title": "应用案例 - 超市布局",
            "duration": 7,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "应用场景 2：超市货架布局"},
                "",
                "优化策略：",
                "- 关联商品就近摆放 -> 提高客单价",
                "- 强关联商品分开摆放 -> 增加走动距离",
                "",
                "实际案例：",
                "- 啤酒 + 尿布 -> 相邻货架",
                "- 意面 + 意面酱 -> 相邻货架",
                "- 牙膏 + 牙刷 -> 相邻货架",
            ], "4. 应用案例")
        },
        
        # 场景 6: 总结 (0.5 分钟)
        {
            "title": "知识总结",
            "duration": 6,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "本节要点回顾"},
                "",
                "核心概念：",
                "- 支持度 - 同时出现的概率",
                "- 置信度 - 条件概率",
                "- 提升度 - 相关性强弱",
                "",
                "Apriori 算法：",
                "- 基于频繁项集挖掘",
                "- 剪枝策略减少计算",
                "",
                "应用场景：推荐系统、货架布局、风控等",
            ], "5. 总结")
        },
        
        {
            "title": "课后任务",
            "duration": 5,
            "create": lambda: create_frame([
                {"type": "highlight", "text": "课后拓展任务"},
                "",
                "基础题：",
                "- 计算给定数据集的支持度、置信度、提升度",
                "",
                "提高题：",
                "- 使用 Python 实现 Apriori 算法",
                "- 分析电商数据集，找出热门商品组合",
                "",
                {"type": "success", "text": "推荐工具：mlxtend 库、Orange 数据挖掘工具"},
            ], "5. 总结")
        },
        
        # 场景 7: 结束
        {
            "title": "结束",
            "duration": 3,
            "create": lambda: create_end_frame()
        },
    ]
    
    # 生成所有帧
    frame_count = 0
    for scene in scenes:
        print(f"生成场景：{scene['title']} ({scene['duration']}秒)")
        img = scene['create']()
        
        # 为该场景生成指定数量的帧
        frames_for_scene = scene['duration'] * FPS
        for i in range(frames_for_scene):
            frame_path = f"{output_dir}/frame_{frame_count:05d}.png"
            img.save(frame_path)
            frame_count += 1
    
    print(f"共生成 {frame_count} 帧图像")
    
    # 使用 ffmpeg 合成视频
    print("正在合成视频...")
    video_path = "/home/admin/.openclaw/workspace/大数据关联规则技术微课.mp4"
    
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

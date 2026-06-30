#!/usr/bin/env python3
"""
编辑工程图纸：移除表格中的"子项名称"行
"""
from PIL import Image, ImageDraw
import os

# 输入输出路径
input_path = '/home/admin/.openclaw/media/inbound/5fec2b5b-e433-4172-86f6-91f0f2273d06.jpg'
output_dir = '/home/admin/.openclaw/workspace/edited_blueprints'
os.makedirs(output_dir, exist_ok=True)

# 打开图片
img = Image.open(input_path)
# 转换为 RGB 模式（如果原来是 RGBA）
if img.mode == 'RGBA':
    img = img.convert('RGB')
width, height = img.size
print(f"图片尺寸：{width} x {height}, 模式：{img.mode}")

# 创建绘图对象
draw = ImageDraw.Draw(img)

# 表格在右下角，需要移除"子项名称"这一行
# 根据图片分析，表格大约在右下角区域
# 我们需要用白色覆盖"子项名称：地下室"这一行

# 估算表格位置（根据典型工程图纸布局）
# 表格右边框距离右边缘约 5%，下边框距离下边缘约 5%
# 表格高度约占图片的 15-20%

# 定义需要覆盖的区域（子项名称行）
# 这些坐标需要根据实际图片调整
table_right = width - 50  # 距离右边缘 50 像素
table_bottom = height - 50  # 距离下边缘 50 像素
table_left = width - 500  # 表格左边界
table_top = height - 250  # 表格上边界

# 子项名称行大约在表格的中间位置
# 工程项目是第一行，子项名称是第二行
subitem_row_top = height - 180
subitem_row_bottom = height - 120

# 用白色填充覆盖"子项名称"这一行
draw.rectangle(
    [(table_left, subitem_row_top), (table_right, subitem_row_bottom)],
    fill='white'
)

# 重新绘制表格线（保留边框）
# 绘制工程项目行的下边框
draw.line(
    [(table_left, subitem_row_top), (table_right, subitem_row_top)],
    fill='black',
    width=1
)

# 绘制子项名称行的下边框（现在这行变成空白了）
draw.line(
    [(table_left, subitem_row_bottom), (table_right, subitem_row_bottom)],
    fill='black',
    width=1
)

# 保存修改后的图片
output_path = os.path.join(output_dir, 'edited_5fec2b5b.jpg')
img.save(output_path, quality=95)
print(f"已保存编辑后的图片：{output_path}")

# 同时保存为 PNG 格式
output_path_png = os.path.join(output_dir, 'edited_5fec2b5b.png')
img.save(output_path_png)
print(f"已保存 PNG 格式：{output_path_png}")

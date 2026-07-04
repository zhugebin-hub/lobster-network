#!/usr/bin/env python3
"""
编辑工程图纸：移除表格中的"子项名称 地下室"行
"""
from PIL import Image, ImageDraw
import os

# 输入输出路径
input_path = '/home/admin/.openclaw/media/inbound/2aee507c-7da4-43c7-b1b3-cb533900237d.jpg'
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

# 根据图片分析，表格在右下角
# 需要移除"子项名称 地下室"这一行（第二行）
# 保留"工程项目 来凤县养老体系建设项目"（第一行）
# 保留"土方开挖阶段施工总平面布置图"（标题）

# 估算表格位置
table_right = width - 80  # 距离右边缘
table_bottom = height - 80  # 距离下边缘
table_left = int(width * 0.65)  # 表格左边界（约 65% 宽度处）
table_top = height - 220  # 表格上边界

# 子项名称行的位置（第二行）
# 第一行：工程项目
# 第二行：子项名称（需要移除）
# 第三部分：图名

subitem_row_top = height - 165  # 子项名称行上边界
subitem_row_bottom = height - 125  # 子项名称行下边界

print(f"表格区域：左={table_left}, 右={table_right}, 上={table_top}, 下={table_bottom}")
print(f"子项名称行：上={subitem_row_top}, 下={subitem_row_bottom}")

# 用白色填充覆盖"子项名称 地下室"这一行
draw.rectangle(
    [(table_left, subitem_row_top), (table_right, subitem_row_bottom)],
    fill='white'
)

# 重新绘制表格线
# 绘制工程项目行的下边框（保留）
draw.line(
    [(table_left, height - 165), (table_right, height - 165)],
    fill='black',
    width=1
)

# 绘制子项名称行的下边框（现在这行变成空白了，但保留边框线）
draw.line(
    [(table_left, subitem_row_bottom), (table_right, subitem_row_bottom)],
    fill='black',
    width=1
)

# 保存修改后的图片
output_path_png = os.path.join(output_dir, 'edited_2aee507c.png')
img.save(output_path_png)
print(f"已保存编辑后的图片：{output_path_png}")

# 也保存为 JPG
output_path_jpg = os.path.join(output_dir, 'edited_2aee507c.jpg')
img.save(output_path_jpg, quality=95)
print(f"已保存 JPG 格式：{output_path_jpg}")

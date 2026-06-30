#!/usr/bin/env python3
"""
编辑工程图纸：移除蓝色标记区域（子项名称行）
"""
from PIL import Image, ImageDraw
import os

# 输入输出路径
input_path = '/home/admin/.openclaw/media/inbound/c17f9884-790e-44f7-8cbf-a8d8c338dcd9.jpg'
output_dir = '/home/admin/.openclaw/workspace/edited_blueprints'
os.makedirs(output_dir, exist_ok=True)

# 打开图片
img = Image.open(input_path)
width, height = img.size
print(f"图片尺寸：{width} x {height}, 模式：{img.mode}")

# 创建绘图对象
draw = ImageDraw.Draw(img)

# 蓝色区域在表格的第二行（子项名称行）
# 根据图片，蓝色区域大约从表格左边界到右边界
# 位置在"工程项目"行下方，"土方开挖阶段..."标题上方

# 估算蓝色区域位置
table_left = int(width * 0.65)  # 表格左边界
table_right = width - 80  # 表格右边界

# 蓝色区域（子项名称行）的位置
blue_area_top = height - 165  # 蓝色区域上边界
blue_area_bottom = height - 125  # 蓝色区域下边界

print(f"蓝色区域：左={table_left}, 右={table_right}, 上={blue_area_top}, 下={blue_area_bottom}")

# 用白色填充覆盖蓝色区域
draw.rectangle(
    [(table_left, blue_area_top), (table_right, blue_area_bottom)],
    fill='white'
)

# 重新绘制表格边框线
# 绘制工程项目行的下边框
draw.line(
    [(table_left, blue_area_top), (table_right, blue_area_top)],
    fill='black',
    width=1
)

# 绘制子项名称行的下边框（保留边框）
draw.line(
    [(table_left, blue_area_bottom), (table_right, blue_area_bottom)],
    fill='black',
    width=1
)

# 保存修改后的图片
output_path_png = os.path.join(output_dir, 'edited_c17f9884.png')
img.save(output_path_png)
print(f"已保存编辑后的图片：{output_path_png}")

# 也保存为 JPG
output_path_jpg = os.path.join(output_dir, 'edited_c17f9884.jpg')
img.save(output_path_jpg, quality=95)
print(f"已保存 JPG 格式：{output_path_jpg}")

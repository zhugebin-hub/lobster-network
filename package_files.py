#!/usr/bin/env python3
import zipfile
import os

os.chdir('/home/admin/.openclaw/workspace')

files = [
    '成员 4-房价与违约率双轴图.png',
    '成员 4-房价下跌触发危机与真实案例.docx',
    '成员 4-任务完成说明.md'
]

with zipfile.ZipFile('成员 4-任务完整材料.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files:
        if os.path.exists(file):
            zipf.write(file)
            print(f'已添加：{file}')
        else:
            print(f'文件不存在：{file}')

print('打包完成：成员 4-任务完整材料.zip')

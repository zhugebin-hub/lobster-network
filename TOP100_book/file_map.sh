#!/bin/bash
SRC="/home/admin/.openclaw/media/inbound/TOP100_extracted/TOP100校内案例"
OUT="/home/admin/.openclaw/workspace/TOP100_book/chapters"
mkdir -p "$OUT"

# 序
pandoc "$SRC/（沈剑军）与\"豆包\"结伴而行.docx" -t markdown -o "$OUT/00_preface.md" 2>/dev/null

# 第一章
pandoc "$SRC/（陈亚澜）问题引领，AI赋能——初中科学《日地月的相对运动》教学实践.docx" -t markdown -o "$OUT/01_01.md" 2>/dev/null
pandoc "$SRC/（金怡雯）AI融教启思 破局素养教学——基于 \"嫌疑人'k'的现身\" 的课堂实践.docx" -t markdown -o "$OUT/01_02.md" 2>/dev/null
pandoc "$SRC/（姚储）情境・情感・评价：三维赋能初中语文教学路径研究.docx" -t markdown -o "$OUT/01_03.md" 2>/dev/null
pandoc "$SRC/（江明欢）AI赋能历史课堂教学实践 — 以《辛亥革命》为例.docx" -t markdown -o "$OUT/01_04.md" 2>/dev/null
pandoc "$SRC/（张勤）AI赋能初中文言文情境化教学与深度学习实践 张勤.docx" -t markdown -o "$OUT/01_05.md" 2>/dev/null
pandoc "$SRC/（诸晓惠）基于AI的情境可视化与兴趣激发实践.doc" -t markdown -o "$OUT/01_06.md" 2>/dev/null
pandoc "$SRC/（高宇轩）AI赋能 \"中国梦\"主题教学的智能体辅助探究实践.docx" -t markdown -o "$OUT/01_07.md" 2>/dev/null
pandoc "$SRC/（岑杭）基于AI实时图像生成的批判性思维培育教学实践.docx" -t markdown -o "$OUT/01_08.md" 2>/dev/null
pandoc "$SRC/（沈剑军）与\"豆包\"结伴而行.docx" -t markdown -o "$OUT/01_09.md" 2>/dev/null

# 第二章
pandoc "$SRC/（夏长斌）基于数智作业的初中数学学情诊断与分层教学实践.docx" -t markdown -o "$OUT/02_01.md" 2>/dev/null
pandoc "$SRC/（肖玲燕）AI应用：初中英语\"听说+数智作业\"精准教学实践.docx" -t markdown -o "$OUT/02_02.md" 2>/dev/null
pandoc "$SRC/（朱颖秋）AI智能批阅与个性化推题赋能初三数学精准教学的实践案例.docx" -t markdown -o "$OUT/02_03.md" 2>/dev/null
pandoc "$SRC/（陈煜瑶）\"一核三阶\"：基于科大讯飞AI的作文智能评改.doc" -t markdown -o "$OUT/02_04.md" 2>/dev/null
pandoc "$SRC/（刘悦）基于大语言模型的初中语文人物传记习作分层批改与精准反馈实践.docx" -t markdown -o "$OUT/02_05.md" 2>/dev/null
pandoc "$SRC/（彭玲琪）基于智慧作业平台和错题归因的初中数学精准教学实践——以《1.7角平分线的性质》为例.docx" -t markdown -o "$OUT/02_06.md" 2>/dev/null
pandoc "$SRC/（陆佳怡）数智赋能，科学增效——基于数智作业平台的初中科学教育\"双减\"加法实践.docx" -t markdown -o "$OUT/02_07.md" 2>/dev/null
pandoc "$SRC/（马玲怡）基于AI的初中历史个性化作业与错题精准辅导.docx" -t markdown -o "$OUT/02_08.md" 2>/dev/null

# 第三章
pandoc "$SRC/（许嘉诚）AI听说课堂赋能初中英语语法课的教学实践案例.docx" -t markdown -o "$OUT/03_01.md" 2>/dev/null
pandoc "$SRC/（郑嘉琳）英语AI听说课堂赋能初一英语\"人人开口\"——基于实时语音评测系统的互动教学实践.docx" -t markdown -o "$OUT/03_02.md" 2>/dev/null
pandoc "$SRC/（杨雨欣）AI赋能教学案例.wps" -t markdown -o "$OUT/03_03.md" 2>/dev/null
pandoc "$SRC/（武莹凡）AI赋能初中数学相似三角形复习.docx" -t markdown -o "$OUT/03_04.md" 2>/dev/null
pandoc "$SRC/（占丽菲）《等式的基本性质》教学案例分析.docx" -t markdown -o "$OUT/03_05.md" 2>/dev/null
pandoc "$SRC/（张佳妮）AI赋能地理教学实践案例_.docx" -t markdown -o "$OUT/03_06.md" 2>/dev/null
pandoc "$SRC/（姜越）利用gemini3快速制作几何题配套模型一些实践尝试.docx" -t markdown -o "$OUT/03_07.md" 2>/dev/null
pandoc "$SRC/（孙康怡）AI赋能的科学实验教学.docx" -t markdown -o "$OUT/03_08.md" 2>/dev/null
pandoc "$SRC/（储佳敏）AI赋能微观可视化：摩擦起电的电子转移探究教学实践.docx" -t markdown -o "$OUT/03_09.md" 2>/dev/null
pandoc "$SRC/（裴伊梦）AI赋能初中科学凸透镜成像精准教学实践案例.docx" -t markdown -o "$OUT/03_10.md" 2>/dev/null
pandoc "$SRC/（冯建芳）AI赋能初中科学精准教学—从课堂到课后的全场景实践与成效.docx" -t markdown -o "$OUT/03_11.md" 2>/dev/null
pandoc "$SRC/（沈正华）数据跑起来，教学更明白 ——智慧操场赋能精准教学.docx" -t markdown -o "$OUT/03_12.md" 2>/dev/null
pandoc "$SRC/（程欣）AI赋能初中社会学科教学的实践探索.docx" -t markdown -o "$OUT/03_13.md" 2>/dev/null
pandoc "$SRC/（方淳）AI赋能心理健康教育教学应用案例.docx" -t markdown -o "$OUT/03_14.md" 2>/dev/null
pandoc "$SRC/（郭士豪）AI赋能教育教学应用的实践案例.docx" -t markdown -o "$OUT/03_15.md" 2>/dev/null
pandoc "$SRC/（申屠楚翘）双轨并行：信息化工具与DeepSeek智能体在初中数学实验教学中的融合应用研究.docx" -t markdown -o "$OUT/03_16.md" 2>/dev/null

# 第四章
pandoc "$SRC/（李承城）巧用AI绘图点亮细节描写.docx" -t markdown -o "$OUT/04_01.md" 2>/dev/null
pandoc "$SRC/（李雪雯）基于人工智能通识教育的学科教学实践——以初中道德与法治《坚守公平》为例.docx" -t markdown -o "$OUT/04_02.md" 2>/dev/null
pandoc "$SRC/（陈乐凡）AI赋能下\"入境—入心—入情\"三阶深度阅读的教学探索——以《桃花源记》为例.docx" -t markdown -o "$OUT/04_03.md" 2>/dev/null
pandoc "$SRC/（沈艺莹）AI赋能：让\"笨拙\"的背影\"触手可及\" ——以《背影》一课的情感体验深化为例.docx" -t markdown -o "$OUT/04_04.md" 2>/dev/null

echo "Done converting"

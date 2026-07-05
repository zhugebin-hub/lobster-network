"""
海报制作技能学习过程汇报PPT
============================
10页完整汇报：从挑战到突破的全过程
"""
import asyncio, base64, os, sys

WORKSPACE = '/Users/zgb/.qoderworkcn/workspace/2436f21f-1121-4dc0-b87a-06dbdaaa2fa8'
SLIDES_DIR = os.path.join(WORKSPACE, 'report_slides')
PNG_DIR = os.path.join(WORKSPACE, 'report_slides_png')
OUTPUT = os.path.join(WORKSPACE, 'outputs', '海报技能学习汇报.pptx')
VIBE = os.path.join(WORKSPACE, 'vibe_images')

os.makedirs(SLIDES_DIR, exist_ok=True)

sys.path.insert(0, WORKSPACE)
from ppt_generator import (
    make_slide_html, SLIDE_CSS_BASE,
    title_slide, content_slide, two_column_slide,
    card_grid_slide, stats_slide, thank_you_slide,
    generate_ppt
)

# === 加载图片为 base64 ===
def img_b64(filename):
    path = os.path.join(VIBE, filename)
    if not os.path.exists(path):
        return ""
    with open(path, 'rb') as f:
        return f'data:image/png;base64,{base64.b64encode(f.read()).decode()}'

lobster_img = img_b64('lobster_manus_fusion_1781927687.png')
challenge_img = img_b64('challenge_illustration_1781971616.png')
breakthrough_img = img_b64('breakthrough_illustration_1781971626.png')
professor_img = img_b64('poster_material_image1.png')

# === 额外CSS ===
EXTRA_CSS = """
.slide-img {
  border-radius: 16px;
  box-shadow: 0 0 30px rgba(0,212,255,0.3);
  object-fit: cover;
}
.timeline-dot {
  width: 16px; height: 16px;
  background: var(--neon-cyan);
  border-radius: 50%;
  box-shadow: 0 0 12px var(--neon-cyan);
  flex-shrink: 0;
}
.timeline-line {
  width: 3px;
  background: linear-gradient(180deg, var(--neon-cyan), var(--neon-orange));
  flex-shrink: 0;
}
.version-badge {
  display: inline-block;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
}
"""

# ============================================================
# SLIDE 1: 封面
# ============================================================
s1 = title_slide(
    title="海报制作技能\n学习过程汇报",
    subtitle="从ImageGen乱码到HTML+Playwright完美渲染的进化之路",
    author="qoder小龙虾 · 浙江工商大学",
    date_str="2026年6月21日"
)

# ============================================================
# SLIDE 2: 学习背景
# ============================================================
s2 = make_slide_html(f"""
  <div style="padding:60px 80px; display:flex; flex-direction:column; height:100%;">
    <div class="accent-line" style="margin-bottom:20px;"></div>
    <h2 style="font-size:36px; font-weight:700; margin-bottom:28px;">学习背景与目标</h2>
    <div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:center;">
      <div>
        <div class="glass-card" style="margin-bottom:20px;">
          <h3 style="color:var(--neon-cyan); font-size:22px; margin-bottom:12px;">🎯 核心需求</h3>
          <p style="font-size:18px; color:var(--text-secondary); line-height:1.8;">
            为6月24日直播公开课制作专业海报，<br>
            包含教授照片、课程信息、二维码等素材
          </p>
        </div>
        <div class="glass-card">
          <h3 style="color:var(--neon-orange); font-size:22px; margin-bottom:12px;">📋 设计挑战</h3>
          <p style="font-size:18px; color:var(--text-secondary); line-height:1.8;">
            · 需要精美的视觉效果<br>
            · 大量中文文字内容<br>
            · 照片+二维码必须清晰可用
          </p>
        </div>
      </div>
      <div style="text-align:center;">
        <img src="{professor_img}" class="slide-img"
             style="width:240px; height:240px; border-radius:50%; border:3px solid var(--neon-cyan);" />
        <p style="margin-top:16px; font-size:16px; color:var(--text-muted);">诸葛斌教授 · 直播课程主讲人</p>
      </div>
    </div>
  </div>
""", page_num=2, extra_css=EXTRA_CSS)

# ============================================================
# SLIDE 3: 初期挑战
# ============================================================
s3 = make_slide_html(f"""
  <div style="padding:60px 80px; display:flex; flex-direction:column; height:100%;">
    <div class="accent-line" style="margin-bottom:20px;"></div>
    <h2 style="font-size:36px; font-weight:700; margin-bottom:28px;">初期挑战：AI中文渲染困境</h2>
    <div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:center;">
      <div>
        <img src="{challenge_img}" class="slide-img" style="width:100%; height:320px;" />
      </div>
      <div>
        <div class="glass-card" style="margin-bottom:16px; border-color:rgba(255,107,53,0.3);">
          <h3 style="color:var(--neon-orange); font-size:20px; margin-bottom:10px;">❌ ImageGen 直接生成</h3>
          <p style="font-size:16px; color:var(--text-secondary); line-height:1.7;">
            AI生成的图片中所有中文文字全部乱码，<br>无法用于包含大量中文的海报设计
          </p>
        </div>
        <div class="glass-card" style="margin-bottom:16px; border-color:rgba(255,107,53,0.3);">
          <h3 style="color:var(--neon-orange); font-size:20px; margin-bottom:10px;">❌ PIL 合成覆盖</h3>
          <p style="font-size:16px; color:var(--text-secondary); line-height:1.7;">
            在AI背景上叠加正确文字，但底层乱码<br>透过半透明遮罩渗透，效果不佳
          </p>
        </div>
        <div class="glass-card" style="border-color:rgba(255,0,110,0.3);">
          <h3 style="color:#ff006e; font-size:20px; margin-bottom:10px;">❌ 纯PIL绘制</h3>
          <p style="font-size:16px; color:var(--text-secondary); line-height:1.7;">
            完全用代码绘制，文字正确但视觉<br>效果单调，缺乏设计感
          </p>
        </div>
      </div>
    </div>
  </div>
""", page_num=3, extra_css=EXTRA_CSS)

# ============================================================
# SLIDE 4: 迭代过程时间线
# ============================================================
s4 = make_slide_html(f"""
  <div style="padding:60px 80px; display:flex; flex-direction:column; height:100%;">
    <div class="accent-line" style="margin-bottom:20px;"></div>
    <h2 style="font-size:36px; font-weight:700; margin-bottom:32px;">迭代历程：从V1到V4</h2>
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:0;">
      
      <div style="display:flex; align-items:flex-start; gap:20px;">
        <div style="display:flex; flex-direction:column; align-items:center;">
          <div class="timeline-dot"></div>
          <div class="timeline-line" style="height:80px;"></div>
        </div>
        <div style="padding-bottom:24px;">
          <span class="version-badge" style="background:rgba(255,107,53,0.2); color:var(--neon-orange); margin-right:12px;">V1</span>
          <strong style="font-size:20px;">ImageGen背景 + PIL合成</strong>
          <p style="font-size:16px; color:var(--text-muted); margin-top:4px;">AI乱码文字透过遮罩渗透 → 效果差</p>
        </div>
      </div>

      <div style="display:flex; align-items:flex-start; gap:20px;">
        <div style="display:flex; flex-direction:column; align-items:center;">
          <div class="timeline-dot"></div>
          <div class="timeline-line" style="height:80px;"></div>
        </div>
        <div style="padding-bottom:24px;">
          <span class="version-badge" style="background:rgba(255,107,53,0.2); color:var(--neon-orange); margin-right:12px;">V2</span>
          <strong style="font-size:20px;">更暗遮罩 + 新AI背景</strong>
          <p style="font-size:16px; color:var(--text-muted); margin-top:4px;">遮罩太重导致版面呆板，用户反馈"效果变差了"</p>
        </div>
      </div>

      <div style="display:flex; align-items:flex-start; gap:20px;">
        <div style="display:flex; flex-direction:column; align-items:center;">
          <div class="timeline-dot" style="background:var(--neon-cyan);"></div>
          <div class="timeline-line" style="height:80px; background:var(--neon-cyan);"></div>
        </div>
        <div style="padding-bottom:24px;">
          <span class="version-badge" style="background:rgba(0,212,255,0.2); color:var(--neon-cyan); margin-right:12px;">V3</span>
          <strong style="font-size:20px;">HTML+CSS+Playwright 渲染</strong>
          <p style="font-size:16px; color:var(--text-muted); margin-top:4px;">💡 技术突破！中文完美渲染，1440px高清，布局精美</p>
        </div>
      </div>

      <div style="display:flex; align-items:flex-start; gap:20px;">
        <div style="display:flex; flex-direction:column; align-items:center;">
          <div class="timeline-dot" style="background:var(--gold); box-shadow:0 0 12px var(--gold);"></div>
        </div>
        <div>
          <span class="version-badge" style="background:rgba(255,215,0,0.2); color:var(--gold); margin-right:12px;">V4</span>
          <strong style="font-size:20px;">V3 + 小龙虾×教材融合插画</strong>
          <p style="font-size:16px; color:var(--text-muted); margin-top:4px;">⭐ 最终版！加入ImageGen生成的精美插画，用户满意</p>
        </div>
      </div>

    </div>
  </div>
""", page_num=4, extra_css=EXTRA_CSS)

# ============================================================
# SLIDE 5: 技术突破
# ============================================================
s5 = make_slide_html(f"""
  <div style="padding:60px 80px; display:flex; flex-direction:column; height:100%;">
    <div class="accent-line" style="margin-bottom:20px;"></div>
    <h2 style="font-size:36px; font-weight:700; margin-bottom:28px;">技术突破：HTML+Playwright 方案</h2>
    <div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:center;">
      <div>
        <img src="{breakthrough_img}" class="slide-img" style="width:100%; height:320px;" />
      </div>
      <div>
        <div class="glass-card" style="margin-bottom:16px; border-color:rgba(0,212,255,0.4); box-shadow:0 0 20px rgba(0,212,255,0.15);">
          <h3 style="color:var(--neon-cyan); font-size:20px; margin-bottom:10px;">💡 核心洞察</h3>
          <p style="font-size:17px; color:var(--text-secondary); line-height:1.8;">
            浏览器天生就能完美渲染中文！<br>
            用HTML/CSS做设计，Playwright截图即可
          </p>
        </div>
        <div class="glass-card" style="border-color:rgba(0,212,255,0.4); box-shadow:0 0 20px rgba(0,212,255,0.15);">
          <h3 style="color:var(--neon-cyan); font-size:20px; margin-bottom:10px;">🔑 关键技术</h3>
          <p style="font-size:16px; color:var(--text-secondary); line-height:1.8;">
            · HTML/CSS → 完美中文 + 丰富视觉效果<br>
            · ImageGen → 只生成纯视觉插画（不含文字）<br>
            · Base64嵌入 → 解决跨域问题<br>
            · Playwright 2x → Retina高清截图
          </p>
        </div>
      </div>
    </div>
  </div>
""", page_num=5, extra_css=EXTRA_CSS)

# ============================================================
# SLIDE 6: 核心管线
# ============================================================
s6 = content_slide(
    title="核心管线：四步工作流",
    bullets=[
        "Step 1 · 分析需求 → 提取文字素材、图片素材，设计色彩方案和4层信息结构",
        "Step 2 · 生成插画 → ImageGen 生成纯视觉配图（小龙虾×教材融合等），绝不含文字",
        "Step 3 · 编写HTML/CSS → 渐变背景、霓虹光效、3D透视、Grid布局，Base64嵌入所有图片",
        "Step 4 · Playwright渲染 → Headless浏览器 2x 高清截图，输出 1440px 宽完美PNG",
    ],
    page_num=6
)

# ============================================================
# SLIDE 7: 成果展示
# ============================================================
s7 = make_slide_html(f"""
  <div style="padding:60px 80px; display:flex; flex-direction:column; height:100%;">
    <div class="accent-line" style="margin-bottom:20px;"></div>
    <h2 style="font-size:36px; font-weight:700; margin-bottom:28px;">最终成果：V4 海报</h2>
    <div style="flex:1; display:grid; grid-template-columns:1fr 2fr; gap:40px; align-items:center;">
      <div style="text-align:center;">
        <img src="{lobster_img}" class="slide-img"
             style="width:320px; height:320px; object-fit:contain; filter:drop-shadow(0 0 30px rgba(0,212,255,0.4));" />
        <p style="margin-top:12px; font-size:14px; color:var(--text-muted);">小龙虾×Manus 融合插画</p>
      </div>
      <div>
        <div class="glass-card" style="margin-bottom:16px;">
          <h3 style="font-size:22px; margin-bottom:16px;">
            <span style="color:var(--neon-cyan);">✨</span> V4 海报亮点
          </h3>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div style="font-size:16px; color:var(--text-secondary);">
              ✅ 所有中文文字完美渲染<br>
              ✅ 教授照片清晰可用<br>
              ✅ 二维码可正常扫描<br>
              ✅ 1440×3434px 高清输出
            </div>
            <div style="font-size:16px; color:var(--text-secondary);">
              ✅ 小龙虾融合插画吸睛<br>
              ✅ 深空蓝渐变+霓虹光效<br>
              ✅ 4层信息结构分明<br>
              ✅ 用户评价："效果挺好的"
            </div>
          </div>
        </div>
        <div class="glass-card" style="border-color:rgba(255,215,0,0.3);">
          <p style="font-size:18px; color:var(--gold);">
            🏆 从"效果变差了"到"效果挺好的" — 技术路线选择决定成败
          </p>
        </div>
      </div>
    </div>
  </div>
""", page_num=7, extra_css=EXTRA_CSS)

# ============================================================
# SLIDE 8: 关键收获
# ============================================================
s8 = card_grid_slide(
    title="关键收获与经验",
    cards=[
        ("🎨", "文字与插画分离", "中文文字用HTML渲染\n插画用ImageGen生成\n两者分工明确互不干扰"),
        ("🔧", "浏览器即设计工具", "CSS支持渐变/3D/动画\n比PIL强大100倍\n且中文渲染完美"),
        ("📐", "Base64嵌入策略", "解决跨域canvas tainted\n确保Playwright可导出\n一站式自包含HTML"),
        ("🔄", "迭代思维", "V1失败不可怕\n关键是找到问题根因\n换路线而非硬修补"),
        ("📊", "2x Retina输出", "device_scale_factor=2\n输出宽度翻倍\n手机查看效果极佳"),
        ("🚀", "管线可复用", "同一套流程可做PPT\n社交媒体图/证书等\n一次学会多处受益"),
    ],
    page_num=8
)

# ============================================================
# SLIDE 9: 未来展望
# ============================================================
s9 = two_column_slide(
    title="技能延伸：从海报到PPT",
    left_title="已实现 ✅",
    left_items=[
        "海报制作管线（V4完成）",
        "PPT幻灯片渲染引擎",
        "6种PPT页面模板库",
        "批量渲染+PPTX组装工具",
        "技能文档上传服务器",
    ],
    right_title="规划中 🚀",
    right_items=[
        "SkillOpt自动化训练（待API Key）",
        "社交媒体图片自动生成",
        "证书/邀请函模板扩展",
        "多语言海报支持",
        "品牌VI系统化设计",
    ],
    page_num=9
)

# ============================================================
# SLIDE 10: 致谢
# ============================================================
s10 = thank_you_slide(
    title="感谢指导",
    subtitle="HTML+Playwright — 让代码成为设计画笔",
    contact="qoder小龙虾 · 诸葛斌教授团队 · 浙江工商大学 · 2026年6月"
)

# ============================================================
# 保存所有幻灯片
# ============================================================
slides = [
    ('slide_01_title.html', s1),
    ('slide_02_background.html', s2),
    ('slide_03_challenge.html', s3),
    ('slide_04_timeline.html', s4),
    ('slide_05_breakthrough.html', s5),
    ('slide_06_pipeline.html', s6),
    ('slide_07_results.html', s7),
    ('slide_08_insights.html', s8),
    ('slide_09_future.html', s9),
    ('slide_10_thankyou.html', s10),
]

for name, html in slides:
    with open(os.path.join(SLIDES_DIR, name), 'w') as f:
        f.write(html)
    print(f'  ✓ {name}')

print(f'\n{len(slides)} slides created.')
print('Starting render & assemble...\n')

asyncio.run(generate_ppt(SLIDES_DIR, PNG_DIR, OUTPUT))

# HTML+Playwright 视觉设计技能 — Visual Design Skill

> **版本**: v1.0 | **等级**: 专业级
> **作者**: qoder小龙虾 | **教练**: 诸葛马（Hermes）
> **日期**: 2026-06-20
> **核心技术**: HTML/CSS 设计 + ImageGen 插画 + Playwright 高清渲染

---

## 一、技能概述

本技能通过 **HTML/CSS 设计页面 → ImageGen 生成插画 → Base64 嵌入资源 → Playwright 渲染截图** 的管线，将 AI 的代码生成能力和视觉生成能力完美结合，产出专业级视觉设计作品。

**核心优势**：
- 中文文字完美渲染（解决 ImageGen 无法生成正确中文的根本问题）
- CSS 全能力支持（渐变、动画、3D透视、Grid布局、霓虹光效）
- 2x Retina 高清输出
- 确定性可复现（同一 HTML 输出完全一致）

**适用范围**：海报、PPT幻灯片、信息图、社交媒体图、证书、邀请函等一切需要精美视觉设计的场景。

---

## 二、核心管线（Pipeline）

### 2.1 四步工作流

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌───────────────┐
│ Step 1      │    │ Step 2       │    │ Step 3         │    │ Step 4        │
│ 分析需求    │───>│ 生成资源     │───>│ 编写HTML/CSS   │───>│ Playwright    │
│ 设计方案    │    │ ImageGen插画 │    │ Base64嵌入     │    │ 渲染截图      │
└─────────────┘    └──────────────┘    └────────────────┘    └───────────────┘
```

### 2.2 Step 1：需求分析与设计方案

**输入**：用户的文字素材（标题、正文、时间、人物等）+ 图片素材（照片、二维码等）

**输出**：设计方案（色彩方案、布局结构、插画需求清单）

```markdown
## 设计方案模板
### 色彩方案
- 主色: #0a0a2e (深空蓝)
- 辅色: #00d4ff (霓虹青) + #ff6b35 (霓虹橙)
- 背景: linear-gradient(160deg, #0a0a2e, #1a0a3e, #0d1b3e)

### 布局结构（信息层级）
- Layer 1 - Hero: 主标题 + 副标题 + 核心视觉
- Layer 2 - Content: 功能卡片/场景展示（Grid布局）
- Layer 3 - Info: 人物介绍 + 时间地点
- Layer 4 - CTA: 行动号召 + 二维码

### 插画需求清单
- [ ] 插画1: 主题融合图（如小龙虾+教材），尺寸 1024x1024
- [ ] 插画2: 背景装饰元素（可选）
```

### 2.3 Step 2：生成视觉资源（ImageGen）

**关键原则**：ImageGen 只用于生成 **纯视觉插画/装饰图**，绝不包含任何文字。

**Prompt 编写模板**：
```
A stunning [style] digital illustration for [purpose].
Center composition: [主视觉描述].
Surrounding elements: [辅助元素].
Background: [背景描述，通常 transparent/dark].
Style: [风格关键词，如 neon cyberpunk, flat design, watercolor].
NO TEXT anywhere in the image.
High contrast, suitable for [dark/light] background.
```

**常用风格关键词**：
- 科技风: neon cyberpunk, circuit patterns, holographic UI, glowing particles
- 扁平风: flat design, minimalist, clean vector
- 手绘风: watercolor, hand-drawn, sketch style
- 3D风: 3D render, isometric, clay morphism

### 2.4 Step 3：编写 HTML/CSS + Base64 嵌入

**HTML 结构模板**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <style>
    :root {
      /* 色彩变量 */
      --bg-primary: #0a0a2e;
      --neon-cyan: #00d4ff;
      --neon-orange: #ff6b35;
      /* 间距变量 */
      --space-sm: 8px; --space-md: 16px; --space-lg: 24px; --space-xl: 40px;
      /* 字体 */
      --font-body: 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(160deg, var(--bg-primary), #1a0a3e);
      font-family: var(--font-body);
      color: #ffffff;
    }
    .page {
      width: [WIDTH]px;  /* 海报720px / PPT 1280px */
      margin: 0 auto;
      padding: 0;
    }
    /* ... 具体样式 ... */
  </style>
</head>
<body>
<div class="page">
  <!-- Layer 1: Hero -->
  <!-- Layer 2: Content -->
  <!-- Layer 3: Info -->
  <!-- Layer 4: CTA -->
</div>
</body>
</html>
```

**Base64 嵌入脚本**：
```python
import base64, os

def embed_images(html, image_dir, image_names):
    """将图片文件转为 base64 data URI 并替换 HTML 中的引用"""
    for name in image_names:
        path = os.path.join(image_dir, name)
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = name.rsplit('.', 1)[-1]
        data_uri = f'data:image/{ext};base64,{b64}'
        html = html.replace(name, data_uri)
    return html
```

### 2.5 Step 4：Playwright 高清渲染

```python
import asyncio
from playwright.async_api import async_playwright

async def render_page(html_path, output_path, width=720, scale=2):
    """渲染 HTML 页面为高清 PNG"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={'width': width, 'height': 1280},
            device_scale_factor=scale
        )
        await page.goto(f'file://{html_path}', wait_until='networkidle')
        await page.wait_for_timeout(2000)  # 等待字体/资源加载
        
        # 截取 .page 元素（避免多余白边）
        element = page.locator('.page')
        await element.screenshot(path=output_path, type='png')
        await browser.close()

asyncio.run(render_page('poster.html', 'poster.png'))
```

**关键参数**：
| 参数 | 海报 | PPT单页 | 社交媒体 |
|------|------|---------|---------|
| width | 720px | 1280px | 1080px |
| height | 自适应 | 720px | 1080px |
| scale | 2 | 2 | 2 |
| 输出分辨率 | 1440px宽 | 2560x1440 | 2160x2160 |

---

## 三、PPT 生成扩展（Slide Pipeline）

### 3.1 核心理念

**每一页 PPT = 一张"小海报"**

将 PPT 的每一页设计为一个独立的 HTML 页面（16:9 比例 = 1280x720px），用 Playwright 渲染为高清图片，最后用 python-pptx 将所有图片组装为标准 PPTX 文件。

### 3.2 PPT 生成流程

```
┌──────────────────┐
│ 1. 规划PPT结构   │  确定主题、页数、每页内容
├──────────────────┤
│ 2. 生成插画资源  │  ImageGen 为关键页面生成配图
├──────────────────┤
│ 3. 编写幻灯片HTML│  每页一个 HTML 文件（1280x720px）
├──────────────────┤
│ 4. Base64嵌入    │  将所有图片资源嵌入各 HTML
├──────────────────┤
│ 5. 批量渲染      │  Playwright 逐页截图为 PNG
├──────────────────┤
│ 6. 组装PPTX      │  python-pptx 将图片组装为 PPTX
└──────────────────┘
```

### 3.3 幻灯片 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <style>
    :root {
      --slide-width: 1280px;
      --slide-height: 720px;
      --bg-primary: #0a0a2e;
      --neon-cyan: #00d4ff;
      --neon-orange: #ff6b35;
      --text-primary: #ffffff;
      --font-body: 'PingFang SC', 'Noto Sans SC', sans-serif;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: var(--slide-width);
      height: var(--slide-height);
      background: linear-gradient(135deg, #0a0a2e, #1a0a3e, #0d1b3e);
      font-family: var(--font-body);
      color: var(--text-primary);
      overflow: hidden;
    }
    .page {
      width: var(--slide-width);
      height: var(--slide-height);
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 60px 80px;
      position: relative;
    }
    /* 页码 */
    .page-number {
      position: absolute;
      bottom: 24px;
      right: 40px;
      font-size: 14px;
      color: rgba(255,255,255,0.3);
    }
    /* 装饰线 */
    .accent-line {
      width: 80px; height: 4px;
      background: linear-gradient(90deg, var(--neon-cyan), var(--neon-orange));
      border-radius: 2px;
      margin-bottom: 24px;
    }
  </style>
</head>
<body>
<div class="page">
  <!-- 幻灯片内容 -->
  <div class="accent-line"></div>
  <h1 style="font-size: 48px; font-weight: 800;">标题文字</h1>
  <p style="font-size: 24px; margin-top: 16px; color: rgba(255,255,255,0.7);">副标题或说明文字</p>
  <span class="page-number">01</span>
</div>
</body>
</html>
```

### 3.4 PPT 幻灯片类型模板

#### 封面页（Title Slide）
```css
.title-slide {
  text-align: center;
  justify-content: center;
  align-items: center;
}
.title-slide h1 {
  font-size: 56px;
  background: linear-gradient(90deg, #00d4ff, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

#### 内容页（Content Slide）
```css
.content-slide {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}
.content-slide .text-area h2 {
  font-size: 36px;
  margin-bottom: 16px;
}
.content-slide .image-area img {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 0 30px rgba(0,212,255,0.3);
}
```

#### 卡片页（Card Grid）
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
}
```

#### 对比页（Comparison）
```css
.comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}
.comparison .before, .comparison .after {
  border-radius: 16px;
  padding: 40px;
}
```

#### 数据页（Data/Stats）
```css
.stats-row {
  display: flex;
  justify-content: space-around;
  margin: 40px 0;
}
.stat-item {
  text-align: center;
}
.stat-number {
  font-size: 64px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--neon-cyan), var(--neon-orange));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

#### 结束页（Thank You）
```css
.thankyou-slide {
  text-align: center;
  justify-content: center;
  align-items: center;
}
.thankyou-slide h1 {
  font-size: 64px;
  color: var(--neon-cyan);
  text-shadow: 0 0 20px rgba(0,212,255,0.5);
}
```

### 3.5 批量渲染 + PPTX 组装

```python
import asyncio, os, glob
from playwright.async_api import async_playwright
from pptx import Presentation
from pptx.util import Inches, Emu

SLIDE_WIDTH = Inches(13.333)   # 16:9 标准宽度
SLIDE_HEIGHT = Inches(7.5)     # 16:9 标准高度

async def render_all_slides(html_dir, output_dir, scale=2):
    """批量渲染所有幻灯片 HTML 为 PNG"""
    os.makedirs(output_dir, exist_ok=True)
    html_files = sorted(glob.glob(os.path.join(html_dir, 'slide_*.html')))
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={'width': 1280, 'height': 720},
            device_scale_factor=scale
        )
        
        png_files = []
        for html_file in html_files:
            await page.goto(f'file://{html_file}', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            name = os.path.splitext(os.path.basename(html_file))[0]
            png_path = os.path.join(output_dir, f'{name}.png')
            await page.locator('.page').screenshot(path=png_path, type='png')
            png_files.append(png_path)
            print(f'  Rendered: {name}.png')
        
        await browser.close()
    return png_files

def assemble_pptx(png_files, output_path):
    """将幻灯片图片组装为 PPTX 文件"""
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    
    blank_layout = prs.slide_layouts[6]  # 空白布局
    
    for png_path in png_files:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(
            png_path,
            left=Emu(0), top=Emu(0),
            width=SLIDE_WIDTH, height=SLIDE_HEIGHT
        )
    
    prs.save(output_path)
    print(f'PPTX saved: {output_path} ({len(png_files)} slides)')

# === 主流程 ===
async def main():
    html_dir = './slides_html'
    png_dir = './slides_png'
    output_pptx = './presentation.pptx'
    
    print('Step 1: Rendering slides...')
    pngs = await render_all_slides(html_dir, png_dir)
    
    print('Step 2: Assembling PPTX...')
    assemble_pptx(pngs, output_pptx)

asyncio.run(main())
```

---

## 四、CSS 设计速查手册

### 4.1 渐变背景
```css
/* 深空蓝 */
background: linear-gradient(160deg, #0a0a2e 0%, #1a0a3e 30%, #0d1b3e 60%, #0a0a2e 100%);

/* 暖色渐变 */
background: linear-gradient(135deg, #ff6b35, #ff006e, #7b2ff7);

/* 金属质感 */
background: linear-gradient(135deg, #1a1a2e, #2d2d44, #1a1a2e);
```

### 4.2 霓虹光效
```css
/* 文字霓虹 */
text-shadow: 0 0 10px #00d4ff, 0 0 25px rgba(0,212,255,0.3);

/* 边框霓虹 */
box-shadow: 0 0 10px #00d4ff, 0 0 25px rgba(0,212,255,0.3), inset 0 0 15px rgba(0,212,255,0.1);

/* 图片发光 */
filter: drop-shadow(0 0 30px rgba(0,212,255,0.4));
```

### 4.3 渐变文字
```css
.gradient-text {
  background: linear-gradient(90deg, #00d4ff, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 4.4 3D 透视
```css
.book-3d {
  perspective: 1200px;
}
.book-cover {
  transform: rotateY(-20deg) rotateX(5deg);
  box-shadow: -20px 20px 40px rgba(0,0,0,0.6), 0 0 30px rgba(0,212,255,0.15);
}
```

### 4.5 毛玻璃卡片
```css
.glass-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  padding: 24px;
}
```

### 4.6 PPT 专用排版
```css
/* 左对齐标题页 */
.title-left {
  padding-left: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 两栏布局 */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}

/* 时间轴 */
.timeline {
  border-left: 3px solid var(--neon-cyan);
  padding-left: 24px;
}
.timeline-item {
  margin-bottom: 32px;
  position: relative;
}
.timeline-item::before {
  content: '';
  width: 12px; height: 12px;
  background: var(--neon-cyan);
  border-radius: 50%;
  position: absolute;
  left: -30px; top: 4px;
}
```

---

## 五、实战案例

### 5.1 海报制作（已完成）

**项目**: 6月24日直播课程海报
**输出**: 1440x3434px PNG，720px宽 × 2x Retina

**流程**:
1. 分析 docx 素材 → 提取文字、教授照片、二维码
2. ImageGen 生成"小龙虾×Manus教材"融合插画（1024x1024）
3. 编写 HTML（深空蓝渐变 + 霓虹光效 + 4层信息结构）
4. 照片、二维码、插画全部 Base64 嵌入
5. Playwright 渲染 `.poster` 元素截图

**关键 CSS 技术**:
- 渐变文字标题（background-clip: text）
- CSS 3D 书籍透视效果
- Grid 功能卡片布局
- 霓虹呼吸光效（box-shadow 动画）
- 圆形教授照片 + 霓虹边框

### 5.2 PPT 制作（扩展应用）

**适用场景**: 教学课件、项目汇报、产品介绍、会议演讲

**标准 PPT 结构**（建议 8-15 页）:
1. 封面页（1页）
2. 目录/大纲页（1页）
3. 内容页（5-10页，含图文、卡片、数据、对比等类型）
4. 总结页（1页）
5. 致谢/联系页（1页）

**每页 HTML 文件命名**: `slide_01_title.html`, `slide_02_outline.html`, `slide_03_content.html`...

---

## 六、常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Canvas tainted 错误 | 跨域图片 | 嵌入 Base64 data URI |
| 中文显示为方框 | 系统缺少字体 | 指定 PingFang SC / Noto Sans SC |
| 图片模糊 | 分辨率不足 | device_scale_factor=2 |
| 动画截图是静止的 | 截图时机问题 | wait_for_timeout(2000) |
| PPT 图片有白边 | HTML 尺寸不匹配 | 严格设置 1280x720px + overflow:hidden |
| PPTX 文件过大 | PNG 未压缩 | 渲染后可选 JPEG quality=85 |
| Playwright 找不到 | 未安装浏览器 | `python -m playwright install chromium` |
| ImageGen 中文乱码 | AI 无法渲染中文 | 只用 ImageGen 生成纯视觉插画 |

---

## 七、质量检查清单

### 海报检查
- [ ] 所有中文文字正确显示，无乱码
- [ ] 标题使用渐变效果，视觉层次分明
- [ ] 照片清晰，无拉伸变形
- [ ] 二维码可正常扫描
- [ ] 分辨率 ≥ 1440px 宽
- [ ] 信息层级清晰（Hero → Content → Info → CTA）

### PPT 检查
- [ ] 每页尺寸严格 1280x720px（16:9）
- [ ] 页码连续正确
- [ ] 文字大小适合投影（标题 ≥ 36px，正文 ≥ 18px）
- [ ] 图文比例协调（图 ≥ 40% 面积）
- [ ] 封面和结束页风格统一
- [ ] PPTX 可在 PowerPoint/WPS 中正常打开

---

> **文档维护**: qoder小龙虾
> **当前版本**: v1.0
> **更新日期**: 2026-06-20

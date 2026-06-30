# 📊 杭州烟草销售数据分析 - 教学案例版

> **方案 C：HTML + ECharts + Python**  
> 代码最易懂，适合学生学习！

---

## 📁 项目结构

```
hangzhou-tobacco-analysis-teaching/
├── index.html           # 主页面（HTML + JavaScript + ECharts）
├── data/
│   └── sales_data.json  # 销售数据（JSON 格式）
├── generate_json.py     # 数据转换脚本
└── README.md           # 项目说明
```

---

## 🚀 快速启动

### 方式 1：直接打开（最简单）

```bash
# 直接用浏览器打开 index.html
# Windows: 双击 index.html
# Mac: open index.html
# Linux: xdg-open index.html
```

### 方式 2：本地服务器（推荐）

```bash
# Python 3 内置服务器
cd hangzhou-tobacco-analysis-teaching
python3 -m http.server 8000

# 浏览器访问：http://localhost:8000
```

### 方式 3：VS Code Live Server

1. 安装 VS Code Live Server 扩展
2. 右键 index.html → "Open with Live Server"

---

## 📋 功能特点

| 功能 | 说明 | 技术 |
|------|------|------|
| 📊 数据概览 | 总销售额、总销量、平均值等指标 | JavaScript 计算 |
| 🥧 饼图 | 各档次销售占比 | ECharts Pie |
| 📊 柱状图 | 品牌/店铺销售排名 | ECharts Bar |
| 📈 折线图 | 每日/月度销售趋势 | ECharts Line |
| 🔀 散点图 | 销量 vs 销售额关系 | ECharts Scatter |
| 📋 数据表格 | 品牌/店铺排名详情 | HTML Table |
| 🏷️ 标签切换 | 4 个页面切换 | JavaScript Tab |

---

## 🎯 代码解析

### 1. HTML 结构（约 200 行）

```html
<!-- 标题 -->
<div class="header">
    <h1>📊 杭州烟草销售数据分析</h1>
</div>

<!-- 指标卡片 -->
<div class="metrics">
    <div class="metric-card">
        <div class="value">¥8,500,000</div>
        <div class="label">💰 总销售额</div>
    </div>
</div>

<!-- 图表容器 -->
<div class="chart-box">
    <h3>各档次销售占比</h3>
    <div id="category-pie" class="chart"></div>
</div>
```

### 2. CSS 样式（约 150 行）

```css
/* 渐变背景 */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 指标卡片 */
.metric-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

/* 响应式布局 */
.charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
}
```

### 3. JavaScript 逻辑（约 300 行）

```javascript
// 加载数据
fetch('data/sales_data.json')
    .then(response => response.json())
    .then(data => {
        salesData = data;
        initOverview();  // 初始化概览页
    });

// 计算指标
const totalSales = salesData.reduce((sum, item) => sum + item.销售金额，0);

// 绘制饼图
const categoryPie = echarts.init(document.getElementById('category-pie'));
categoryPie.setOption({
    series: [{
        type: 'pie',
        data: [...]
    }]
});
```

### 4. ECharts 图表（约 150 行）

```javascript
// 柱状图配置
{
    type: 'bar',
    data: [100, 200, 300],
    itemStyle: {
        color: new echarts.graphic.LinearGradient(...)
    }
}

// 折线图配置
{
    type: 'line',
    smooth: true,
    areaStyle: {...}
}
```

---

## 📚 教学应用

### 适用课程

| 课程 | 适用章节 | 课时 |
|------|---------|------|
| Web 前端开发 | HTML/CSS 基础 | 2-4 课时 |
| JavaScript 编程 | DOM 操作、数据 fetch | 2-4 课时 |
| 数据可视化 | ECharts 图表库 | 4-6 课时 |
| 信息技术 | 综合项目实践 | 4-8 课时 |

### 知识点覆盖

- ✅ HTML 结构与语义化
- ✅ CSS 布局（Grid、Flexbox）
- ✅ CSS 渐变与动画
- ✅ JavaScript 基础语法
- ✅ JavaScript 数组操作（map、reduce、filter）
- ✅ Fetch API 数据加载
- ✅ ECharts 图表库使用
- ✅ 响应式网页设计

### 实验任务

#### 任务 1：代码阅读（1 课时）
- 阅读 index.html 源代码
- 理解 HTML 结构
- 标记不理解的代码

#### 任务 2：修改样式（1 课时）
- 修改主题颜色
- 调整卡片大小
- 添加新的 CSS 动画

#### 任务 3：添加图表（2 课时）
- 复制现有图表代码
- 修改数据源
- 调整图表配置

#### 任务 4：功能扩展（2 课时）
- 添加数据筛选功能
- 添加导出功能
- 添加新的页面标签

---

## 🔧 自定义修改

### 修改主题颜色

找到 CSS 中的颜色定义：

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-card .value {
    color: #667eea;  /* 修改这个颜色 */
}
```

### 修改图表类型

找到 ECharts 配置：

```javascript
series: [{
    type: 'bar',  // 改为 'line'、'pie'、'scatter'
    data: [...]
}]
```

### 添加新指标卡片

复制 HTML 代码：

```html
<div class="metric-card">
    <div class="value" id="new-metric">0</div>
    <div class="label">📌 新指标</div>
</div>
```

更新 JavaScript：

```javascript
document.getElementById('new-metric').textContent = 计算结果;
```

---

## 📊 数据说明

| 字段 | 类型 | 说明 |
|------|------|------|
| 日期 | String | 销售日期（YYYY-MM-DD） |
| 店铺名称 | String | 店铺名称 |
| 区域 | String | 所属区域 |
| 品牌 | String | 香烟品牌 |
| 档次 | String | 高档/中档/低档 |
| 销售数量 | Number | 销售条数 |
| 销售金额 | Number | 销售金额（元） |

**数据量：** 54,750 条销售记录  
**时间范围：** 2025 年全年  
**店铺数量：** 10 家  
**品牌数量：** 8 个

---

## 🌐 部署方案

### 方案 1：GitHub Pages（免费）

```bash
# 1. 创建 GitHub 仓库
# 2. 推送代码
git init
git add .
git commit -m "Initial commit"
git push origin main

# 3. 开启 GitHub Pages
# Settings → Pages → Source: main branch
```

访问：`https://用户名.github.io/仓库名/`

### 方案 2：Vercel（免费）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

### 方案 3：本地服务器

```bash
# Python
python3 -m http.server 8000

# Node.js
npx http-server -p 8000
```

---

## ⚠️ 注意事项

1. **数据文件较大** - sales_data.json 约 8MB，首次加载需要几秒
2. **浏览器兼容** - 推荐使用 Chrome、Edge、Firefox
3. **跨域问题** - 直接打开 HTML 可能无法加载 JSON，建议用本地服务器
4. **图表渲染** - 大量数据时图表渲染可能较慢

---

##  学习资源

### ECharts 官方
- [ECharts 官网](https://echarts.apache.org/zh/)
- [ECharts 配置项手册](https://echarts.apache.org/zh/option.html)
- [ECharts 示例库](https://echarts.apache.org/examples/zh/index.html)

### JavaScript 学习
- [MDN JavaScript 教程](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)
- [现代 JavaScript 教程](https://zh.javascript.info/)

### Web 开发
- [HTML & CSS 教程](https://developer.mozilla.org/zh-CN/docs/Learn/HTML)
- [响应式网页设计](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Responsive_Design)

---

## 📝 学生作业模板

### 基础作业（必做）

1. 修改网页标题和自己的名字
2. 修改主题颜色（至少 3 处）
3. 添加 1 个新的指标卡片
4. 修改 1 个图表的类型或样式

### 进阶作业（选做）

1. 添加数据筛选功能（按品牌/区域筛选）
2. 添加新的图表类型（雷达图、热力图等）
3. 添加数据导出功能
4. 优化移动端显示效果

### 挑战作业（拓展）

1. 添加实时数据更新功能
2. 集成机器学习预测
3. 添加用户登录功能
4. 部署到公网可访问

---

## 📧 联系与反馈

- **指导教师：** 图图老师
- **开发时间：** 2026 年 4 月
- **技术栈：** HTML + CSS + JavaScript + ECharts
- **适用对象：** 初中/高中/大学信息技术课程

---

**🦞 开发：** 小龙虾智能体辅助  
**📅 最后更新：** 2026 年 4 月 17 日

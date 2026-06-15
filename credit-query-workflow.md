# 教务系统学分统计固定流程

**适用场景：** 浙江工商大学教务系统学分查询与统计分析  
**目标网站：** http://124.160.64.163/jwglxt/xtgl/login_slogin.html

---

## 📋 完整操作流程

### 第一步：登录教务系统

```bash
# 使用浏览器 CDP 或自动化工具访问登录页面
URL: http://124.160.64.163/jwglxt/xtgl/login_slogin.html

# 填写登录信息
用户名：2011080119
密码：lzq20020125

# 注意：如有验证码，需识别后填写
# 验证码识别方法：
# 1. 截取验证码图片 (yzmPic 元素)
# 2. 人工识别或使用 OCR
# 3. 填写到 yzm 输入框
```

---

### 第二步：进入学生学业情况查询页面

**方法 A：通过菜单导航**
1. 点击顶部菜单「信息查询」
2. 在下拉菜单中选择「学生学业情况查询」

**方法 B：直接访问 URL**
```
http://124.160.64.163/jwglxt/xsxy/xsxyqk_cxXsxyqkIndex.html?gnmkdm=N105515
```

**方法 C：使用 clickMenu 函数（推荐）**
```javascript
clickMenu('N105515', '/xsxy/xsxyqk_cxXsxyqkIndex.html', '学生学业情况查询', 'null')
```

---

### 第三步：获取页面数据

**使用 CDP 协议获取页面 HTML：**
```javascript
// WebSocket 连接
ws://127.0.0.1:11687/devtools/page/{targetId}

// 获取完整 HTML
document.documentElement.outerHTML

// 或获取页面文本
document.body.innerText
```

**使用浏览器自动化命令：**
```
browser action=snapshot
browser action=act ref=e1 kind=click
```

---

### 第四步：解析学分数据

**关键数据模式：**
```javascript
// 学分数据格式
"模块名称&nbsp;要求学分:XX.X&nbsp;获得学分:XX.X&nbsp;未获得学分:XX.X"

// 正则提取模式
/([^&]+)&nbsp;要求学分:([\d.]+)&nbsp;获得学分:([\d.]+)&nbsp;未获得学分:([\d.]+)/
```

**主要学分模块：**
| 模块 | 关键词 |
|------|--------|
| 主修合计 | 主修 |
| 课堂教学 | 课堂教学 |
| 通识选修课 | 通识选修课 |
| 专业核心课 | 专业核心课 |
| 专业选修课 | 专业选修课 |
| 实践教学 | 实践教学 |
| 思想政治理论类 | 思想政治理论类 |
| 军事体育类 | 军事体育类 |
| 外语模块 | 外语模块 |
| 计算机模块 | 计算机模块 |
| 学科共同课 | 学科共同课 |
| 个性化课程 | 个性化课程 |
| 创新创业 | 创新创意创业 |

---

### 第五步：统计分析

**计算公式：**
```
完成率 = (获得学分 / 要求学分) × 100%
差值 = 获得学分 - 要求学分
```

**状态判断：**
- ✅ 已完成：获得学分 ≥ 要求学分（要求学分 > 0）
- 🔶 超额：要求学分 = 0 且 获得学分 > 0
- ❌ 未完成：获得学分 < 要求学分
- ⚪ 未开始：要求学分 = 0 且 获得学分 = 0

**输出内容：**
1. 各模块学分对照表
2. 总学分统计
3. 完成率计算
4. 未修课程数量
5. GPA 信息

---

## 🔧 自动化脚本模板

```javascript
const WebSocket = require('ws');

async function queryCredits() {
  // 1. 连接到浏览器 CDP
  const ws = new WebSocket('ws://127.0.0.1:11687/devtools/page/{targetId}');
  
  // 2. 导航到学业情况页面
  await navigate('http://124.160.64.163/jwglxt/xsxy/xsxyqk_cxXsxyqkIndex.html?gnmkdm=N105515');
  
  // 3. 获取页面 HTML
  const html = await evaluate('document.documentElement.outerHTML');
  
  // 4. 提取学分数据
  const modules = extractCreditData(html);
  
  // 5. 统计分析
  const report = generateReport(modules);
  
  // 6. 输出结果
  console.log(report);
}

function extractCreditData(html) {
  const pattern = /([^&]+)&nbsp;要求学分:([\d.]+)&nbsp;获得学分:([\d.]+)&nbsp;未获得学分:([\d.]+)/g;
  const modules = [];
  let match;
  
  while ((match = pattern.exec(html)) !== null) {
    modules.push({
      name: match[1].trim(),
      required: parseFloat(match[2]),
      obtained: parseFloat(match[3]),
      missing: parseFloat(match[4])
    });
  }
  
  return modules;
}

function generateReport(modules) {
  let totalReq = 0, totalObt = 0;
  
  modules.forEach(m => {
    totalReq += m.required;
    totalObt += m.obtained;
  });
  
  return {
    totalRequired: totalReq,
    totalObtained: totalObt,
    completion: ((totalObt / totalReq) * 100).toFixed(1) + '%',
    modules: modules
  };
}
```

---

## 📝 快速命令参考

### 登录相关
```bash
# 检查 Chrome CDP 状态
curl http://127.0.0.1:11687/json

# 启动 CDP 代理
node ~/.openclaw/workspace/skills/web-access/scripts/cdp-proxy.mjs &
```

### 页面导航
```javascript
// 直接导航
Page.navigate({url: 'http://124.160.64.163/jwglxt/xtgl/index_initMenu.html?jsdm=xs'})

// 使用 clickMenu
clickMenu('N105515', '/xsxy/xsxyqk_cxXsxyqkIndex.html', '学生学业情况查询', 'null')
```

### 数据获取
```javascript
// 获取 HTML
document.documentElement.outerHTML

// 获取文本
document.body.innerText

// 截图
Page.captureScreenshot({format: 'png'})
```

### 数据提取
```bash
# grep 提取学分数据
grep '要求学分' page.html | grep '获得学分'

# 提取特定模块
grep -E '专业核心课 | 专业选修课 | 实践教学' page.html
```

---

## ⚠️ 注意事项

1. **验证码处理**
   - 如遇到验证码，先截图保存
   - 验证码图片元素 ID：`yzmPic`
   - 验证码输入框 name：`yzm`

2. **会话保持**
   - 登录后会话有效期有限
   - 超时需重新登录
   - 建议一次性完成查询

3. **数据统计时间**
   - 页面显示统计时间为当前数据生效时间
   - 成绩更新后需重新查询

4. **浏览器要求**
   - 需要 Chrome 开启远程调试 (端口 9222 或 11687)
   - 或使用 OpenClaw browser 工具

---

## 📊 输出报告模板

```
========================================
  XXX 同学 - 学分模块详细统计
========================================

统计时间：YYYY-MM-DD HH:MM:SS

一、总体概况
- 计划总课程：XX 门
- 已通过：XX 门
- 未通过：X 门
- 未修：XX 门
- GPA: X.XX

二、各模块学分完成情况
| 模块名称 | 要求学分 | 获得学分 | 差值 | 状态 |
|----------|----------|----------|------|------|
| ...

三、总结
- 要求总学分：XXX.X 学分
- 已获得学分：XXX.X 学分
- 超额学分：+XX.X 学分
- 总完成率：XXX.X%
- 不及格记录：X 门

四、结论
✅ 学分已修满！/ ❌ 学分未修满！
```

---

**文档版本：** v1.0  
**创建时间：** 2026-05-05  
**适用系统：** 浙江工商大学教务管理系统 V-9.0

#!/usr/bin/env node
/**
 * 人工智能赋能职教课堂的顶层设计、实践案例与应用实操
 * 2.5小时讲座PPT生成脚本
 */

const pptx = require('pptxgenjs');

// 创建PPT实例
const pres = new pptx();
pres.author = '蒋献';
pres.title = '人工智能赋能职教课堂的顶层设计、实践案例与应用实操';
pres.subject = '数字化教学设计培训';
pres.layout = 'LAYOUT_WIDE'; // 16:9

// ==================== 配色方案 ====================
const COLORS = {
  primary: '1E3A5F',      // 深蓝
  secondary: '2563EB',    // 亮蓝
  accent: 'F59E0B',       // 琥珀
  success: '10B981',      // 翠绿
  danger: 'EF4444',       // 红色
  text: '1F2937',         // 深灰
  lightText: '6B7280',    // 浅灰
  bg: 'FFFFFF',           // 白色
  lightBg: 'F3F4F6',      // 浅灰背景
  darkBg: '1E3A5F',       // 深蓝背景
  gradient1: '667EEA',    // 渐变1
  gradient2: '764BA2',    // 渐变2
};

// ==================== 通用样式 ====================
const FONT = {
  title: { fontSize: 36, bold: true, color: COLORS.text, fontFace: '微软雅黑' },
  subtitle: { fontSize: 24, bold: true, color: COLORS.primary, fontFace: '微软雅黑' },
  body: { fontSize: 16, color: COLORS.text, fontFace: '微软雅黑' },
  small: { fontSize: 12, color: COLORS.lightText, fontFace: '微软雅黑' },
  bullet: { fontSize: 15, color: COLORS.text, fontFace: '微软雅黑' },
  highlight: { fontSize: 16, bold: true, color: COLORS.secondary, fontFace: '微软雅黑' },
  code: { fontSize: 13, fontFace: 'Consolas', color: COLORS.text },
};

// ==================== 工具函数 ====================
function addBackground(slide, color) {
  slide.background = { color: color };
}

function addTextBox(slide, text, x, y, w, h, options) {
  const opts = { x, y, w, h, ...options };
  return slide.addText(text, opts);
}

function addShape(slide, shapeType, x, y, w, h, fill) {
  return slide.addShape(shapeType, { x, y, w, h, fill: { color: fill } });
}

function addBulletList(slide, items, x, y, w, h, options) {
  const bulletedItems = items.map(item => ({
    text: item.text || item,
    options: {
      fontSize: options?.fontSize || FONT.bullet.fontSize,
      color: options?.color || FONT.bullet.color,
      fontFace: options?.fontFace || FONT.bullet.fontFace,
      bold: item.bold || false,
      bullet: { type: 'bullet', code: '2022' },
      paragraphSpacingBefore: 6,
      paragraphSpacingAfter: 6,
      ...options,
    }
  }));
  return slide.addText(bulletedItems.map(i => i.text), {
    x, y, w, h,
    fontSize: options?.fontSize || FONT.bullet.fontSize,
    color: options?.color || FONT.bullet.color,
    fontFace: options?.fontFace || FONT.bullet.fontFace,
    bullet: { type: 'bullet', code: '2022' },
    paragraphSpacingBefore: 6,
    paragraphSpacingAfter: 6,
    ...options,
  });
}

// ==================== 第1页：封面 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);

  // 顶部装饰条
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  // 主标题
  addTextBox(slide, '人工智能赋能职教课堂', 1, 1.8, 11.33, 1, {
    fontSize: 44, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });

  // 副标题
  addTextBox(slide, '顶层设计 · 实践案例 · 应用实操', 1, 3.0, 11.33, 0.8, {
    fontSize: 28, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });

  // 分隔线
  addShape(slide, 'rect', 4, 4.0, 5.33, 0.04, COLORS.accent);

  // 补充说明
  addTextBox(slide, '数字化教学设计培训讲座', 1, 4.3, 11.33, 0.6, {
    fontSize: 20, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });

  // 底部信息
  addTextBox(slide, '培训地点：杭州  |  培训时长：2.5小时', 1, 6.5, 11.33, 0.5, {
    fontSize: 14, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '2026年6月', 1, 7.0, 11.33, 0.5, {
    fontSize: 14, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第2页：目录 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  // 标题栏
  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '目  录', 1, 0.2, 11.33, 0.8, {
    fontSize: 36, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 四个章节
  const chapters = [
    { num: '01', title: '背景与趋势', subtitle: 'AI+职业教育融合的时代背景', time: '30分钟' },
    { num: '02', title: '顶层设计', subtitle: '数字化教学设计的框架与方法', time: '40分钟' },
    { num: '03', title: '实践案例', subtitle: '国内职教AI应用典型案例分析', time: '30分钟' },
    { num: '04', title: '工具实操', subtitle: 'AI教学工具 hands-on 体验', time: '30分钟' },
  ];

  chapters.forEach((ch, i) => {
    const yPos = 1.6 + i * 1.5;

    // 序号圆圈
    addShape(slide, 'oval', 1.2, yPos, 0.9, 0.9, COLORS.secondary);
    addTextBox(slide, ch.num, 1.2, yPos + 0.15, 0.9, 0.6, {
      fontSize: 28, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });

    // 标题
    addTextBox(slide, ch.title, 2.5, yPos + 0.05, 6, 0.5, {
      fontSize: 22, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });

    // 副标题
    addTextBox(slide, ch.subtitle, 2.5, yPos + 0.55, 6, 0.4, {
      fontSize: 14, color: COLORS.lightText, fontFace: '微软雅黑',
    });

    // 时间标签
    addTextBox(slide, ch.time, 9.5, yPos + 0.2, 2.5, 0.5, {
      fontSize: 14, color: COLORS.secondary, fontFace: '微软雅黑', align: 'right',
    });
  });
})();

// ==================== 第3页：过渡页 - 第一部分 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '01', 1, 2, 11.33, 1, {
    fontSize: 72, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '背景与趋势', 1, 3.2, 11.33, 1, {
    fontSize: 40, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, 'AI+职业教育融合的时代背景', 1, 4.3, 11.33, 0.6, {
    fontSize: 20, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第4页：政策背景 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '国家政策驱动职业教育数字化', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  const policies = [
    { icon: '📋', title: '《职业教育数字化转型行动计划》', desc: '到2025年，建成一批全国性职业教育数字资源库' },
    { icon: '🎯', title: '《教育信息化2.0行动计划》', desc: '实现"三全两高一大"目标，推动AI+教育深度融合' },
    { icon: '🏫', title: '《关于深化现代职业教育体系建设改革的意见》', desc: '推进职业教育数字化转型，建设智慧校园' },
    { icon: '💡', title: '《新一代人工智能发展规划》', desc: '推广人工智能在教学、管理等方面的全流程应用' },
  ];

  policies.forEach((p, i) => {
    const yPos = 1.5 + i * 1.4;

    // 卡片背景
    addShape(slide, 'roundRect', 0.8, yPos, 11.73, 1.2, COLORS.lightBg);

    // 图标
    addTextBox(slide, p.icon, 1.0, yPos + 0.2, 0.8, 0.8, {
      fontSize: 28, align: 'center',
    });

    // 标题
    addTextBox(slide, p.title, 2.0, yPos + 0.1, 9, 0.5, {
      fontSize: 16, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });

    // 描述
    addTextBox(slide, p.desc, 2.0, yPos + 0.6, 9, 0.5, {
      fontSize: 13, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第5页：AI教育应用现状 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, 'AI在教育领域的应用现状', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 四宫格
  const areas = [
    { title: '智能备课', icon: '✍️', items: ['AI课件生成', '教案智能推荐', '教学资源检索'], color: COLORS.secondary },
    { title: '智慧课堂', icon: '🎓', items: ['实时互动反馈', '学情数据分析', '课堂行为识别'], color: COLORS.success },
    { title: '个性化学习', icon: '🎯', items: ['自适应学习路径', '知识图谱导航', '智能答疑辅导'], color: COLORS.accent },
    { title: '智能评价', icon: '📊', items: ['自动化作业批改', '学习诊断分析', '能力画像构建'], color: COLORS.danger },
  ];

  areas.forEach((area, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const xPos = 0.8 + col * 6.2;
    const yPos = 1.5 + row * 2.8;

    // 卡片
    addShape(slide, 'roundRect', xPos, yPos, 5.8, 2.5, COLORS.lightBg);

    // 顶部色条
    addShape(slide, 'roundRect', xPos, yPos, 5.8, 0.6, area.color);

    // 图标+标题
    addTextBox(slide, area.icon + ' ' + area.title, xPos + 0.3, yPos + 0.05, 5, 0.5, {
      fontSize: 18, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
    });

    // 内容项
    area.items.forEach((item, j) => {
      addTextBox(slide, '• ' + item, xPos + 0.5, yPos + 0.8 + j * 0.45, 4.8, 0.4, {
        fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
      });
    });
  });
})();

// ==================== 第6页：职教课堂的痛点 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '职教课堂数字化的痛点与机遇', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 左侧：痛点
  addTextBox(slide, '当前痛点', 0.8, 1.5, 5, 0.5, {
    fontSize: 22, bold: true, color: COLORS.danger, fontFace: '微软雅黑',
  });

  const painPoints = [
    '学生基础差异大，难以因材施教',
    '实训资源有限，动手机会不足',
    '教师备课负担重，资源开发成本高',
    '评价方式单一，缺乏过程性数据',
    '教学内容更新滞后于产业发展',
  ];

  painPoints.forEach((p, i) => {
    addTextBox(slide, '❌ ' + p, 0.8, 2.1 + i * 0.6, 5, 0.5, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 右侧：机遇
  addTextBox(slide, 'AI带来的机遇', 7, 1.5, 5.5, 0.5, {
    fontSize: 22, bold: true, color: COLORS.success, fontFace: '微软雅黑',
  });

  const opportunities = [
    'AI实现个性化学习路径推荐',
    '虚拟仿真拓展实训场景',
    '智能工具提升教师效率',
    '数据驱动精准教学决策',
    '产业数据实时同步更新',
  ];

  opportunities.forEach((o, i) => {
    addTextBox(slide, '✅ ' + o, 7, 2.1 + i * 0.6, 5.5, 0.5, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 中间箭头
  addTextBox(slide, '→', 6.2, 3.5, 1, 1, {
    fontSize: 48, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第7页：过渡页 - 第二部分 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '02', 1, 2, 11.33, 1, {
    fontSize: 72, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '顶层设计', 1, 3.2, 11.33, 1, {
    fontSize: 40, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '数字化教学设计的框架与方法', 1, 4.3, 11.33, 0.6, {
    fontSize: 20, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第8页：ADDIE模型演进 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, 'ADDIE模型在AI时代的演进', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 传统ADDIE vs AI-enhanced ADDIE 对比
  const phases = [
    { phase: 'Analysis 分析', traditional: '经验判断、问卷调查', ai: '学情数据挖掘、知识图谱分析' },
    { phase: 'Design 设计', traditional: '教师手工设计教案', ai: 'AI辅助生成教学方案' },
    { phase: 'Develop 开发', traditional: 'PPT+讲义制作', ai: 'AI课件生成、资源智能推荐' },
    { phase: 'Implement 实施', traditional: '课堂讲授+板书', ai: '智慧课堂、实时互动反馈' },
    { phase: 'Evaluate 评价', traditional: '期末考试+作业', ai: '过程性评价、学习诊断分析' },
  ];

  // 表头
  addShape(slide, 'rect', 0.8, 1.5, 11.73, 0.6, COLORS.secondary);
  addTextBox(slide, '阶段', 0.9, 1.55, 2, 0.5, { fontSize: 14, bold: true, color: 'FFFFFF', fontFace: '微软雅黑' });
  addTextBox(slide, '传统方式', 3.5, 1.55, 4, 0.5, { fontSize: 14, bold: true, color: 'FFFFFF', fontFace: '微软雅黑' });
  addTextBox(slide, 'AI增强方式', 8, 1.55, 4, 0.5, { fontSize: 14, bold: true, color: 'FFFFFF', fontFace: '微软雅黑' });

  phases.forEach((p, i) => {
    const yPos = 2.2 + i * 0.9;
    const bgColor = i % 2 === 0 ? COLORS.lightBg : COLORS.bg;
    addShape(slide, 'rect', 0.8, yPos, 11.73, 0.8, bgColor);

    addTextBox(slide, p.phase, 0.9, yPos + 0.1, 2, 0.6, {
      fontSize: 14, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
    });
    addTextBox(slide, p.traditional, 3.5, yPos + 0.1, 4, 0.6, {
      fontSize: 13, color: COLORS.lightText, fontFace: '微软雅黑',
    });
    addTextBox(slide, p.ai, 8, yPos + 0.1, 4, 0.6, {
      fontSize: 13, bold: true, color: COLORS.success, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第9页：三层架构设计 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, 'AI赋能职教课堂的三层架构', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 三层架构 - 从下到上
  const layers = [
    {
      title: '应用层 — AI辅助教学工具',
      color: COLORS.secondary,
      items: ['智能备课系统', '智慧课堂平台', '自适应学习系统', '自动化评价工具'],
      y: 5.5, h: 2.5,
    },
    {
      title: '数据层 — 学情数据采集与分析',
      color: COLORS.accent,
      items: ['学习行为数据', '知识掌握数据', '互动参与数据', '学习成果数据'],
      y: 3.0, h: 2.3,
    },
    {
      title: '基础设施层 — 数字化教学环境',
      color: COLORS.success,
      items: ['云平台/服务器', '网络环境', '智能终端设备', '教学管理系统'],
      y: 1.5, h: 1.3,
    },
  ];

  layers.forEach((layer, i) => {
    // 层级方块
    addShape(slide, 'roundRect', 1.5, layer.y, 10.33, layer.h, layer.color);

    // 标题
    addTextBox(slide, layer.title, 1.8, layer.y + 0.15, 9, 0.5, {
      fontSize: 18, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });

    // 内容项
    layer.items.forEach((item, j) => {
      addTextBox(slide, '• ' + item, 2.5, layer.y + 0.7 + j * 0.4, 8, 0.4, {
        fontSize: 14, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
      });
    });

    // 箭头（层与层之间）
    if (i < layers.length - 1) {
      addTextBox(slide, '▲', 6.3, layer.y - 0.4, 0.8, 0.5, {
        fontSize: 24, color: COLORS.text, fontFace: '微软雅黑', align: 'center',
      });
    }
  });
})();

// ==================== 第10页：以学习者为中心的设计原则 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '以学习者为中心的设计原则', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  const principles = [
    { num: '1', title: '个性化', desc: '基于学生画像提供差异化学习路径', icon: '👤' },
    { num: '2', title: '互动性', desc: '设计多层次的师生、生生互动环节', icon: '🤝' },
    { num: '3', title: '实践性', desc: '理论联系实际，强化动手操作能力', icon: '🔧' },
    { num: '4', title: '反馈性', desc: '及时的学习反馈与持续改进机制', icon: '💬' },
    { num: '5', title: '数据驱动', desc: '用数据支撑教学决策与评价', icon: '📊' },
  ];

  principles.forEach((p, i) => {
    const yPos = 1.5 + i * 1.4;

    // 序号
    addShape(slide, 'oval', 1, yPos + 0.1, 0.8, 0.8, COLORS.secondary);
    addTextBox(slide, p.num, 1, yPos + 0.15, 0.8, 0.7, {
      fontSize: 24, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });

    // 标题
    addTextBox(slide, p.icon + ' ' + p.title, 2.1, yPos + 0.05, 3, 0.5, {
      fontSize: 18, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });

    // 描述
    addTextBox(slide, p.desc, 2.1, yPos + 0.6, 9, 0.5, {
      fontSize: 14, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第11页：过渡页 - 第三部分 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '03', 1, 2, 11.33, 1, {
    fontSize: 72, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '实践案例', 1, 3.2, 11.33, 1, {
    fontSize: 40, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '国内职教AI应用典型案例分析', 1, 4.3, 11.33, 0.6, {
    fontSize: 20, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第12页：案例1 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '案例1：浙江某高职院校AI+实训教学平台', 1, 0.2, 11.33, 0.8, {
    fontSize: 26, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 案例背景
  addTextBox(slide, '案例背景', 0.8, 1.5, 5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });
  addTextBox(slide, '该校面向智能制造专业群，建设了AI+实训教学平台，整合虚拟仿真、智能评价、个性化学习等功能，覆盖3个专业、500+学生。', 0.8, 2.1, 5.5, 1.5, {
    fontSize: 14, color: COLORS.text, fontFace: '微软雅黑', lineSpacingMultiple: 1.5,
  });

  // 技术方案
  addTextBox(slide, '技术方案', 7, 1.5, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });
  const techItems = [
    '虚拟仿真平台（Unity3D）',
    'AI学习分析引擎',
    '知识图谱构建',
    '智能评价系统',
  ];
  techItems.forEach((item, i) => {
    addTextBox(slide, '• ' + item, 7, 2.1 + i * 0.4, 5.5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 成效数据
  addTextBox(slide, '成效数据', 0.8, 4.0, 5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.success, fontFace: '微软雅黑',
  });
  const results = [
    '学生实操成绩提升23%',
    '教师备课时间减少40%',
    '学生满意度达到92%',
    '实训资源利用率提升3倍',
  ];
  results.forEach((r, i) => {
    addTextBox(slide, '📈 ' + r, 0.8, 4.6 + i * 0.45, 5.5, 0.4, {
      fontSize: 14, bold: true, color: COLORS.success, fontFace: '微软雅黑',
    });
  });

  // 可复制经验
  addTextBox(slide, '可复制经验', 7, 4.0, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.accent, fontFace: '微软雅黑',
  });
  const experiences = [
    '分阶段推进，先试点后推广',
    '校企共建，引入产业资源',
    '重视教师培训，提升数字素养',
    '建立数据驱动的持续改进机制',
  ];
  experiences.forEach((e, i) => {
    addTextBox(slide, '💡 ' + e, 7, 4.6 + i * 0.45, 5.5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第13页：案例2 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '案例2：深圳职业技术学院智能教学系统', 1, 0.2, 11.33, 0.8, {
    fontSize: 26, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 核心特色
  addTextBox(slide, '核心特色', 0.8, 1.5, 5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const features = [
    { title: 'AI助教系统', desc: '7×24小时在线答疑，覆盖80%常见问题' },
    { title: '智能排课系统', desc: '基于学生画像和课程难度智能排课' },
    { title: '学习预警机制', desc: '实时监测学习状态，提前预警学业风险' },
    { title: '虚拟教研室', desc: '跨校区教师协作备课与资源共享' },
  ];

  features.forEach((f, i) => {
    const yPos = 2.1 + i * 1.2;
    addShape(slide, 'roundRect', 0.8, yPos, 5.5, 1.0, COLORS.lightBg);
    addTextBox(slide, f.title, 1.0, yPos + 0.1, 5, 0.4, {
      fontSize: 16, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
    });
    addTextBox(slide, f.desc, 1.0, yPos + 0.5, 5, 0.5, {
      fontSize: 13, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });

  // 实施路径
  addTextBox(slide, '实施路径', 7, 1.5, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const steps = [
    '第一阶段：基础设施建设（6个月）',
    '第二阶段：平台开发与集成（8个月）',
    '第三阶段：试点应用与优化（4个月）',
    '第四阶段：全面推广与深化（持续）',
  ];

  steps.forEach((s, i) => {
    addTextBox(slide, (i + 1) + '. ' + s, 7, 2.1 + i * 0.7, 5.5, 0.5, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 关键成功因素
  addTextBox(slide, '关键成功因素', 7, 5.2, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.accent, fontFace: '微软雅黑',
  });
  const factors = [
    '校领导高度重视，一把手工程',
    '充足的经费保障（年均500万+）',
    '专业团队建设（技术+教学）',
    '与头部企业深度合作',
  ];
  factors.forEach((f, i) => {
    addTextBox(slide, '★ ' + f, 7, 5.8 + i * 0.5, 5.5, 0.4, {
      fontSize: 13, color: COLORS.text, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第14页：案例3和4 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '案例3&4：AI辅助课程设计 + 虚拟仿真实训', 1, 0.2, 11.33, 0.8, {
    fontSize: 26, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 案例3
  addTextBox(slide, '案例3：南京职教中心AI辅助课程设计', 0.8, 1.5, 11, 0.5, {
    fontSize: 18, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });
  addShape(slide, 'roundRect', 0.8, 2.0, 5.8, 3.5, COLORS.lightBg);

  const case3 = [
    'AI辅助课程设计：使用AI工具生成课程大纲、教学活动设计',
    '智能资源推荐：根据教学目标自动推荐教学资源',
    '学情分析看板：实时展示班级学习进度和知识掌握情况',
    '成效：课程设计效率提升60%，资源匹配精准度提升45%',
  ];
  case3.forEach((item, i) => {
    addTextBox(slide, '• ' + item, 1.0, 2.2 + i * 0.75, 5.4, 0.7, {
      fontSize: 13, color: COLORS.text, fontFace: '微软雅黑', lineSpacingMultiple: 1.3,
    });
  });

  // 案例4
  addTextBox(slide, '案例4：北京职业院校虚拟仿真实训', 7, 1.5, 5.5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });
  addShape(slide, 'roundRect', 7, 2.0, 5.8, 3.5, COLORS.lightBg);

  const case4 = [
    '虚拟仿真实训：VR/AR技术构建沉浸式实训环境',
    'AI操作指导：实时监测操作步骤，提供智能纠错',
    '安全实训场景：高危场景虚拟训练，零风险学习',
    '成效：实训安全事故降为0，技能掌握速度提升35%',
  ];
  case4.forEach((item, i) => {
    addTextBox(slide, '• ' + item, 7.2, 2.2 + i * 0.75, 5.4, 0.7, {
      fontSize: 13, color: COLORS.text, fontFace: '微软雅黑', lineSpacingMultiple: 1.3,
    });
  });

  // 底部总结
  addShape(slide, 'roundRect', 0.8, 5.8, 11.73, 1.5, COLORS.primary);
  addTextBox(slide, '案例共性总结', 0.8, 5.9, 11.73, 0.5, {
    fontSize: 18, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '① 顶层设计先行  ② 分阶段推进  ③ 校企深度合作  ④ 数据驱动改进  ⑤ 重视教师培训', 0.8, 6.4, 11.73, 0.7, {
    fontSize: 14, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第15页：过渡页 - 第四部分 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '04', 1, 2, 11.33, 1, {
    fontSize: 72, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '工具实操', 1, 3.2, 11.33, 1, {
    fontSize: 40, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, 'AI教学工具 hands-on 体验', 1, 4.3, 11.33, 0.6, {
    fontSize: 20, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第16页：AI课件生成工具 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '实验1：AI辅助课件设计', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 推荐工具
  addTextBox(slide, '推荐工具', 0.8, 1.5, 5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const tools = [
    { name: 'Gamma', desc: 'AI驱动演示文稿生成', url: 'gamma.app' },
    { name: 'MindShow', desc: 'Markdown转PPT', url: 'mindshow.fun' },
    { name: 'WPS AI', desc: '国产AI办公套件', url: 'wps.cn' },
    { name: '腾讯智影', desc: 'AI视频+课件生成', url: 'zenvideo.qq.com' },
  ];

  tools.forEach((tool, i) => {
    const yPos = 2.1 + i * 0.9;
    addShape(slide, 'roundRect', 0.8, yPos, 5.5, 0.7, COLORS.lightBg);
    addTextBox(slide, '🔧 ' + tool.name, 1.0, yPos + 0.05, 3, 0.35, {
      fontSize: 15, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });
    addTextBox(slide, tool.desc + ' | ' + tool.url, 1.0, yPos + 0.4, 5, 0.3, {
      fontSize: 11, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });

  // 操作步骤
  addTextBox(slide, '操作步骤', 7, 1.5, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const steps = [
    '1. 确定课程主题和教学目标',
    '2. 编写提示词（Prompt）',
    '3. 生成课件初稿',
    '4. 人工审核与调整',
    '5. 添加互动设计环节',
    '6. 导出并测试',
  ];

  steps.forEach((s, i) => {
    addTextBox(slide, s, 7, 2.1 + i * 0.6, 5.5, 0.5, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 提示词示例
  addTextBox(slide, '提示词示例', 0.8, 5.8, 5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.accent, fontFace: '微软雅黑',
  });
  addShape(slide, 'roundRect', 0.8, 6.3, 11.73, 1.0, COLORS.lightBg);
  addTextBox(slide, '"请生成一份关于"人工智能基础"的课件，包含：①AI发展历史 ②机器学习概念 ③应用场景 ④互动讨论环节。面向高职学生，共15页。"', 1.0, 6.4, 11.33, 0.8, {
    fontSize: 12, color: COLORS.text, fontFace: 'Consolas', lineSpacingMultiple: 1.3,
  });
})();

// ==================== 第17页：数字化教学设计实操 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '实验2：数字化教学设计实操', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 教学设计模板要素
  addTextBox(slide, '教学设计模板要素', 0.8, 1.5, 5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const elements = [
    { num: '1', title: '学情分析', desc: '学生基础、学习风格、先修知识' },
    { num: '2', title: '教学目标', desc: '布鲁姆分类法：知识/技能/素养' },
    { num: '3', title: '教学活动', desc: '导入→讲授→互动→练习→总结' },
    { num: '4', title: '评价方案', desc: '形成性评价+总结性评价' },
    { num: '5', title: 'AI工具嵌入', desc: '明确每个环节的AI工具使用点' },
  ];

  elements.forEach((el, i) => {
    const yPos = 2.1 + i * 1.0;
    addShape(slide, 'roundRect', 0.8, yPos, 5.5, 0.85, COLORS.lightBg);
    addShape(slide, 'oval', 1.0, yPos + 0.15, 0.5, 0.5, COLORS.secondary);
    addTextBox(slide, el.num, 1.0, yPos + 0.2, 0.5, 0.4, {
      fontSize: 16, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });
    addTextBox(slide, el.title, 1.7, yPos + 0.05, 4, 0.35, {
      fontSize: 15, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });
    addTextBox(slide, el.desc, 1.7, yPos + 0.45, 4, 0.35, {
      fontSize: 12, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });

  // 推荐平台
  addTextBox(slide, '推荐平台', 7, 1.5, 5.5, 0.5, {
    fontSize: 20, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const platforms = [
    { name: '雨课堂', desc: '清华出品，智慧课堂工具' },
    { name: '学习通', desc: '超星平台，资源丰富' },
    { name: '课堂派', desc: '课堂管理与互动' },
    { name: '腾讯课堂', desc: '在线教学平台' },
  ];

  platforms.forEach((p, i) => {
    const yPos = 2.1 + i * 0.9;
    addShape(slide, 'roundRect', 7, yPos, 5.5, 0.7, COLORS.lightBg);
    addTextBox(slide, '📱 ' + p.name, 7.2, yPos + 0.05, 3, 0.35, {
      fontSize: 15, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });
    addTextBox(slide, p.desc, 7.2, yPos + 0.4, 5, 0.3, {
      fontSize: 12, color: COLORS.lightText, fontFace: '微软雅黑',
    });
  });

  // 实操任务
  addTextBox(slide, '实操任务', 0.8, 6.5, 11.73, 0.5, {
    fontSize: 18, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '请基于自己的专业课程，使用AI工具完成一份数字化教学设计方案（包含上述5个要素），30分钟后分组展示。', 0.8, 7.0, 11.73, 0.5, {
    fontSize: 14, color: COLORS.text, fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第18页：提示词设计技巧 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, 'AI工具使用核心：提示词（Prompt）设计', 1, 0.2, 11.33, 0.8, {
    fontSize: 28, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 提示词设计框架
  addTextBox(slide, '提示词设计框架：CREATE', 0.8, 1.5, 11, 0.5, {
    fontSize: 22, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });

  const create = [
    { letter: 'C', word: 'Context', desc: '提供背景信息', example: '面向高职大二学生...' },
    { letter: 'R', word: 'Role', desc: '设定AI角色', example: '你是一位资深职教教师...' },
    { letter: 'E', word: 'Explicit', desc: '明确任务要求', example: '请生成15页课件...' },
    { letter: 'A', word: 'Action', desc: '指定输出格式', example: '以表格形式输出...' },
    { letter: 'T', word: 'Test', desc: '设置检验标准', example: '确保包含互动环节...' },
    { letter: 'E', word: 'Evaluate', desc: '迭代优化', example: '根据反馈调整...' },
  ];

  create.forEach((item, i) => {
    const xPos = 0.8 + (i % 3) * 4.0;
    const yPos = 2.2 + Math.floor(i / 3) * 2.5;

    addShape(slide, 'roundRect', xPos, yPos, 3.6, 2.2, COLORS.lightBg);

    // 字母
    addShape(slide, 'oval', xPos + 0.2, yPos + 0.2, 0.7, 0.7, COLORS.secondary);
    addTextBox(slide, item.letter, xPos + 0.2, yPos + 0.25, 0.7, 0.6, {
      fontSize: 24, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });

    // 单词
    addTextBox(slide, item.word, xPos + 1.1, yPos + 0.2, 2.3, 0.4, {
      fontSize: 16, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });

    // 说明
    addTextBox(slide, item.desc, xPos + 1.1, yPos + 0.7, 2.3, 0.4, {
      fontSize: 13, color: COLORS.lightText, fontFace: '微软雅黑',
    });

    // 示例
    addTextBox(slide, item.example, xPos + 0.3, yPos + 1.3, 3.0, 0.7, {
      fontSize: 11, color: COLORS.text, fontFace: '微软雅黑', lineSpacingMultiple: 1.2,
    });
  });
})();

// ==================== 第19页：过渡页 - 总结 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '总结与展望', 1, 2, 11.33, 1, {
    fontSize: 40, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, 'AI赋能职教课堂的核心要点回顾', 1, 3.2, 11.33, 0.6, {
    fontSize: 22, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第20页：核心要点回顾 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '核心要点回顾', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  const keyPoints = [
    { num: '1', title: '趋势不可逆', desc: 'AI+教育已从可选项变为必选项，职业教育数字化是国家战略方向', color: COLORS.secondary },
    { num: '2', title: '设计先行', desc: '好的教学设计是成功的关键，AI是工具而非目的', color: COLORS.success },
    { num: '3', title: '数据驱动', desc: '用数据支撑教学决策，实现精准教学和个性化学习', color: COLORS.accent },
    { num: '4', title: '教师角色转变', desc: '从知识传授者转变为学习引导者和课程设计者', color: COLORS.danger },
    { num: '5', title: '持续迭代', desc: 'AI技术在快速发展，需要保持学习心态，持续优化教学方案', color: COLORS.gradient2 },
  ];

  keyPoints.forEach((kp, i) => {
    const yPos = 1.5 + i * 1.4;

    // 序号
    addShape(slide, 'roundRect', 0.8, yPos, 0.8, 0.8, kp.color);
    addTextBox(slide, kp.num, 0.8, yPos + 0.1, 0.8, 0.6, {
      fontSize: 28, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
    });

    // 标题
    addTextBox(slide, kp.title, 1.9, yPos + 0.05, 4, 0.4, {
      fontSize: 20, bold: true, color: COLORS.text, fontFace: '微软雅黑',
    });

    // 描述
    addTextBox(slide, kp.desc, 1.9, yPos + 0.55, 10, 0.6, {
      fontSize: 14, color: COLORS.lightText, fontFace: '微软雅黑', lineSpacingMultiple: 1.3,
    });
  });
})();

// ==================== 第21页：行动计划 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.bg);

  addShape(slide, 'rect', 0, 0, 13.33, 1.2, COLORS.primary);
  addTextBox(slide, '制定您的行动计划', 1, 0.2, 11.33, 0.8, {
    fontSize: 30, bold: true, color: 'FFFFFF', fontFace: '微软雅黑',
  });

  // 短期（1个月内）
  addTextBox(slide, '📅 短期行动（1个月内）', 0.8, 1.5, 5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.secondary, fontFace: '微软雅黑',
  });
  const shortTerm = [
    '选择1-2个AI工具进行深度体验',
    '完成一节课程的AI辅助课件设计',
    '加入AI教育应用交流社群',
  ];
  shortTerm.forEach((s, i) => {
    addTextBox(slide, '✓ ' + s, 0.8, 2.1 + i * 0.5, 5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 中期（一学期）
  addTextBox(slide, '📅 中期行动（一学期内）', 7, 1.5, 5.5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.success, fontFace: '微软雅黑',
  });
  const midTerm = [
    '完成一门课程的数字化教学设计',
    '在课堂中实践AI辅助教学',
    '收集学生反馈和学习数据',
  ];
  midTerm.forEach((m, i) => {
    addTextBox(slide, '✓ ' + m, 7, 2.1 + i * 0.5, 5.5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 长期（一学年）
  addTextBox(slide, '📅 长期行动（一学年内）', 0.8, 4.2, 5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.accent, fontFace: '微软雅黑',
  });
  const longTerm = [
    '建成1-2门AI赋能的示范课程',
    '形成可推广的教学模式',
    '申报相关教改课题',
  ];
  longTerm.forEach((l, i) => {
    addTextBox(slide, '✓ ' + l, 0.8, 4.8 + i * 0.5, 5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });

  // 资源推荐
  addTextBox(slide, '📚 推荐学习资源', 7, 4.2, 5.5, 0.5, {
    fontSize: 18, bold: true, color: COLORS.danger, fontFace: '微软雅黑',
  });
  const resources = [
    '《AI+教育：未来已来》',
    '中国大学MOOC"人工智能教育应用"',
    '智慧职教平台（icve.com）',
    'AI教育应用微信公众号',
  ];
  resources.forEach((r, i) => {
    addTextBox(slide, '• ' + r, 7, 4.8 + i * 0.5, 5.5, 0.4, {
      fontSize: 14, color: COLORS.text, fontFace: '微软雅黑',
    });
  });
})();

// ==================== 第22页：Q&A ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, 'Q & A', 1, 2, 11.33, 1, {
    fontSize: 64, bold: true, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '提问与交流', 1, 3.2, 11.33, 0.6, {
    fontSize: 28, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });

  addShape(slide, 'rect', 4, 4.2, 5.33, 0.04, COLORS.accent);

  addTextBox(slide, '欢迎提出您在AI教学应用中遇到的任何问题', 1, 4.6, 11.33, 0.6, {
    fontSize: 18, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 第23页：结尾页 ====================
(function() {
  const slide = pres.addSlide();
  addBackground(slide, COLORS.primary);
  addShape(slide, 'rect', 0, 0, 13.33, 0.15, COLORS.accent);

  addTextBox(slide, '感谢聆听！', 1, 2, 11.33, 1, {
    fontSize: 48, bold: true, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });

  addShape(slide, 'rect', 4, 3.3, 5.33, 0.04, COLORS.accent);

  addTextBox(slide, '人工智能赋能职教课堂', 1, 3.7, 11.33, 0.6, {
    fontSize: 24, color: COLORS.accent, fontFace: '微软雅黑', align: 'center',
  });
  addTextBox(slide, '顶层设计 · 实践案例 · 应用实操', 1, 4.4, 11.33, 0.6, {
    fontSize: 20, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });

  addTextBox(slide, '让我们共同探索AI+职业教育的无限可能', 1, 5.5, 11.33, 0.6, {
    fontSize: 16, color: 'FFFFFF', fontFace: '微软雅黑', align: 'center',
  });

  addTextBox(slide, '培训地点：杭州  |  2026年6月', 1, 7.0, 11.33, 0.5, {
    fontSize: 14, color: 'B0C4DE', fontFace: '微软雅黑', align: 'center',
  });

  // AI标识
  addTextBox(slide, '本课件由AI辅助创作', 1, 7.8, 11.33, 0.4, {
    fontSize: 11, color: '6B7280', fontFace: '微软雅黑', align: 'center',
  });
})();

// ==================== 保存PPT ====================
const outputPath = '/home/admin/.openclaw/workspace/人工智能赋能职教课堂.pptx';
pres.writeFile({ fileName: outputPath }).then(function() {
  console.log('✅ PPT已生成：' + outputPath);
}).catch(function(err) {
  console.error('❌ 生成失败：' + err);
});

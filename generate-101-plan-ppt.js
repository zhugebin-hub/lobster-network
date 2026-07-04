// 生成"101计划"首批核心课程培育推进会汇报PPT
const pptxgenjs = require("pptxgenjs");

const pres = new pptxgenjs();

// 页面设置
pres.defineLayout({ name: "LAYOUT_16_9", width: 13.33, height: 7.5 });
pres.layout = "LAYOUT_16_9";

// 配色方案
const colors = {
  primary: "#1E3A5F",      // 深蓝
  secondary: "#2C5F8A",    // 中蓝
  accent: "#E67E22",       // 橙色强调
  light: "#F8F9FA",        // 浅灰背景
  white: "#FFFFFF",
  text: "#333333",
  muted: "#6C757D",
  success: "#27AE60"
};

// ========== 幻灯片1: 封面 ==========
const slide1 = pres.addSlide();
slide1.background = { fill: colors.primary };

slide1.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 0.15,
  fill: colors.accent
});

slide1.addText("“101计划”首批核心课程培育推进会", {
  x: 1, y: 1.5, w: 11.33, h: 1.2,
  fontSize: 36,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true,
  align: "center",
  lineSpacingMultiple: 1.2
});

slide1.addText("计算机网络课程建设构想", {
  x: 1, y: 3, w: 11.33, h: 0.8,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.accent,
  bold: true,
  align: "center"
});

slide1.addText("汇报人：诸葛斌  |  2026年6月25日\n科创大楼206会议室", {
  x: 1, y: 5.5, w: 11.33, h: 0.8,
  fontSize: 16,
  fontFace: "微软雅黑",
  color: colors.muted,
  align: "center"
});

// ========== 幻灯片2: 101计划背景 ==========
const slide2 = pres.addSlide();
slide2.background = { fill: colors.white };

slide2.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 1.2,
  fill: colors.primary
});
slide2.addText("📋 101计划背景与意义", {
  x: 0.5, y: 0.15, w: 12, h: 0.9,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true
});

slide2.addText("政策背景", {
  x: 0.8, y: 1.6, w: 3, h: 0.5,
  fontSize: 20,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true
});

slide2.addText("• 教育部统筹的拔尖创新人才培养筑基性工程\n• 汇聚顶尖高校、顶尖师资、顶尖出版单位\n• 以课程、教材、教师和实践项目为核心要素\n• 带动教育教学系统全面改革", {
  x: 0.8, y: 2.2, w: 11, h: 2.2,
  fontSize: 16,
  fontFace: "微软雅黑",
  color: colors.text,
  lineSpacingMultiple: 1.5
});

slide2.addShape("rectangle", {
  x: 7, y: 4.5, w: 5.5, h: 2,
  fill: colors.light,
  rectRadius: 0.2,
  line: { color: colors.accent, width: 2 }
});

slide2.addText("🎯 核心目标\n\n建设一流核心课程\n打造一流核心教材\n培养一流核心师资", {
  x: 7.2, y: 4.6, w: 5.1, h: 1.8,
  fontSize: 16,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true,
  align: "center"
});

// ========== 幻灯片3: 课程建设现状 ==========
const slide3 = pres.addSlide();
slide3.background = { fill: colors.white };

slide3.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 1.2,
  fill: colors.primary
});
slide3.addText("🖥️ 计算机网络课程建设现状", {
  x: 0.5, y: 0.15, w: 12, h: 0.9,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true
});

slide3.addText("✅ 已完成工作", {
  x: 0.8, y: 1.6, w: 4, h: 0.5,
  fontSize: 18,
  fontFace: "微软雅黑",
  color: colors.success,
  bold: true
});

slide3.addText("• 课程教学大纲已完善\n• 核心知识点体系已构建\n• 实验实践环节已优化\n• 考核评价体系已建立", {
  x: 0.8, y: 2.2, w: 5, h: 2,
  fontSize: 15,
  fontFace: "微软雅黑",
  color: colors.text,
  lineSpacingMultiple: 1.5
});

slide3.addText("🔄 进行中工作", {
  x: 7, y: 1.6, w: 4, h: 0.5,
  fontSize: 18,
  fontFace: "微软雅黑",
  color: colors.accent,
  bold: true
});

slide3.addText("• 智慧树平台在线课程部署\n• 数字化教学资源建设\n• 互动式教学模块开发\n• 课程视频录制与剪辑", {
  x: 7, y: 2.2, w: 5, h: 2,
  fontSize: 15,
  fontFace: "微软雅黑",
  color: colors.text,
  lineSpacingMultiple: 1.5
});

slide3.addShape("rectangle", {
  x: 0.8, y: 5, w: 11.5, h: 0.6,
  fill: colors.light,
  rectRadius: 0.1
});

slide3.addText("课程建设进度：65%", {
  x: 0.9, y: 5.05, w: 3, h: 0.5,
  fontSize: 14,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true
});

slide3.addShape("rectangle", {
  x: 4, y: 5.15, w: 7, h: 0.3,
  fill: colors.success,
  rectRadius: 0.05
});

// ========== 幻灯片4: 智慧树部署进展 ==========
const slide4 = pres.addSlide();
slide4.background = { fill: colors.white };

slide4.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 1.2,
  fill: colors.primary
});
slide4.addText("🌳 智慧树在线课程部署进展", {
  x: 0.5, y: 0.15, w: 12, h: 0.9,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true
});

slide4.addText("平台优势", {
  x: 0.8, y: 1.6, w: 3, h: 0.5,
  fontSize: 18,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true
});

slide4.addText("• 国内领先的在线教育平台\n• 支持大规模在线开放课程\n• 完善的学情分析系统\n• 跨校共享与学分互认", {
  x: 0.8, y: 2.2, w: 5, h: 2,
  fontSize: 15,
  fontFace: "微软雅黑",
  color: colors.text,
  lineSpacingMultiple: 1.5
});

slide4.addText("部署清单", {
  x: 7, y: 1.6, w: 3, h: 0.5,
  fontSize: 18,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true
});

const deployItems = [
  { text: "✓ 课程框架搭建", done: true },
  { text: "✓ 教学视频上传", done: true },
  { text: "✓ 章节测验配置", done: true },
  { text: "⟳ 讨论区设置", done: false },
  { text: "⟳ 作业批改规则", done: false },
  { text: "○ 期末考试配置", done: false }
];

let deployY = 2.2;
deployItems.forEach(item => {
  slide4.addText(item.text, {
    x: 7, y: deployY, w: 5, h: 0.4,
    fontSize: 15,
    fontFace: "微软雅黑",
    color: item.done ? colors.success : colors.muted,
    bold: item.done
  });
  deployY += 0.4;
});

// ========== 幻灯片5: 建设构想 ==========
const slide5 = pres.addSlide();
slide5.background = { fill: colors.white };

slide5.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 1.2,
  fill: colors.primary
});
slide5.addText("🚀 建设构想与未来规划", {
  x: 0.5, y: 0.15, w: 12, h: 0.9,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true
});

const plans = [
  {
    title: "📚 教材建设",
    desc: "编写符合101计划标准的\n计算机网络核心教材",
    color: colors.primary
  },
  {
    title: "👨‍🏫 师资培养",
    desc: "打造高水平教学团队\n提升教师数字化教学能力",
    color: colors.secondary
  },
  {
    title: "💻 实践平台",
    desc: "建设虚拟仿真实验平台\n强化学生动手能力培养",
    color: colors.accent
  },
  {
    title: "🌐 资源共享",
    desc: "推动跨校课程共享\n实现优质教育资源辐射",
    color: colors.success
  }
];

let planX = 0.6;
plans.forEach(plan => {
  slide5.addShape("rectangle", {
    x: planX, y: 1.8, w: 3, h: 2.5,
    fill: colors.light,
    rectRadius: 0.15,
    line: { color: plan.color, width: 2 }
  });

  slide5.addText(plan.title, {
    x: planX + 0.2, y: 1.9, w: 2.6, h: 0.5,
    fontSize: 18,
    fontFace: "微软雅黑",
    color: plan.color,
    bold: true,
    align: "center"
  });

  slide5.addText(plan.desc, {
    x: planX + 0.2, y: 2.5, w: 2.6, h: 1.5,
    fontSize: 14,
    fontFace: "微软雅黑",
    color: colors.text,
    align: "center",
    lineSpacingMultiple: 1.4
  });

  planX += 3.2;
});

// ========== 幻灯片6: 预期成果 ==========
const slide6 = pres.addSlide();
slide6.background = { fill: colors.white };

slide6.addShape("rectangle", {
  x: 0, y: 0, w: "100%", h: 1.2,
  fill: colors.primary
});
slide6.addText("🎯 预期成果与总结", {
  x: 0.5, y: 0.15, w: 12, h: 0.9,
  fontSize: 28,
  fontFace: "微软雅黑",
  color: colors.white,
  bold: true
});

const achievements = [
  "建成符合101计划标准的计算机网络核心课程",
  "完成智慧树平台在线课程部署与运营",
  "出版配套核心教材与实验指导书",
  "形成可复制推广的课程建设模式",
  "培养一支高水平数字化教学团队"
];

let achieveY = 1.8;
achievements.forEach((item, index) => {
  slide6.addShape("rectangle", {
    x: 0.8, y: achieveY, w: 0.5, h: 0.5,
    fill: colors.accent,
    rectRadius: 0.1
  });

  slide6.addText(`${index + 1}. ${item}`, {
    x: 1.5, y: achieveY - 0.05, w: 10, h: 0.6,
    fontSize: 18,
    fontFace: "微软雅黑",
    color: colors.text,
    bold: true
  });

  achieveY += 0.9;
});

slide6.addText("感谢聆听！\n欢迎批评指正", {
  x: 0, y: 5.5, w: 13.33, h: 1,
  fontSize: 24,
  fontFace: "微软雅黑",
  color: colors.primary,
  bold: true,
  align: "center"
});

// 保存文件
const outputPath = "/home/admin/.openclaw/workspace/101计划_计算机网络课程建设构想.pptx";
pres.writeFile({ outputFileName: outputPath })
  .then(() => {
    console.log(`PPT已生成：${outputPath}`);
  })
  .catch(err => {
    console.error("生成PPT失败：", err);
  });
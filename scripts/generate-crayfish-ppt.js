const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();

// Slide layout
pres.defineLayout({ name: "WIDE", width: 13.33, height: 7.5 });
pres.layout = "WIDE";

// Colors
const COLORS = {
  primary: "1E3A5F",
  secondary: "2E86AB",
  accent: "F18F01",
  accent2: "C73E1D",
  light: "F0F4F8",
  white: "FFFFFF",
  dark: "1A1A2E",
  gray: "6B7280",
  success: "10B981",
  purple: "6366F1",
  gradient1: "0F172A",
  gradient2: "1E3A5F",
};

// Helper: add slide with gradient-like background
function addSlideWithTitle(title, subtitle) {
  const slide = pres.addSlide();
  slide.background = { color: COLORS.light };
  // Top bar
  slide.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.2, fill: { color: COLORS.primary } });
  slide.addText(title, {
    x: 0.5, y: 0.15, w: 12, h: 0.9,
    fontSize: 28, fontColor: COLORS.white, bold: true, align: "left",
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 1.4, w: 12, h: 0.5,
      fontSize: 14, fontColor: COLORS.gray, italic: true,
    });
  }
  return slide;
}

function addBulletPoints(slide, bullets, startY = 2.0) {
  let y = startY;
  bullets.forEach((item) => {
    const isMain = typeof item === "string";
    const text = isMain ? item : item.text;
    const opts = isMain ? {} : item;
    slide.addText(text, {
      x: 1.0, y: y, w: 11.3, h: opts.h || 0.45,
      fontSize: opts.fontSize || 15,
      fontColor: opts.fontColor || COLORS.dark,
      bold: opts.bold || false,
      bullet: opts.bullet !== false && !opts.noBullet,
      indentLevel: opts.indent || 0,
      lineSpacingMultiple: 1.2,
    });
    y += (opts.h || 0.45) + 0.15;
  });
}

function addIconBox(slide, x, y, w, h, icon, title, desc, bgColor) {
  slide.addShape("roundRect", {
    x, y, w, h, fill: { color: bgColor || COLORS.white },
    rectRadius: 0.1, shadow: { type: "outer", blur: 6, offset: 2, color: "00000033" },
  });
  slide.addText(icon, {
    x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.6,
    fontSize: 24, align: "center",
  });
  slide.addText(title, {
    x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 0.35,
    fontSize: 13, bold: true, fontColor: COLORS.primary, align: "center",
  });
  slide.addText(desc, {
    x: x + 0.15, y: y + 1.05, w: w - 0.3, h: h - 1.15,
    fontSize: 10, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.2,
  });
}

// ============================================
// SLIDE 1: Cover
// ============================================
{
  const slide = pres.addSlide();
  slide.background = { fill: { type: "solid", color: COLORS.gradient1 } };

  // Decorative shapes
  slide.addShape("rect", { x: 0, y: 0, w: 13.33, h: 0.08, fill: { color: COLORS.accent } });
  slide.addShape("rect", { x: 0, y: 7.42, w: 13.33, h: 0.08, fill: { color: COLORS.accent } });
  slide.addShape("rect", { x: 0, y: 5.8, w: 13.33, h: 0.03, fill: { color: COLORS.secondary + "40" } });

  // Title area
  slide.addText("🦞", {
    x: 0, y: 1.0, w: 13.33, h: 1.2,
    fontSize: 56, align: "center",
  });
  slide.addText("小龙虾生态网络", {
    x: 1, y: 2.0, w: 11.33, h: 1.2,
    fontSize: 44, fontColor: COLORS.white, bold: true, align: "center",
  });
  slide.addText("多智能体协作生态 · 从校园到未来", {
    x: 1, y: 3.2, w: 11.33, h: 0.7,
    fontSize: 22, fontColor: COLORS.secondary, align: "center",
  });
  slide.addText("SDP理论 × RAD范式 × MCP协议 × A2A协议 深度融合", {
    x: 1, y: 3.9, w: 11.33, h: 0.5,
    fontSize: 14, fontColor: COLORS.gray, align: "center",
  });
  slide.addText("诸葛斌教授团队 | 浙江工商大学 人工智能学院 | 2026年6月", {
    x: 1, y: 6.2, w: 11.33, h: 0.5,
    fontSize: 13, fontColor: COLORS.gray, align: "center",
  });
  slide.addText("基于首届AI黑客松大赛成果 · 已落地1268条真实业务数据", {
    x: 1, y: 6.6, w: 11.33, h: 0.5,
    fontSize: 12, fontColor: COLORS.accent, align: "center",
  });
}

// ============================================
// SLIDE 2: 什么是小龙虾生态？
// ============================================
{
  const slide = addSlideWithTitle("🦞 什么是小龙虾生态网络？", "用大白话解释复杂概念");

  slide.addText("想象一下：每只"小龙虾"都是一个AI智能助手，各有专长。", {
    x: 1.0, y: 1.5, w: 11.3, h: 0.5,
    fontSize: 16, fontColor: COLORS.dark, bold: true, italic: true,
  });

  addBulletPoints(slide, [
    { text: "🏠 房间虾 — 帮你预约会议室，说句话就行", h: 0.4, fontSize: 15 },
    { text: "📋 筛选虾 — 智能筛选简历，减少人工核对", h: 0.4, fontSize: 15 },
    { text: "🏆 奖学金虾 — 自动评定奖学金，公平高效", h: 0.4, fontSize: 15 },
    { text: "📊 数据虾 — 调研分析，生成报告", h: 0.4, fontSize: 15 },
    { text: "📝 文档虾 — 一键生成Word/PPT文档", h: 0.4, fontSize: 15 },
    { text: "", h: 0.3 },
    { text: "它们通过统一的协议互相协作，像一支训练有素的团队。", bold: true, h: 0.4, fontSize: 15 },
    { text: "Router（路由虾）是总指挥，接收任务、分解任务、分发给合适的虾执行。", h: 0.4, fontSize: 14, fontColor: COLORS.gray },
  ]);

  // Info box
  slide.addShape("roundRect", {
    x: 1.0, y: 5.0, w: 11.3, h: 1.8, fill: { color: COLORS.secondary + "15" },
    rectRadius: 0.15,
  });
  slide.addText("💡 核心理念", {
    x: 1.2, y: 5.1, w: 3, h: 0.4,
    fontSize: 16, bold: true, fontColor: COLORS.primary,
  });
  slide.addText("一个人拥有多个专业化Agent，就像拥有一家公司。每只虾各司其职，协同完成复杂任务。\n这不是科幻——我们已经有了1268条真实业务数据验证。", {
    x: 1.2, y: 5.5, w: 10.9, h: 1.2,
    fontSize: 13, fontColor: COLORS.dark, lineSpacingMultiple: 1.4,
  });
}

// ============================================
// SLIDE 3: 四大技术支柱
// ============================================
{
  const slide = addSlideWithTitle("🏛️ 四大技术支柱", "SDP × RAD × MCP × A2A 深度融合");

  const boxes = [
    { icon: "💰", title: "SDP理论", desc: "软件定义价格\n动态定价驱动资源优化\n2016年提出，Agent时代焕发新生", color: COLORS.accent + "20", accent: COLORS.accent },
    { icon: "🔄", title: "RAD范式", desc: "递归自主式分解\n任务拆解→智能匹配→协调执行\n让复杂任务变简单", color: COLORS.success + "20", accent: COLORS.success },
    { icon: "🔧", title: "MCP协议", desc: "Model Context Protocol\nAgent的「工具箱」\n标准化调用各种工具", color: COLORS.secondary + "20", accent: COLORS.secondary },
    { icon: "🤝", title: "A2A协议", desc: "Agent-to-Agent Protocol\nAgent的「社交网络」\n对等协作、发现与通信", color: COLORS.purple + "20", accent: COLORS.purple },
  ];

  boxes.forEach((b, i) => {
    const x = 0.7 + i * 3.15;
    addIconBox(slide, x, 1.8, 2.9, 3.8, b.icon, b.title, b.desc, b.color);
    // Accent line on top
    slide.addShape("rect", { x: x, y: 1.8, w: 2.9, h: 0.06, fill: { color: b.accent } });
  });

  // Bottom formula
  slide.addShape("roundRect", {
    x: 1.5, y: 5.9, w: 10.3, h: 1.0, fill: { color: COLORS.primary },
    rectRadius: 0.1,
  });
  slide.addText("SDP（理论根基）+ RAD（协作方法）+ MCP（工具调用）+ A2A（Agent协作）= 完整的小龙虾生态技术栈", {
    x: 1.7, y: 6.0, w: 9.9, h: 0.8,
    fontSize: 14, fontColor: COLORS.white, bold: true, align: "center", lineSpacingMultiple: 1.3,
  });
}

// ============================================
// SLIDE 4: MCP vs A2A
// ============================================
{
  const slide = addSlideWithTitle("🔌 MCP vs A2A — 两大协议如何分工？", "各管一摊，互补共生");

  // MCP box
  slide.addShape("roundRect", {
    x: 0.8, y: 1.8, w: 5.5, h: 4.5, fill: { color: COLORS.secondary + "12" },
    rectRadius: 0.15,
  });
  slide.addShape("rect", { x: 0.8, y: 1.8, w: 5.5, h: 0.6, fill: { color: COLORS.secondary } });
  slide.addText("🔧 MCP — Agent的工具箱", {
    x: 0.8, y: 1.85, w: 5.5, h: 0.5,
    fontSize: 18, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "纵向连接：大脑 → 手脚", bold: true, fontSize: 14, h: 0.4 },
    { text: "Agent通过MCP调用各种工具", fontSize: 13, h: 0.35 },
    { text: "就像人用工具完成具体任务", fontSize: 13, h: 0.35 },
    { text: "", h: 0.25 },
    { text: "典型场景：", bold: true, fontSize: 13, h: 0.35 },
    { text: "  → 文档虾调用Word生成工具", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  → 数据虾调用数据分析工具", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  → 查询虾调用数据库查询工具", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.6);

  // A2A box
  slide.addShape("roundRect", {
    x: 7.0, y: 1.8, w: 5.5, h: 4.5, fill: { color: COLORS.purple + "12" },
    rectRadius: 0.15,
  });
  slide.addShape("rect", { x: 7.0, y: 1.8, w: 5.5, h: 0.6, fill: { color: COLORS.purple } });
  slide.addText("🤝 A2A — Agent的社交网络", {
    x: 7.0, y: 1.85, w: 5.5, h: 0.5,
    fontSize: 18, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "横向连接：对等方 → 对等方", bold: true, fontSize: 14, h: 0.4 },
    { text: "Agent之间发现彼此、协作完成任务", fontSize: 13, h: 0.35 },
    { text: "就像同事之间的协作沟通", fontSize: 13, h: 0.35 },
    { text: "", h: 0.25 },
    { text: "典型场景：", bold: true, fontSize: 13, h: 0.35 },
    { text: "  → Router发现文档虾并派任务", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  → 多只虾组队完成复杂项目", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  → 虾在外部市场接单交付", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.6);

  // Arrow between
  slide.addText("⟷ 互补协作", {
    x: 6.35, y: 3.6, w: 0.8, h: 0.5,
    fontSize: 12, bold: true, fontColor: COLORS.accent, align: "center",
  });
}

// ============================================
// SLIDE 5: 三期演进总览
// ============================================
{
  const slide = addSlideWithTitle("📈 三期演进路线图", "稳扎稳打，从验证到全覆盖");

  // Phase 1
  slide.addShape("roundRect", {
    x: 0.5, y: 1.8, w: 3.8, h: 4.8, fill: { color: COLORS.success + "15" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 0.5, y: 1.8, w: 3.8, h: 0.55, fill: { color: COLORS.success } });
  slide.addText("✅ 一期验证（已完成）", {
    x: 0.5, y: 1.82, w: 3.8, h: 0.5,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "会议室预约小龙虾", bold: true, fontSize: 14, h: 0.4 },
    { text: "「芯朋友」AI助手", fontSize: 13, h: 0.3 },
    { text: "管理6个会议室", fontSize: 13, h: 0.3 },
    { text: "1268条真实预约记录", bold: true, fontSize: 13, fontColor: COLORS.success, h: 0.3 },
    { text: "日均1.4次、月均42次", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "验证：钉钉集成、AI语义理解", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.5);

  // Arrow
  slide.addText("→", { x: 4.3, y: 3.8, w: 0.5, h: 0.5, fontSize: 28, fontColor: COLORS.accent, bold: true, align: "center" });

  // Phase 2
  slide.addShape("roundRect", {
    x: 4.8, y: 1.8, w: 3.8, h: 4.8, fill: { color: COLORS.accent + "15" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 4.8, y: 1.8, w: 3.8, h: 0.55, fill: { color: COLORS.accent } });
  slide.addText("🚀 二期扩展（进行中）", {
    x: 4.8, y: 1.82, w: 3.8, h: 0.5,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "18个黑客松作品 → 19只业务虾", bold: true, fontSize: 14, h: 0.4 },
    { text: "五大族群：", fontSize: 13, h: 0.3 },
    { text: "  院务虾、学务虾、评奖虾", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  空间虾、科研虾", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "同题竞争 → 市场定价验证", fontSize: 13, h: 0.3 },
    { text: "MCP封装 → Agent Card发布", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.5);

  // Arrow
  slide.addText("→", { x: 8.6, y: 3.8, w: 0.5, h: 0.5, fontSize: 28, fontColor: COLORS.accent2, bold: true, align: "center" });

  // Phase 3
  slide.addShape("roundRect", {
    x: 9.1, y: 1.8, w: 3.7, h: 4.8, fill: { color: COLORS.accent2 + "15" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 9.1, y: 1.8, w: 3.7, h: 0.55, fill: { color: COLORS.accent2 } });
  slide.addText("🌟 三期全覆盖（规划中）", {
    x: 9.1, y: 1.82, w: 3.7, h: 0.5,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "全面铺开学院业务", bold: true, fontSize: 14, h: 0.4 },
    { text: "对接外部劳务市场", fontSize: 13, h: 0.3 },
    { text: "ClawBNB平台挂牌", fontSize: 13, h: 0.3 },
    { text: "10+小龙虾生态协作", fontSize: 13, h: 0.3 },
    { text: "面向义乌小商品产业", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "AI Agent柔性定制", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.5);
}

// ============================================
// SLIDE 6: 一期成果 — 房间虾
// ============================================
{
  const slide = addSlideWithTitle("🏠 一期成果：「芯朋友」预约小龙虾", "已上线，真实运营数据说话");

  // Stats row
  const stats = [
    { num: "1268", label: "累计预约记录", color: COLORS.success },
    { num: "42", label: "月均预约次数", color: COLORS.secondary },
    { num: "6", label: "管理会议室数", color: COLORS.accent },
    { num: "V2.0", label: "当前版本", color: COLORS.purple },
  ];
  stats.forEach((s, i) => {
    const x = 0.7 + i * 3.15;
    slide.addShape("roundRect", {
      x, y: 1.8, w: 2.9, h: 1.3, fill: { color: s.color + "15" },
      rectRadius: 0.1,
    });
    slide.addText(s.num, {
      x, y: 1.85, w: 2.9, h: 0.7,
      fontSize: 32, bold: true, fontColor: s.color, align: "center",
    });
    slide.addText(s.label, {
      x, y: 2.55, w: 2.9, h: 0.4,
      fontSize: 12, fontColor: COLORS.gray, align: "center",
    });
  });

  // Features
  slide.addText("🎯 核心能力", {
    x: 1.0, y: 3.4, w: 5, h: 0.4,
    fontSize: 16, bold: true, fontColor: COLORS.primary,
  });
  addBulletPoints(slide, [
    { text: "AI语义理解：说\"明天下午约330\"自动解析", h: 0.35 },
    { text: "冲突检测：时间冲突时主动推荐可用房间", h: 0.35 },
    { text: "热力图：绿(空闲)/粉(占用)/蓝(选中)一目了然", h: 0.35 },
    { text: "双入口：AI对话 + Web界面，数据互通", h: 0.35 },
    { text: "钉钉免登：组织架构鉴权，隐私保护", h: 0.35 },
  ], 3.8);

  // Validation box
  slide.addShape("roundRect", {
    x: 7.0, y: 3.4, w: 5.5, h: 3.5, fill: { color: COLORS.primary + "10" },
    rectRadius: 0.1,
  });
  slide.addText("📌 一期验证了什么？", {
    x: 7.2, y: 3.5, w: 5, h: 0.4,
    fontSize: 15, bold: true, fontColor: COLORS.primary,
  });
  addBulletPoints(slide, [
    { text: "✅ 钉钉生态集成可行性", fontSize: 13, h: 0.35 },
    { text: "    无需额外注册或下载APP", fontSize: 11, fontColor: COLORS.gray, h: 0.3 },
    { text: "✅ AI Agent替代人工操作", fontSize: 13, h: 0.35 },
    { text: "    不只是问答机器人，能真正执行任务", fontSize: 11, fontColor: COLORS.gray, h: 0.3 },
    { text: "✅ 双入口架构", fontSize: 13, h: 0.35 },
    { text: "    为后续多模态交互提供参考范式", fontSize: 11, fontColor: COLORS.gray, h: 0.3 },
    { text: "✅ Agent Card能力画像基准", fontSize: 13, h: 0.35 },
    { text: "    为后续虾的定价提供真实数据", fontSize: 11, fontColor: COLORS.gray, h: 0.3 },
  ], 3.95);
}

// ============================================
// SLIDE 7: 二期 — 18只业务虾
// ============================================
{
  const slide = addSlideWithTitle("🎓 二期扩展：18个黑客松作品 → 19只业务虾", "首届AI黑客松成果，全部来自本科生");

  slide.addText("五大业务虾族群", {
    x: 1.0, y: 1.6, w: 5, h: 0.4,
    fontSize: 16, bold: true, fontColor: COLORS.primary,
  });

  const groups = [
    { name: "院务虾", icon: "📋", count: "3只", desc: "通知、筛选、办公", color: COLORS.secondary },
    { name: "学务虾", icon: "📚", count: "5只", desc: "答疑、排课、选课", color: COLORS.success },
    { name: "评奖虾", icon: "🏆", count: "3只", desc: "奖学金评定", color: COLORS.accent },
    { name: "空间虾", icon: "🏠", count: "4只", desc: "会议室、座位、实验室", color: COLORS.purple },
    { name: "科研虾", icon: "🔬", count: "4只", desc: "论文管理、实验", color: COLORS.accent2 },
  ];

  groups.forEach((g, i) => {
    const x = 0.6 + i * 2.55;
    slide.addShape("roundRect", {
      x, y: 2.1, w: 2.35, h: 2.2, fill: { color: g.color + "15" },
      rectRadius: 0.1,
    });
    slide.addText(g.icon, {
      x, y: 2.2, w: 2.35, h: 0.6,
      fontSize: 28, align: "center",
    });
    slide.addText(g.name, {
      x, y: 2.8, w: 2.35, h: 0.35,
      fontSize: 16, bold: true, fontColor: g.color, align: "center",
    });
    slide.addText(g.count, {
      x, y: 3.15, w: 2.35, h: 0.3,
      fontSize: 13, fontColor: COLORS.gray, align: "center",
    });
    slide.addText(g.desc, {
      x, y: 3.5, w: 2.35, h: 0.6,
      fontSize: 11, fontColor: COLORS.dark, align: "center", lineSpacingMultiple: 1.2,
    });
  });

  // Competition highlight
  slide.addShape("roundRect", {
    x: 1.0, y: 4.6, w: 11.3, h: 2.2, fill: { color: COLORS.accent + "10" },
    rectRadius: 0.1,
  });
  slide.addText("⚔️ 同题竞争 — 天然的市场定价实验", {
    x: 1.2, y: 4.7, w: 10, h: 0.4,
    fontSize: 15, bold: true, fontColor: COLORS.accent,
  });
  addBulletPoints(slide, [
    { text: "奖学金评选：3个独立版本（不同C/S/Q画像 → 差异化竞争）", fontSize: 13, h: 0.35 },
    { text: "座位预约：3个独立版本（验证Agent Card能力画像机制）", fontSize: 13, h: 0.35 },
    { text: "实验室管理：2个版本 | 科研论文管理：2个版本 | 事务通知：2个版本", fontSize: 13, h: 0.35 },
    { text: "这正是SDP动态定价理论的天然实验场 —— 市场会选出最优方案！", bold: true, fontSize: 13, fontColor: COLORS.accent2, h: 0.4 },
  ], 5.1);
}

// ============================================
// SLIDE 8: 三只明星虾
// ============================================
{
  const slide = addSlideWithTitle("⭐ 三只"明星虾"展示", "从黑客松作品到业务虾的蜕变");

  // Star 1: Room Agent
  slide.addShape("roundRect", {
    x: 0.5, y: 1.8, w: 4.0, h: 4.8, fill: { color: COLORS.success + "10" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 0.5, y: 1.8, w: 4.0, h: 0.5, fill: { color: COLORS.success } });
  slide.addText("🏠 房间虾（已上线）", {
    x: 0.5, y: 1.82, w: 4.0, h: 0.45,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "开发者：胡庆凯（信电学院）", fontSize: 12, h: 0.3 },
    { text: "AI助手名：芯朋友", fontSize: 12, h: 0.3 },
    { text: "上线时间：2023年12月", fontSize: 12, h: 0.3 },
    { text: "累计预约：1268条", bold: true, fontSize: 13, fontColor: COLORS.success, h: 0.3 },
    { text: "", h: 0.15 },
    { text: "技能：", bold: true, fontSize: 13, h: 0.3 },
    { text: "  • AI语义预约", fontSize: 12, h: 0.25 },
    { text: "  • 房间查询", fontSize: 12, h: 0.25 },
    { text: "  • 取消/改约", fontSize: 12, h: 0.25 },
    { text: "  • 可视化热力图", fontSize: 12, h: 0.25 },
  ], 2.4);

  // Star 2: Scholarship Agent C
  slide.addShape("roundRect", {
    x: 4.7, y: 1.8, w: 4.0, h: 4.8, fill: { color: COLORS.accent + "10" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 4.7, y: 1.8, w: 4.0, h: 0.5, fill: { color: COLORS.accent } });
  slide.addText("🏆 奖学金虾C（MCP原生）", {
    x: 4.7, y: 1.82, w: 4.0, h: 0.45,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "开发者：徐杰、孙豪", fontSize: 12, h: 0.3 },
    { text: "技术：Flask + MCP Server", fontSize: 12, h: 0.3 },
    { text: "🌟 最接近业务虾形态的作品！", bold: true, fontSize: 12, fontColor: COLORS.accent2, h: 0.3 },
    { text: "", h: 0.15 },
    { text: "技能：", bold: true, fontSize: 13, h: 0.3 },
    { text: "  • 公平排名与公示", fontSize: 12, h: 0.25 },
    { text: "  • 学生提交加分材料", fontSize: 12, h: 0.25 },
    { text: "  • 辅导员AI辅助审核", fontSize: 12, h: 0.25 },
    { text: "  • 发布评定结果", fontSize: 12, h: 0.25 },
    { text: "", h: 0.15 },
    { text: "已集成钉钉机器人 ✅", fontSize: 12, fontColor: COLORS.success, h: 0.3 },
  ], 2.4);

  // Star 3: Screen Agent
  slide.addShape("roundRect", {
    x: 8.9, y: 1.8, w: 4.0, h: 4.8, fill: { color: COLORS.purple + "10" },
    rectRadius: 0.1,
  });
  slide.addShape("rect", { x: 8.9, y: 1.8, w: 4.0, h: 0.5, fill: { color: COLORS.purple } });
  slide.addText("📋 筛选虾（简历筛选）", {
    x: 8.9, y: 1.82, w: 4.0, h: 0.45,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "开发者：李清扬（信电学院AI专业）", fontSize: 12, h: 0.3 },
    { text: "", h: 0.15 },
    { text: "技能：", bold: true, fontSize: 13, h: 0.3 },
    { text: "  • 简历智能筛选", fontSize: 12, h: 0.25 },
    { text: "  • AI辅助人才审核", fontSize: 12, h: 0.25 },
    { text: "  • 减少人工核对", fontSize: 12, h: 0.25 },
    { text: "", h: 0.15 },
    { text: "经济属性：", bold: true, fontSize: 13, h: 0.3 },
    { text: "  基础价格：0.10元/次", fontSize: 12, h: 0.25 },
    { text: "  批量折扣：10+次享85折", fontSize: 12, h: 0.25 },
    { text: "  50+次享75折", fontSize: 12, h: 0.25 },
  ], 2.4);
}

// ============================================
// SLIDE 9: Agent Card 是什么？
// ============================================
{
  const slide = addSlideWithTitle("📇 Agent Card — 每只虾的"身份证"", "标准化描述Agent的能力与价值");

  slide.addText("Agent Card = Agent的身份名片，让别人知道你能做什么、做得怎么样、收多少钱", {
    x: 1.0, y: 1.5, w: 11.3, h: 0.5,
    fontSize: 14, fontColor: COLORS.gray, italic: true,
  });

  // Three sections of Agent Card
  const sections = [
    {
      title: "🆔 基本信息",
      color: COLORS.secondary,
      items: ["名称、ID、版本号", "能力描述", "访问地址(URL)", "开发者信息（可溯源到黑客松作品）"],
    },
    {
      title: "📊 能力画像（C/S/Q）",
      color: COLORS.success,
      items: ["Cost（成本）：平均每次多少钱", "Speed（速度）：平均响应时间", "Quality（质量）：任务完成质量评分", "类似外卖骑手的评分系统"],
    },
    {
      title: "💰 经济属性",
      color: COLORS.accent,
      items: ["基础价格、当前动态价格", "批量折扣策略", "高峰时段溢价", "历史订单数、评分、完成率"],
    },
  ];

  sections.forEach((s, i) => {
    const x = 0.7 + i * 4.15;
    slide.addShape("roundRect", {
      x, y: 2.2, w: 3.9, h: 4.5, fill: { color: s.color + "12" },
      rectRadius: 0.1,
    });
    slide.addShape("rect", { x, y: 2.2, w: 3.9, h: 0.5, fill: { color: s.color } });
    slide.addText(s.title, {
      x, y: 2.22, w: 3.9, h: 0.45,
      fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
    });
    addBulletPoints(slide, s.items.map(item => ({
      text: item, fontSize: 12, h: 0.35,
    })), 2.9);
  });
}

// ============================================
// SLIDE 10: 经济模型 — Agent劳务市场
// ============================================
{
  const slide = addSlideWithTitle("💰 Agent劳务市场与经济模型", "让小龙虾不只是"免费打工"，而是能"赚钱"的数字员工");

  // Three trade modes
  const modes = [
    {
      icon: "⚡", title: "即时交易",
      desc: "发布任务 → 即时接单 → 执行交付",
      example: "例："帮我生成一份Word报告"\n→ 文档虾接单 → 30秒完成 → 收费0.05元",
      analogy: "类似淘宝"一口价"",
      color: COLORS.success,
    },
    {
      icon: "🎯", title: "悬赏竞标",
      desc: "发布悬赏 → 多虾竞标 → 择优录取",
      example: "例："市场调研报告，预算50元"\n→ 数据虾A报20元 vs 虾B报35元 → 选B",
      analogy: "类似猪八戒网"悬赏模式"",
      color: COLORS.accent,
    },
    {
      icon: "📅", title: "长期合约",
      desc: "签订长期服务协议，按月结算",
      example: "例："每天9点生成销售日报"\n→ 多虾组成固定Pipeline → 月费30元",
      analogy: "类似SaaS"订阅模式"",
      color: COLORS.purple,
    },
  ];

  modes.forEach((m, i) => {
    const x = 0.5 + i * 4.25;
    slide.addShape("roundRect", {
      x, y: 1.8, w: 4.0, h: 4.5, fill: { color: m.color + "10" },
      rectRadius: 0.1,
    });
    slide.addShape("rect", { x, y: 1.8, w: 4.0, h: 0.55, fill: { color: m.color } });
    slide.addText(`${m.icon} ${m.title}`, {
      x, y: 1.82, w: 4.0, h: 0.5,
      fontSize: 16, fontColor: COLORS.white, bold: true, align: "center",
    });
    slide.addText(m.desc, {
      x: x + 0.2, y: 2.5, w: 3.6, h: 0.5,
      fontSize: 12, fontColor: COLORS.dark, align: "center", bold: true,
    });
    slide.addText(m.example, {
      x: x + 0.2, y: 3.1, w: 3.6, h: 1.8,
      fontSize: 11, fontColor: COLORS.gray, lineSpacingMultiple: 1.3,
    });
    slide.addShape("roundRect", {
      x: x + 0.3, y: 5.2, w: 3.4, h: 0.5, fill: { color: m.color + "20" },
      rectRadius: 0.08,
    });
    slide.addText(m.analogy, {
      x: x + 0.3, y: 5.22, w: 3.4, h: 0.45,
      fontSize: 11, fontColor: m.color, bold: true, align: "center",
    });
  });

  // Revenue sharing
  slide.addShape("roundRect", {
    x: 1.0, y: 6.5, w: 11.3, h: 0.7, fill: { color: COLORS.primary },
    rectRadius: 0.1,
  });
  slide.addText("收益分配：平台抽成10% + 算力成本30% + 利润60%（虾主人/学院）", {
    x: 1.2, y: 6.55, w: 10.9, h: 0.6,
    fontSize: 14, fontColor: COLORS.white, bold: true, align: "center",
  });
}

// ============================================
// SLIDE 11: 技能定价公式
// ============================================
{
  const slide = addSlideWithTitle("📐 Skill定价公式 — SDP理论的Agent时代表达", "从"网络资源定价"到"Agent Skill定价"");

  // Formula box
  slide.addShape("roundRect", {
    x: 2.0, y: 1.8, w: 9.3, h: 1.5, fill: { color: COLORS.primary },
    rectRadius: 0.1,
  });
  slide.addText("P(skill) = P_base × D_factor × Q_premium × U_discount", {
    x: 2.0, y: 1.9, w: 9.3, h: 0.7,
    fontSize: 22, fontColor: COLORS.white, bold: true, align: "center",
  });
  slide.addText("Skill价格 = 基础价 × 动态因子 × 质量溢价 × 批量折扣", {
    x: 2.0, y: 2.6, w: 9.3, h: 0.5,
    fontSize: 13, fontColor: COLORS.secondary, align: "center",
  });

  // Four factors
  const factors = [
    { name: "P_base", desc: "基础价格", detail: "根据任务复杂度和算力成本设定初始价格", icon: "💵", color: COLORS.success },
    { name: "D_factor", desc: "动态因子", detail: "供需关系实时调节：供不应求时涨价，闲置时降价", icon: "📊", color: COLORS.secondary },
    { name: "Q_premium", desc: "质量溢价", detail: "高质量虾获得溢价奖励，激励提升服务质量", icon: "⭐", color: COLORS.accent },
    { name: "U_discount", desc: "批量折扣", detail: "大订单享受折扣，鼓励长期合作", icon: "🏷️", color: COLORS.purple },
  ];

  factors.forEach((f, i) => {
    const x = 0.6 + i * 3.15;
    slide.addShape("roundRect", {
      x, y: 3.6, w: 2.95, h: 3.2, fill: { color: f.color + "12" },
      rectRadius: 0.1,
    });
    slide.addText(f.icon, {
      x, y: 3.7, w: 2.95, h: 0.5,
      fontSize: 24, align: "center",
    });
    slide.addText(f.name, {
      x, y: 4.2, w: 2.95, h: 0.35,
      fontSize: 16, bold: true, fontColor: f.color, align: "center",
    });
    slide.addText(f.desc, {
      x, y: 4.55, w: 2.95, h: 0.3,
      fontSize: 13, bold: true, fontColor: COLORS.dark, align: "center",
    });
    slide.addText(f.detail, {
      x: x + 0.15, y: 4.9, w: 2.65, h: 1.7,
      fontSize: 11, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.3,
    });
  });
}

// ============================================
// SLIDE 12: 双循环生态
// ============================================
{
  const slide = addSlideWithTitle("🔄 双循环生态 — 校内 + 外部市场", "内循环服务师生，外循环创造价值");

  // Inner circle
  slide.addShape("roundRect", {
    x: 0.5, y: 1.8, w: 6.0, h: 4.8, fill: { color: COLORS.secondary + "12" },
    rectRadius: 0.15,
  });
  slide.addShape("rect", { x: 0.5, y: 1.8, w: 6.0, h: 0.55, fill: { color: COLORS.secondary } });
  slide.addText("🏫 内循环（校内生态）", {
    x: 0.5, y: 1.82, w: 6.0, h: 0.5,
    fontSize: 18, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "10+只小龙虾在内部协作", bold: true, fontSize: 14, h: 0.4 },
    { text: "通过MCP+A2A完成教学科研任务", fontSize: 13, h: 0.35 },
    { text: "Router作为生态协调器，内部匹配和调度", fontSize: 13, h: 0.35 },
    { text: "", h: 0.2 },
    { text: "服务对象：", bold: true, fontSize: 13, h: 0.35 },
    { text: "  • 老师：会议室预约、文档生成、数据分析", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  • 学生：选课答疑、奖学金评定、论文管理", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  • 辅导员：学生事务通知、材料审核", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.5);

  // Outer circle
  slide.addShape("roundRect", {
    x: 6.8, y: 1.8, w: 6.0, h: 4.8, fill: { color: COLORS.accent + "12" },
    rectRadius: 0.15,
  });
  slide.addShape("rect", { x: 6.8, y: 1.8, w: 6.0, h: 0.55, fill: { color: COLORS.accent } });
  slide.addText("🌍 外循环（外部市场）", {
    x: 6.8, y: 1.82, w: 6.0, h: 0.5,
    fontSize: 18, fontColor: COLORS.white, bold: true, align: "center",
  });
  addBulletPoints(slide, [
    { text: "通过A2A对接ClawBNB平台", bold: true, fontSize: 14, h: 0.4 },
    { text: "学院小龙虾"挂牌上市"，接受外部委托", fontSize: 13, h: 0.35 },
    { text: "Router充当"经纪人"角色", fontSize: 13, h: 0.35 },
    { text: "", h: 0.2 },
    { text: "市场定位：", bold: true, fontSize: 13, h: 0.35 },
    { text: "  • 教育行业Agent解决方案", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  • 面向义乌小商品产业的柔性定制", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
    { text: "  • AI Agent劳务市场专业服务", fontSize: 12, fontColor: COLORS.gray, h: 0.3 },
  ], 2.5);

  // Bridge
  slide.addText("⟷", {
    x: 6.35, y: 3.8, w: 0.6, h: 0.5,
    fontSize: 24, fontColor: COLORS.accent2, bold: true, align: "center",
  });
  slide.addText("A2A\n桥接", {
    x: 6.15, y: 4.3, w: 0.8, h: 0.6,
    fontSize: 10, fontColor: COLORS.accent2, bold: true, align: "center",
  });
}

// ============================================
// SLIDE 13: Router — 生态协调器
// ============================================
{
  const slide = addSlideWithTitle("🎯 Router — 生态协调器", "从"消息路由器"升级为"生态大脑"");

  slide.addText("Router不再只是转发消息，而是生态的智能中枢，拥有三重身份：", {
    x: 1.0, y: 1.5, w: 11.3, h: 0.5,
    fontSize: 14, fontColor: COLORS.gray, italic: true,
  });

  const roles = [
    {
      icon: "🧑‍💼", title: "A2A Agent",
      desc: "发布自己的Agent Card，作为生态的统一入口",
      detail: "接受来自个人小龙虾和外部Agent的Task请求，是整个生态的"前台接待"",
      color: COLORS.secondary,
    },
    {
      icon: "📤", title: "A2A Client",
      desc: "将分解后的子任务发送给业务虾",
      detail: "监听Task状态变化，驱动DAG有向无环图执行，是任务的"调度中心"",
      color: COLORS.accent,
    },
    {
      icon: "🔧", title: "MCP Client",
      desc: "直接调用业务虾的工具（简单查询）",
      detail: "需要快速获取信息时，作为MCP Client调用虾的工具，是"快捷通道"",
      color: COLORS.purple,
    },
  ];

  roles.forEach((r, i) => {
    const x = 0.6 + i * 4.15;
    slide.addShape("roundRect", {
      x, y: 2.2, w: 3.9, h: 3.5, fill: { color: r.color + "12" },
      rectRadius: 0.1,
    });
    slide.addText(r.icon, {
      x, y: 2.3, w: 3.9, h: 0.6,
      fontSize: 30, align: "center",
    });
    slide.addText(r.title, {
      x, y: 2.9, w: 3.9, h: 0.4,
      fontSize: 18, bold: true, fontColor: r.color, align: "center",
    });
    slide.addText(r.desc, {
      x: x + 0.2, y: 3.35, w: 3.5, h: 0.5,
      fontSize: 12, fontColor: COLORS.dark, align: "center", bold: true,
    });
    slide.addText(r.detail, {
      x: x + 0.2, y: 3.9, w: 3.5, h: 1.6,
      fontSize: 11, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.3,
    });
  });

  // RAD process
  slide.addShape("roundRect", {
    x: 1.0, y: 5.9, w: 11.3, h: 1.2, fill: { color: COLORS.primary },
    rectRadius: 0.1,
  });
  slide.addText("RAD协作流程：接收任务 → 递归分解为"元业务" → 三维匹配最佳执行虾 → 协调编排执行 → 交付结果", {
    x: 1.2, y: 5.95, w: 10.9, h: 1.1,
    fontSize: 14, fontColor: COLORS.white, bold: true, align: "center", lineSpacingMultiple: 1.3,
  });
}

// ============================================
// SLIDE 14: 转化路径
// ============================================
{
  const slide = addSlideWithTitle("🛤️ 黑客松作品 → 业务虾 三步转化法", "每个作品只需三步，就能变成一只真正的业务虾");

  const steps = [
    {
      step: "Step 1", title: "MCP Tool封装",
      icon: "📦", color: COLORS.secondary,
      desc: "将作品核心功能封装为标准MCP Tool接口",
      example: "例：screen_resume(input, criteria) → result\n每个作品提取1-4个核心Skill\n作品#15已自带MCP Server，可直接接入",
    },
    {
      step: "Step 2", title: "Agent Card发布",
      icon: "📇", color: COLORS.accent,
      desc: "生成标准Agent Card，含能力画像和定价",
      example: "部署到 /.well-known/agent.json 端点\n或向Router注册（轻量接入）\nsource字段关联原始黑客松作品，保持可溯源",
    },
    {
      step: "Step 3", title: "市场挂牌",
      icon: "🏪", color: COLORS.success,
      desc: "将Agent Card同步到ClawBNB平台",
      example: "设置初始定价和促销策略（如首月半价）\n开始接受外部订单\n赚钱啦！💰",
    },
  ];

  steps.forEach((s, i) => {
    const x = 0.5 + i * 4.25;
    slide.addShape("roundRect", {
      x, y: 1.8, w: 4.0, h: 5.0, fill: { color: s.color + "10" },
      rectRadius: 0.1,
    });
    // Step badge
    slide.addShape("roundRect", {
      x: x + 1.2, y: 1.7, w: 1.6, h: 0.5, fill: { color: s.color },
      rectRadius: 0.08,
    });
    slide.addText(s.step, {
      x: x + 1.2, y: 1.72, w: 1.6, h: 0.45,
      fontSize: 14, fontColor: COLORS.white, bold: true, align: "center",
    });
    slide.addText(s.icon, {
      x, y: 2.3, w: 4.0, h: 0.6,
      fontSize: 28, align: "center",
    });
    slide.addText(s.title, {
      x, y: 2.9, w: 4.0, h: 0.4,
      fontSize: 18, bold: true, fontColor: s.color, align: "center",
    });
    slide.addText(s.desc, {
      x: x + 0.2, y: 3.4, w: 3.6, h: 0.5,
      fontSize: 12, fontColor: COLORS.dark, align: "center", bold: true,
    });
    slide.addText(s.example, {
      x: x + 0.2, y: 4.0, w: 3.6, h: 2.5,
      fontSize: 11, fontColor: COLORS.gray, lineSpacingMultiple: 1.3,
    });
  });
}

// ============================================
// SLIDE 15: 经济测算
// ============================================
{
  const slide = addSlideWithTitle("📊 19虾上线后的经济测算", "预估收益与成本分析");

  slide.addText("基于真实运营数据（房间虾月均42次）和同类Agent市场价估算：", {
    x: 1.0, y: 1.5, w: 11.3, h: 0.4,
    fontSize: 13, fontColor: COLORS.gray, italic: true,
  });

  // Projection table
  const projections = [
    { metric: "日均调用次数", value: "200-500次", desc: "19只虾×平均10-25次/天", color: COLORS.secondary },
    { metric: "月均收入", value: "¥1,500-4,000", desc: "按平均¥0.05-0.15/次估算", color: COLORS.success },
    { metric: "算力成本", value: "¥300-800", desc: "服务器、API调用等基础开销", color: COLORS.accent },
    { metric: "月净利润", value: "¥900-2,400", desc: "利润60%归属虾主人/学院", color: COLORS.purple },
  ];

  projections.forEach((p, i) => {
    const y = 2.1 + i * 1.15;
    slide.addShape("roundRect", {
      x: 1.0, y, w: 11.3, h: 1.0, fill: { color: p.color + "10" },
      rectRadius: 0.08,
    });
    slide.addShape("rect", {
      x: 1.0, y, w: 0.08, h: 1.0, fill: { color: p.color },
    });
    slide.addText(p.metric, {
      x: 1.3, y: y + 0.05, w: 3, h: 0.4,
      fontSize: 14, bold: true, fontColor: COLORS.dark,
    });
    slide.addText(p.value, {
      x: 4.3, y: y + 0.05, w: 4, h: 0.4,
      fontSize: 18, bold: true, fontColor: p.color,
    });
    slide.addText(p.desc, {
      x: 8.3, y: y + 0.1, w: 3.8, h: 0.8,
      fontSize: 11, fontColor: COLORS.gray, lineSpacingMultiple: 1.2,
    });
  });

  // Note
  slide.addShape("roundRect", {
    x: 1.0, y: 6.8, w: 11.3, h: 0.5, fill: { color: COLORS.primary + "10" },
    rectRadius: 0.08,
  });
  slide.addText("💡 注：以上为保守估算，实际收益取决于使用频率、定价策略和市场接受度。随着生态成熟，收益有望指数增长。", {
    x: 1.2, y: 6.82, w: 10.9, h: 0.45,
    fontSize: 11, fontColor: COLORS.gray, lineSpacingMultiple: 1.2,
  });
}

// ============================================
// SLIDE 16: 愿景与未来
// ============================================
{
  const slide = addSlideWithTitle("🌟 愿景与未来", "从校园到产业，从小龙虾到大生态");

  // Vision statement
  slide.addShape("roundRect", {
    x: 1.0, y: 1.8, w: 11.3, h: 1.5, fill: { color: COLORS.primary },
    rectRadius: 0.1,
  });
  slide.addText("让每只小龙虾都成为有价值的数字员工\n让每个师生都拥有自己的AI团队\n让Agent协作像同事协作一样自然", {
    x: 1.2, y: 1.9, w: 10.9, h: 1.3,
    fontSize: 16, fontColor: COLORS.white, bold: true, align: "center", lineSpacingMultiple: 1.5,
  });

  // Future items
  const futures = [
    { icon: "🎓", title: "教育行业标杆", desc: "打造高校AI Agent生态标杆，输出标准化方案", color: COLORS.secondary },
    { icon: "🏭", title: "产业赋能", desc: "面向义乌小商品产业，提供AI Agent柔性定制服务", color: COLORS.accent },
    { icon: "🌐", title: "开放生态", desc: "对接ClawBNB等外部平台，融入全球Agent经济网络", color: COLORS.success },
    { icon: "🦞", title: "10+虾生态", desc: "构建10+小龙虾协作生态，多虾协同完成复杂任务", color: COLORS.purple },
  ];

  futures.forEach((f, i) => {
    const x = 0.6 + i * 3.15;
    slide.addShape("roundRect", {
      x, y: 3.6, w: 2.95, h: 2.8, fill: { color: f.color + "12" },
      rectRadius: 0.1,
    });
    slide.addText(f.icon, {
      x, y: 3.7, w: 2.95, h: 0.6,
      fontSize: 28, align: "center",
    });
    slide.addText(f.title, {
      x, y: 4.3, w: 2.95, h: 0.4,
      fontSize: 16, bold: true, fontColor: f.color, align: "center",
    });
    slide.addText(f.desc, {
      x: x + 0.15, y: 4.75, w: 2.65, h: 1.5,
      fontSize: 12, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.3,
    });
  });
}

// ============================================
// SLIDE 17: 团队与致谢
// ============================================
{
  const slide = pres.addSlide();
  slide.background = { fill: { type: "solid", color: COLORS.gradient1 } };

  slide.addShape("rect", { x: 0, y: 0, w: 13.33, h: 0.08, fill: { color: COLORS.accent } });
  slide.addShape("rect", { x: 0, y: 7.42, w: 13.33, h: 0.08, fill: { color: COLORS.accent } });

  slide.addText("🦞", {
    x: 0, y: 1.5, w: 13.33, h: 1.0,
    fontSize: 48, align: "center",
  });
  slide.addText("感谢聆听", {
    x: 1, y: 2.5, w: 11.33, h: 1.0,
    fontSize: 40, fontColor: COLORS.white, bold: true, align: "center",
  });
  slide.addText("小龙虾生态网络 · 多智能体协作生态", {
    x: 1, y: 3.5, w: 11.33, h: 0.5,
    fontSize: 18, fontColor: COLORS.secondary, align: "center",
  });
  slide.addText("方案设计：诸葛斌教授团队\n依托单位：浙江工商大学 人工智能学院\n理论体系：SDP(2016) + RAD(2026)\n协议架构：MCP + A2A 混合架构", {
    x: 1, y: 4.3, w: 11.33, h: 1.8,
    fontSize: 14, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.6,
  });
  slide.addText("2026年6月", {
    x: 1, y: 6.2, w: 11.33, h: 0.4,
    fontSize: 13, fontColor: COLORS.accent, align: "center",
  });
  slide.addText("---\n本文由AI辅助创作 / 虾尔 🦞 / 2026-06-14", {
    x: 1, y: 6.7, w: 11.33, h: 0.5,
    fontSize: 10, fontColor: COLORS.gray, align: "center", lineSpacingMultiple: 1.2,
  });
}

// Save
const outputPath = path.join(process.env.HOME, ".openclaw/workspace", "小龙虾生态网络_大众介绍版.pptx");
pres.writeFile({ outputPath }).then(() => {
  console.log("✅ PPT generated:", outputPath);
}).catch((err) => {
  console.error("❌ Error:", err);
  process.exit(1);
});

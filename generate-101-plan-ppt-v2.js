const pptxgenjs = require("pptxgenjs");

const pres = new pptxgenjs();
pres.defineLayout({ name: "LAYOUT_16_9", width: 13.33, height: 7.5 });
pres.layout = "LAYOUT_16_9";

const C = {
  primary: "#1A365D", secondary: "#2B6CB0", accent: "#E8832A",
  light: "#F7F9FC", white: "#FFFFFF", text: "#2D3748",
  muted: "#718096", success: "#38A169", teal: "#319795"
};

// ========== Slide 1: 封面 ==========
const s1 = pres.addSlide();
s1.background = { fill: C.primary };
s1.addShape("rect", { x: 0, y: 0, w: "100%", h: 0.12, fill: C.accent });
s1.addText("教育部“101计划”首批核心课程培育推进会", {
  x: 1, y: 1.2, w: 11.33, h: 1, fontSize: 34, fontFace: "微软雅黑",
  color: C.white, bold: true, align: "center"
});
s1.addText("计算机网络课程建设构想", {
  x: 1, y: 2.5, w: 11.33, h: 0.7, fontSize: 26, fontFace: "微软雅黑",
  color: C.accent, bold: true, align: "center"
});
s1.addText("浙江工商大学 \u00b7 诸葛斌团队\n2026\u5e746\u670825\u65e5 | \u79d1\u521b\u5927\u697c206", {
  x: 1, y: 5.5, w: 11.33, h: 0.8, fontSize: 15, fontFace: "微软雅黑",
  color: "#A0AEC0", align: "center"
});

// ========== Slide 2: 101计划背景 ==========
const s2 = pres.addSlide();
s2.background = { fill: C.white };
s2.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s2.addText("101\u8ba1\u5212\uff1a\u62d4\u5c16\u521b\u65b0\u4eba\u624d\u57f9\u517b\u7b51\u57fa\u6027\u5de5\u7a0b", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s2.addText("政策定位", {
  x: 0.8, y: 1.5, w: 3, h: 0.5, fontSize: 20, fontFace: "微软雅黑",
  color: C.primary, bold: true
});
s2.addText("\u2022 \u6559\u80b2\u90e8\u7edf\u7b79\uff0c\u6c47\u805a\u9876\u5c16\u9ad8\u6821\u3001\u9876\u5c16\u5e08\u8d44\u3001\u9876\u5c16\u51fa\u7248\u5355\u4f4d\n\u2022 \u4ee5\u8bfe\u7a0b\u3001\u6559\u6750\u3001\u6559\u5e08\u548c\u5b9e\u8df5\u9879\u76ee\u4e3a\u6838\u5fc3\u8981\u7d20\u5efa\u8bbe\n\u2022 \u5e26\u52a8\u6559\u80b2\u6559\u5b66\u7cfb\u7edf\u5168\u9762\u6539\u9769\n\u2022 \u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\u9886\u57df\u9996\u6279\u6838\u5fc3\u8bfe\u7a0b\u4e4b\u4e00", {
  x: 0.8, y: 2.1, w: 11, h: 2.2, fontSize: 15, fontFace: "微软雅黑",
  color: C.text, lineSpacingMultiple: 1.5
});
s2.addShape("rect", { x: 0.8, y: 4.8, w: 11.5, h: 2, fill: C.light, rectRadius: 0.15, line: { color: C.accent, width: 2 } });
s2.addText("\u6211\u4eec\u7684\u5b9a\u4f4d\uff1a\u6a21\u5757\u4e00 \u00b7 \u8ba1\u7b97\u673a\u7f51\u7edc\uff08\u672c\u79d1 \u00b7 \u4e13\u4e1a\u6838\u5fc3\u8bfe\uff09\n\n\u5efa\u8bbe\u5468\u671f\uff1a2026.01 - 2027.12\uff082\u5e74\uff09\n\u6838\u5fc3\u6539\u9769\uff1a\u56fd\u4ea7\u4e91\u5e73\u53f0\u4e3a\u5e95\u5ea7\uff0c\u6df1\u5ea6\u878d\u5408\u667a\u80fd\u4f53\u5de5\u5177\uff0c\u6784\u5efa\u5168\u94fe\u6761\u6559\u5b66\u65b0\u8303\u5f0f", {
  x: 1, y: 4.9, w: 11, h: 1.8, fontSize: 15, fontFace: "微软雅黑",
  color: C.primary, align: "center", lineSpacingMultiple: 1.4
});

// ========== Slide 3: 团队现有成果基础 ==========
const s3 = pres.addSlide();
s3.background = { fill: C.white };
s3.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s3.addText("\u56e2\u961f\u73b0\u6709\u6210\u679c\u57fa\u7840", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});

const achievements = [
  { title: "MOOC\u5728\u7ebf\u8bfe\u7a0b", desc: "\u300a\u9ad8\u7ea7\u7f51\u7edc\u901a\u4fe1\u539f\u7406\u5b9e\u8df5\u300b\n\u4e2d\u56fd\u5927\u5b66MOOC\u5e73\u53f0 | 228\u4eba\u5b66\u4e60\n18\u5468\u8bfe\u7a0b\uff08\u5df2\u5b8c\u621014\u5468\uff09\n\u5408\u4f5c\u4f01\u4e1a\uff1a\u963f\u91cc\u4e91", color: C.secondary },
  { title: "\u5df2\u51fa\u7248\u6559\u6750", desc: "\u300a\u7f51\u7edc\u901a\u4fe1\u539f\u7406\u5b9e\u8df5\u300b\uff08\u6e05\u534e\u51fa\u7248\u793e,2024\uff09\n\u300a\u7cfb\u7edf\u7ea7\u7f16\u7a0b\u53ca\u5206\u5e03\u5f0f\u5e94\u7528\u5b9e\u73b0\u6280\u672f\u300b\n\uff08\u6e05\u534e\u51fa\u7248\u793e,\u5df2\u5b9a\u7a3f\uff09\n4-6\u4f4d\u6838\u5fc3\u4f5c\u8005", color: C.teal },
  { title: "\u7701\u7ea7\u4e00\u6d41\u5b9e\u9a8c\u8bfe", desc: "\u300a\u8ba1\u7b97\u673a\u7f51\u7edc\u5b9e\u9a8c\u300b\u7701\u7ea7\u7ebf\u4e0a\u4e00\u6d41\u8bfe\u7a0b\n7\u671f\u8fd0\u884c | 623\u4eba\u6b21\u9009\u8bfe\n22\u6240\u9ad8\u6821\u8986\u76d6\n\u7d2f\u8ba1\u8bbf\u95ee59.4\u4e07\u6b21", color: C.success },
  { title: "\u5b9e\u9a8c\u5e73\u53f0", desc: "\u963f\u91cc\u4e91\u4e91\u5b9e\u9a8c\u5ba4\u5e73\u53f0\nMininet / OpenDaylight / OpenStack\n\u652f\u6301\u7f51\u7edc\u865a\u62df\u5316\u5b9e\u6218\n\u4f01\u4e1a\u7ea7\u5b9e\u9a8c\u73af\u5883", color: C.accent }
];

let ax = 0.5;
achievements.forEach(a => {
  s3.addShape("rect", { x: ax, y: 1.5, w: 3.05, h: 3.5, fill: C.light, rectRadius: 0.12, line: { color: a.color, width: 1.5 } });
  s3.addText(a.title, {
    x: ax + 0.15, y: 1.6, w: 2.75, h: 0.5, fontSize: 16, fontFace: "微软雅黑",
    color: a.color, bold: true, align: "center"
  });
  s3.addText(a.desc, {
    x: ax + 0.15, y: 2.2, w: 2.75, h: 2.6, fontSize: 13, fontFace: "微软雅黑",
    color: C.text, align: "left", lineSpacingMultiple: 1.4
  });
  ax += 3.2;
});
s3.addText("\u56e2\u961f\u6838\u5fc3\u6210\u5458\uff1a\u8bf8\u845b\u658c\uff08\u6559\u6388\uff09\u3001\u91d1\u84c9\uff08\u526f\u6559\u6388\uff09\u3001\u9ad8\u660e\u3001\u674e\u4f20\u714c\u3001\u848b\u732e", {
  x: 0.8, y: 5.5, w: 11, h: 0.5, fontSize: 14, fontFace: "微软雅黑",
  color: C.muted, align: "center"
});

// ========== Slide 4: 核心改革方向 ==========
const s4 = pres.addSlide();
s4.background = { fill: C.white };
s4.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s4.addText("\u6838\u5fc3\u6539\u9769\u65b9\u5411\uff1aAI\u539f\u751f\u6559\u5b66\u65b0\u8303\u5f0f", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s4.addText("\u7406\u5ff5\u8f6c\u53d8", {
  x: 0.8, y: 1.5, w: 3, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.accent, bold: true
});
s4.addText("\u2022 \u4ece\u201c\u77e5\u8bc6\u704c\u8f93\u201d \u2192 \u201cAI\u5e94\u7528\u7684\u5b9e\u8df5\u573a\u666f\u201d\n\u2022 \u8bfe\u7a0b\u662fAI\u5de5\u5177\u5e94\u7528\u7684\u80cc\u666f\u573a\u666f\n\u2022 \u6838\u5fc3\u76ee\u6807\uff1a\u57f9\u517b\u5bf9AI\u751f\u6210\u5185\u5bb9\u7684\u5224\u65ad\u529b\n\u2022 \u4e94\u5e74\u540e\u4e13\u4e1a\u6559\u80b2\u5c06\u5168\u9762\u91cd\u6784", {
  x: 0.8, y: 2.1, w: 5.5, h: 2.2, fontSize: 14, fontFace: "微软雅黑",
  color: C.text, lineSpacingMultiple: 1.5
});
s4.addShape("rect", { x: 7, y: 1.4, w: 5.5, h: 3.2, fill: C.primary, rectRadius: 0.12 });
s4.addText("\u5168\u94fe\u6761\u6559\u5b66\u65b0\u8303\u5f0f", {
  x: 7.2, y: 1.5, w: 5, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.accent, bold: true, align: "center"
});
const chainSteps = [
  "1. \u667a\u80fd\u751f\u6210 \u2014 AI\u8f85\u52a9\u77e5\u8bc6\u70b9\u5185\u5bb9\u751f\u6210",
  "2. \u79c1\u6709\u7b54\u7591 \u2014 \u77e5\u8bc6\u5e93\u673a\u5668\u4eba\u7cbe\u51c6\u7b54\u7591",
  "3. \u667a\u6167\u7ba1\u7406 \u2014 AI\u9a71\u52a8\u8bfe\u7a0b\u8d44\u6e90\u7ba1\u7406",
  "4. \u5b9e\u6218\u90e8\u7f72 \u2014 \u56fd\u4ea7\u4e91\u5e73\u53f0\u771f\u5b9e\u73af\u5883\u9a8c\u8bc1"
];
let cy = 2.2;
chainSteps.forEach(step => {
  s4.addText(step, {
    x: 7.3, y: cy, w: 5, h: 0.55, fontSize: 14, fontFace: "微软雅黑",
    color: C.white, lineSpacingMultiple: 1.3
  });
  cy += 0.55;
});
s4.addShape("rect", { x: 0.8, y: 5.2, w: 11.5, h: 1, fill: C.light, rectRadius: 0.1 });
s4.addText('\u201c\u672a\u6765\u8bfe\u7a0b\u5efa\u8bbe\u7684\u5173\u952e\u4e0d\u518d\u662f\u77e5\u8bc6\u4f20\u6388\uff0c\u800c\u662f\u57f9\u517b\u5b66\u751f\u5bf9AI\u751f\u6210\u5185\u5bb9\u7684\u5224\u65ad\u529b\u3002\u201d\n\u2014\u2014 \u8bf8\u845b\u658c', {
  x: 1, y: 5.25, w: 11, h: 0.9, fontSize: 14, fontFace: "微软雅黑",
  color: C.primary, italic: true, align: "center", lineSpacingMultiple: 1.3
});

// ========== Slide 5: 三大核心任务总览 ==========
const s5 = pres.addSlide();
s5.background = { fill: C.white };
s5.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s5.addText("\u4e09\u5927\u6838\u5fc3\u4efb\u52a1\u4f53\u7cfb", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
const tasks = [
  {
    num: "\u4efb\u52a1\u4e00", title: "\u8bfe\u7a0b\u5efa\u8bbe", lead: "\u8bf8\u845b\u658c",
    items: ["\u77e5\u8bc6\u4f53\u7cfb\u68b3\u7406\uff0850-60\u4e2a\u77e5\u8bc6\u70b9\uff09", "\u77e5\u8bc6\u70b9\u56fe\u8c31\u53ef\u89c6\u5316\u6784\u5efa", "\u8bfe\u7a0b\u5efa\u8bbe\u6307\u5357\u7f16\u5199", "\u672c\u5730\u5316\u6559\u5b66\u5927\u7eb2\u8bbe\u8ba1", "\u6559\u5b66\u8d44\u6e90\u5305\u5f00\u53d1\uff08\u52a8\u753b/\u8bfe\u4ef6/\u4e60\u9898\uff09", "\u5b9e\u9a8c\u8bfe\u7a0b2.0\u5347\u7ea7"],
    color: C.secondary
  },
  {
    num: "\u4efb\u52a1\u4e8c", title: "\u6559\u6750\u7f16\u5199", lead: "\u8bf8\u845b\u658c + \u9ad8\u660e",
    items: ["\u57fa\u4e8e\u73b0\u6709\u6559\u6750\u5347\u7ea7\uff08\u975e\u5168\u65b0\u7f16\u5199\uff09", "\u6570\u5b57\u6559\u6750\u914d\u5957\u89c6\u9891/\u52a8\u753b/\u4ea4\u4e92", "\u6bcf\u7ae0\u914d\u5957\u6848\u4f8b\u22653\u4e2a\uff0c\u4f01\u4e1a\u6848\u4f8b\u226530%", "\u6e05\u534e\u5927\u5b66\u51fa\u7248\u793e\u5408\u4f5c\u7eed\u7b7e", "\u6837\u7ae0\u64b0\u5199\uff081-2\u7ae0\u5148\u884c\uff09", "\u6559\u6750\u521d\u7a3f\u5b8c\u6210"],
    color: C.teal
  },
  {
    num: "\u4efb\u52a1\u4e09", title: "\u5b9e\u8df5\u6848\u4f8b", lead: "\u8bf8\u845b\u658c + \u848b\u732e",
    items: ["\u9a8c\u8bc1\u6027/\u8bbe\u8ba1\u6027/\u7efc\u5408\u6027=3:4:3", "\u667a\u80fd\u4f53\u8f85\u52a9\u5b9e\u9a8c\uff08AI\u751f\u6210+\u4eba\u5de5\u6392\u9519\uff09", "\u963f\u91cc\u4e91\u5e73\u53f0+\u591a\u4e91\u652f\u6301\u5347\u7ea7", "\u62d3\u5c55\u534e\u4e3a/\u534e\u4e09\u7b49\u4f01\u4e1a\u5408\u4f5c", "\u5b9e\u9a8c\u9879\u76ee\u6e05\u5355\uff08\u226510\u4e2a\uff09", "\u5b9e\u8df5\u6848\u4f8b\u7fa4\u5efa\u8bbe\uff08\u22655\u4e2a\uff09"],
    color: C.accent
  }
];
let tx = 0.4;
tasks.forEach(t => {
  s5.addShape("rect", { x: tx, y: 1.4, w: 4.1, h: 5.3, fill: C.light, rectRadius: 0.1, line: { color: t.color, width: 2 } });
  s5.addText(`${t.num}\uff1a${t.title}`, {
    x: tx + 0.15, y: 1.5, w: 3.8, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
    color: t.color, bold: true, align: "center"
  });
  s5.addText(`\u8d1f\u8d23\u4eba\uff1a${t.lead}`, {
    x: tx + 0.15, y: 2, w: 3.8, h: 0.4, fontSize: 13, fontFace: "微软雅黑",
    color: C.muted, align: "center"
  });
  s5.addText(t.items.map((item, i) => `${i + 1}. ${item}`).join("\n"), {
    x: tx + 0.15, y: 2.4, w: 3.8, h: 4, fontSize: 12, fontFace: "微软雅黑",
    color: C.text, lineSpacingMultiple: 1.4
  });
  tx += 4.25;
});

// ========== Slide 6: 时间节点 ==========
const s6 = pres.addSlide();
s6.background = { fill: C.white };
s6.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s6.addText("\u5173\u952e\u91cc\u7a0b\u7891\u4e0e\u65f6\u95f4\u8282\u70b9", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
const milestones = [
  { date: "2026.06.30", items: "\u77e5\u8bc6\u4f53\u7cfb\u521d\u7a3f + \u6559\u5b66\u5927\u7eb2\u672c\u5730\u5316", done: true },
  { date: "2026.07.15", items: "\u6559\u6750\u6846\u67b6\u8bbe\u8ba1 + \u77e5\u8bc6\u70b9\u56fe\u8c31\u5b8c\u6210", done: false },
  { date: "2026.07.31", items: "\u6559\u6750\u6837\u7ae02\u7ae0 + \u5b9e\u9a8c\u6848\u4f8b5\u4e2a", done: false },
  { date: "2026.08.31", items: "\u534f\u8bae\u52a8\u753b5\u4e2a + \u77e5\u8bc6\u5e93\u673a\u5668\u4ebaMVP + \u4f01\u4e1a\u5408\u4f5c", done: false },
  { date: "2026.09.30", items: "\u5168\u90e8\u4ea4\u4ed8\u7269\u521d\u7a3f\u5b8c\u6210 + \u6559\u5b66\u8d44\u6e90\u5305", done: false },
  { date: "2026.10.31", items: "\u6559\u6750\u521d\u7a3f + \u5b9e\u9a8c\u8bfe\u7a0b2.0 + \u4e2d\u671f\u6750\u6599", done: false },
  { date: "2026.11-12", items: "\u4e2d\u671f\u5de5\u4f5c\u603b\u7ed3 + \u8d28\u91cf\u6807\u51c6\u5236\u5b9a", done: false }
];
let my = 1.5;
milestones.forEach(m => {
  s6.addShape("rect", { x: 0.8, y: my, w: 0.45, h: 0.45, fill: m.done ? C.success : C.light, rectRadius: 0.1, line: { color: m.done ? C.success : C.muted, width: 1 } });
  s6.addText(m.date, {
    x: 1.5, y: my - 0.02, w: 2, h: 0.5, fontSize: 16, fontFace: "微软雅黑",
    color: C.primary, bold: true
  });
  s6.addText(m.items, {
    x: 3.6, y: my - 0.02, w: 8, h: 0.5, fontSize: 15, fontFace: "微软雅黑",
    color: C.text
  });
  s6.addText(m.done ? "\u2713" : "\u25cb", {
    x: 12, y: my - 0.02, w: 0.5, h: 0.5, fontSize: 16, fontFace: "微软雅黑",
    color: m.done ? C.success : C.muted, bold: true
  });
  my += 0.65;
});

// ========== Slide 7: 智慧树 ==========
const s7 = pres.addSlide();
s7.background = { fill: C.white };
s7.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s7.addText("\u667a\u6167\u6811\u5728\u7ebf\u8bfe\u7a0b\u90e8\u7f72\u8fdb\u5c55", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s7.addText("\u5e73\u53f0\u4ef7\u503c", {
  x: 0.8, y: 1.5, w: 3, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.primary, bold: true
});
s7.addText("\u2022 \u56fd\u5185\u9886\u5148\u8de8\u6821\u5171\u4eab\u5728\u7ebf\u6559\u80b2\u5e73\u53f0\n\u2022 \u652f\u6301\u5927\u89c4\u6a21\u5728\u7ebf\u5f00\u653e\u8bfe\u7a0b\u8fd0\u8425\n\u2022 \u5b8c\u5584\u5b66\u60c5\u5206\u6790\u4e0e\u8fc7\u7a0b\u8bc4\u4ef7\u4f53\u7cfb\n\u2022 \u5b66\u5206\u4e92\u8ba4\uff0c\u6269\u5927\u8bfe\u7a0b\u8f90\u5c04\u9762", {
  x: 0.8, y: 2.1, w: 5.5, h: 2, fontSize: 14, fontFace: "微软雅黑",
  color: C.text, lineSpacingMultiple: 1.5
});
s7.addText("\u5f53\u524d\u90e8\u7f72\u8fdb\u5ea6", {
  x: 7, y: 1.5, w: 4, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.primary, bold: true
});
const deployList = [
  { text: "\u2713 \u8bfe\u7a0b\u6846\u67b6\u642d\u5efa", status: "done" },
  { text: "\u2713 \u6559\u5b66\u89c6\u9891\u4e0a\u4f20", status: "done" },
  { text: "\u2713 \u7ae0\u8282\u6d4b\u9a8c\u914d\u7f6e", status: "done" },
  { text: "\u27f3 \u8ba8\u8bba\u533a\u4e0e\u4e92\u52a8\u6a21\u5757\u8bbe\u7f6e", status: "progress" },
  { text: "\u27f3 \u4f5c\u4e1a\u6279\u6539\u89c4\u5219\u914d\u7f6e", status: "progress" },
  { text: "\u25cb AI\u8f85\u52a9\u7b54\u7591\u6a21\u5757\u63a5\u5165", status: "todo" },
  { text: "\u25cb \u671f\u672b\u8003\u8bd5\u4e0e\u8bc4\u4ef7\u914d\u7f6e", status: "todo" }
];
let dy = 2.1;
deployList.forEach(d => {
  const color = d.status === "done" ? C.success : d.status === "progress" ? C.accent : C.muted;
  s7.addText(d.text, {
    x: 7, y: dy, w: 5.5, h: 0.45, fontSize: 14, fontFace: "微软雅黑",
    color: color, bold: d.status === "done"
  });
  dy += 0.45;
});

// ========== Slide 8: AI原生教学 ==========
const s8 = pres.addSlide();
s8.background = { fill: C.white };
s8.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s8.addText("AI\u539f\u751f\u6559\u5b66\u521b\u65b0\u5b9e\u8df5", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s8.addText("\u4f5c\u4e1a\u5f62\u5f0f\u6539\u9769", {
  x: 0.8, y: 1.5, w: 4, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.accent, bold: true
});
s8.addText("\u2022 \u5b66\u751f\u4f7f\u7528AI\u4e3a\u6bcf\u4e2a\u77e5\u8bc6\u70b9\u751f\u6210\u8bb2\u89e3\u6750\u6599\n\u2022 \u6210\u679c\u5f62\u5f0f\uff1a\u52a8\u753b\u3001\u6587\u6863\u3001\u53ef\u89c6\u5316\u5185\u5bb9\n\u2022 \u6559\u5e08\u7b5b\u9009\u6700\u4f73\u7248\u672c\uff08\u6bcf\u77e5\u8bc6\u70b9\u90093\u4e2a\uff09\n\u2022 \u7eb3\u5165\u8bfe\u7a0b\u8d44\u6e90\u5e93\uff0c\u9762\u5411\u63a8\u5e7f\u590d\u7528", {
  x: 0.8, y: 2.1, w: 5.5, h: 2, fontSize: 14, fontFace: "微软雅黑",
  color: C.text, lineSpacingMultiple: 1.5
});
s8.addShape("rect", { x: 7, y: 1.4, w: 5.5, h: 3.2, fill: C.light, rectRadius: 0.12, line: { color: C.accent, width: 2 } });
s8.addText("\u5173\u952e\u539f\u5219", {
  x: 7.2, y: 1.5, w: 5, h: 0.4, fontSize: 17, fontFace: "微软雅黑",
  color: C.primary, bold: true, align: "center"
});
const principles = [
  "1. AI\u4f5c\u4e3a\u5b66\u751f\u81ea\u4e3b\u5b9e\u8df5\u8f7d\u4f53\uff0c\u975e\u6559\u5e08\u4ee3\u52b3",
  "2. \u5b9e\u9a8c\u8bfe\u4fdd\u7559\u4f20\u7edf\u64cd\u4f5c\uff0cAI\u8f85\u52a9\u6982\u5ff5\u7406\u89e3",
  "3. \u5f15\u5bfc\u9a8c\u8bc1AI\u7ed3\u679c\uff0c\u63d0\u5347\u5224\u65ad\u529b",
  "4. \u5b66\u751f\u9a71\u52a8\u521b\u65b0\uff0c\u4eba\u5de5\u7b5b\u9009\u4f18\u8d28\u6210\u679c",
  "5. \u6559\u80b2\u5b9e\u6548\u4f18\u5148\uff0c\u8d85\u8d8a\u4f20\u7edfPPT\u548c\u6559\u6750",
  '6. \u201c\u627e\u4e24\u4e2a\u597d\u4f5c\u54c1\u201d\u6bd4\u201c\u8ba9\u6240\u6709\u4eba\u505a\u5bf9\u201d\u66f4\u91cd\u8981'
];
let py = 2;
principles.forEach(p => {
  s8.addText(p, {
    x: 7.2, y: py, w: 5.1, h: 0.45, fontSize: 13, fontFace: "微软雅黑",
    color: C.text, lineSpacingMultiple: 1.3
  });
  py += 0.45;
});

// ========== Slide 9: 试点高校 ==========
const s9 = pres.addSlide();
s9.background = { fill: C.white };
s9.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s9.addText("\u8bd5\u70b9\u9ad8\u6821\u62d3\u5c55\u8ba1\u5212\uff08\u7b2c\u4e8c\u5e74\uff09", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s9.addText("\u5efa\u8bae\u8bd5\u70b9\u9ad8\u6821\u540d\u5355", {
  x: 0.8, y: 1.5, w: 4, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.primary, bold: true
});
const universities = [
  "\u6d59\u6c5f\u5de5\u4e1a\u5927\u5b66",
  "\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66",
  "\u6d59\u6c5f\u7406\u5de5\u5927\u5b66",
  "\u5b81\u6ce2\u5927\u5b66",
  "\u6d59\u6c5f\u5e08\u8303\u5927\u5b66"
];
let uy = 2.2;
universities.forEach(u => {
  s9.addShape("rect", { x: 0.8, y: uy, w: 5.5, h: 0.55, fill: C.light, rectRadius: 0.08 });
  s9.addText(`\u2b50 ${u}`, {
    x: 1, y: uy + 0.05, w: 4, h: 0.45, fontSize: 16, fontFace: "微软雅黑",
    color: C.primary, bold: true
  });
  uy += 0.7;
});
s9.addText("\u8bd5\u7528\u5185\u5bb9", {
  x: 7.5, y: 1.5, w: 3, h: 0.5, fontSize: 18, fontFace: "微软雅黑",
  color: C.primary, bold: true
});
s9.addText("\u2022 \u914d\u5957\u6559\u6750 + \u5b9e\u9a8c\u6307\u5bfc\u4e66\n\u2022 \u5728\u7ebf\u8bfe\u7a0b + \u5b9e\u8df5\u6848\u4f8b\n\u2022 \u4e91\u5e73\u53f0\u5b9e\u9a8c\u73af\u5883\n\u2022 AI\u8f85\u52a9\u7b54\u7591\u6a21\u5757", {
  x: 7.5, y: 2.1, w: 5, h: 1.8, fontSize: 14, fontFace: "微软雅黑",
  color: C.text, lineSpacingMultiple: 1.5
});
s9.addShape("rect", { x: 7.5, y: 4.2, w: 5, h: 1.2, fill: C.light, rectRadius: 0.1, line: { color: C.accent, width: 1.5 } });
s9.addText("\u53cd\u9988\u673a\u5236\n\n\u95ee\u5377\u8c03\u67e5 + \u6df1\u5ea6\u8bbf\u8c08 + \u6570\u636e\u5206\u6790\n\u76ee\u6807\u6837\u672c\uff1a\u4e0d\u5c11\u4e8e500\u4efd", {
  x: 7.6, y: 4.25, w: 4.8, h: 1.1, fontSize: 13, fontFace: "微软雅黑",
  color: C.primary, align: "center", lineSpacingMultiple: 1.3
});

// ========== Slide 10: 协作机制 ==========
const s10 = pres.addSlide();
s10.background = { fill: C.white };
s10.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s10.addText("\u534f\u4f5c\u673a\u5236\u4e0e\u4fdd\u969c\u63aa\u65bd", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
s10.addShape("rect", { x: 0.8, y: 1.5, w: 11.5, h: 0.5, fill: C.primary });
s10.addText("\u4e8b\u9879", { x: 1, y: 1.5, w: 3, h: 0.5, fontSize: 15, fontFace: "微软雅黑", color: C.white, bold: true });
s10.addText("\u9891\u7387/\u65f6\u95f4", { x: 4, y: 1.5, w: 3, h: 0.5, fontSize: 15, fontFace: "微软雅黑", color: C.white, bold: true });
s10.addText("\u8d1f\u8d23\u4eba", { x: 8, y: 1.5, w: 3, h: 0.5, fontSize: 15, fontFace: "微软雅黑", color: C.white, bold: true });
const mechRows = [
  ["\u7ebf\u4e0a\u78b0\u5934\u4f1a", "\u53cc\u5468 | \u5468\u4e94 15:00-16:00", "\u8bf8\u845b\u658c"],
  ["\u7ebf\u4e0b\u7814\u8ba8\u4f1a", "\u6bcf\u5b63\u5ea6 | \u65f6\u95f4\u5f85\u5b9a", "\u5168\u4f53"],
  ["\u6587\u6863\u5f52\u6863", "\u6bcf\u6708 | \u6708\u5e95", "\u91d1\u84c9"],
  ["\u4e2d\u671f\u603b\u7ed3", "2026\u5e7411-12\u6708", "\u674e\u4f20\u714c"]
];
let ry = 2.1;
mechRows.forEach((row, i) => {
  const bg = i % 2 === 0 ? C.white : C.light;
  s10.addShape("rect", { x: 0.8, y: ry, w: 11.5, h: 0.5, fill: bg });
  s10.addText(row[0], { x: 1, y: ry, w: 3, h: 0.5, fontSize: 14, fontFace: "微软雅黑", color: C.text });
  s10.addText(row[1], { x: 4, y: ry, w: 3.8, h: 0.5, fontSize: 14, fontFace: "微软雅黑", color: C.text });
  s10.addText(row[2], { x: 8, y: ry, w: 3, h: 0.5, fontSize: 14, fontFace: "微软雅黑", color: C.text });
  ry += 0.55;
});
s10.addShape("rect", { x: 0.8, y: 5.2, w: 11.5, h: 1.2, fill: C.light, rectRadius: 0.1, line: { color: C.accent, width: 2 } });
s10.addText("\u4fdd\u969c\u63aa\u65bd\n\n\u2022 \u6587\u6863\u7edf\u4e00\u5b58\u653e\u9489\u9489\u7fa4\u6587\u4ef6/\u4e91\u5e73\u53f0\uff0c\u786e\u4fdd\u900f\u660e\u534f\u4f5c\n\u2022 \u6bcf\u6708\u5e95\u63d0\u4ea4\u8fdb\u5ea6\u62a5\u544a\uff0c\u786e\u4fdd\u8282\u70b9\u53ef\u63a7\n\u2022 AI\u7b97\u529b\u5145\u88d5\u652f\u6301\u957f\u671f\u63a2\u7d22\n\u2022 \u6559\u5e08\u56e2\u961f\u5148\u76f8\u4fe1AI\u6f5c\u529b\uff0c\u518d\u8c03\u6574\u6559\u5b66\u7b56\u7565", {
  x: 1, y: 5.25, w: 11, h: 1.1, fontSize: 13, fontFace: "微软雅黑",
  color: C.primary, lineSpacingMultiple: 1.3
});

// ========== Slide 11: 预期成果 ==========
const s11 = pres.addSlide();
s11.background = { fill: C.white };
s11.addShape("rect", { x: 0, y: 0, w: "100%", h: 1.1, fill: C.primary });
s11.addText("\u9884\u671f\u6210\u679c\u4e0e\u5c55\u671b", {
  x: 0.5, y: 0.1, w: 12, h: 0.9, fontSize: 26, fontFace: "微软雅黑",
  color: C.white, bold: true
});
const outcomes = [
  { text: "\u5efa\u6210\u7b26\u5408101\u8ba1\u5212\u6807\u51c6\u7684\u8ba1\u7b97\u673a\u7f51\u7edc\u6838\u5fc3\u8bfe\u7a0b\u4f53\u7cfb", color: C.secondary },
  { text: "\u51fa\u7248\u914d\u5957\u6838\u5fc3\u6559\u6750\uff08\u6e05\u534e\u51fa\u7248\u793e\uff09\u4e0e\u6570\u5b57\u8d44\u6e90", color: C.teal },
  { text: "\u5b8c\u6210\u667a\u6167\u6811\u5e73\u53f0\u5728\u7ebf\u8bfe\u7a0b\u90e8\u7f72\u4e0e\u8de8\u6821\u8fd0\u8425", color: C.success },
  { text: "\u5f62\u6210AI\u539f\u751f\u6559\u5b66\u8303\u5f0f\uff0c\u53ef\u590d\u5236\u63a8\u5e7f", color: C.accent },
  { text: "\u4e0d\u5c11\u4e8e5\u6240\u9ad8\u6821\u8bd5\u70b9\uff0c\u8986\u76d6500+\u5b66\u751f\u53cd\u9988", color: C.primary },
  { text: "\u57f9\u517b\u9ad8\u6c34\u5e73\u6570\u5b57\u5316\u6559\u5b66\u56e2\u961f", color: C.secondary }
];
let oy = 1.5;
outcomes.forEach(o => {
  s11.addShape("rect", { x: 0.8, y: oy, w: 0.55, h: 0.55, fill: o.color, rectRadius: 0.1 });
  s11.addText(o.text, {
    x: 1.55, y: oy - 0.03, w: 10.5, h: 0.6, fontSize: 17, fontFace: "微软雅黑",
    color: C.text, bold: true
  });
  oy += 0.75;
});

// ========== Slide 12: 结束页 ==========
const s12 = pres.addSlide();
s12.background = { fill: C.primary };
s12.addShape("rect", { x: 0, y: 0, w: "100%", h: 0.12, fill: C.accent });
s12.addText("\u611f\u8c22\u8046\u542c\uff01", {
  x: 1, y: 2.5, w: 11.33, h: 1, fontSize: 40, fontFace: "微软雅黑",
  color: C.white, bold: true, align: "center"
});
s12.addText("\u6b22\u8fce\u6279\u8bc4\u6307\u6b63", {
  x: 1, y: 3.5, w: 11.33, h: 0.7, fontSize: 24, fontFace: "微软雅黑",
  color: C.accent, align: "center"
});
s12.addText("诸葛斌团队 \u00b7 \u6d59\u6c5f\u5de5\u5546\u5927\u5b66\n\u8ba1\u7b97\u673a\u7f51\u7edc\u201c101\u8ba1\u5212\u201d\u8bfe\u7a0b\u5efa\u8bbe\u9879\u76ee", {
  x: 1, y: 5.5, w: 11.33, h: 0.8, fontSize: 16, fontFace: "微软雅黑",
  color: "#A0AEC0", align: "center"
});

const outputPath = "/home/admin/.openclaw/workspace/101\u8ba1\u5212_\u8ba1\u7b97\u673a\u7f51\u7edc\u8bfe\u7a0b\u5efa\u8bbe\u6784\u60f3_v2.pptx";
pres.writeFile({ outputFileName: outputPath })
  .then(() => console.log(`PPT v2\u5df2\u751f\u6210\uff1a${outputPath}`))
  .catch(err => console.error("\u751f\u6210PPT\u5931\u8d25\uff1a", err));
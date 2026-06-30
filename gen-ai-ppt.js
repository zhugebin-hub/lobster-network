const pptxgen = require("pptxgenjs");

const pres = new pptxgen();

// 设置幻灯片尺寸（16:9）
pres.defineLayout({ name: "LAYOUT", width: 13.33, height: 7.5 });
pres.layout = "LAYOUT";

// 配色
const C = {
  deep: "#0D1B2A",
  primary: "#1B3A5C",
  accent: "#00AEEF",
  accent2: "#F39C12",
  white: "#FFFFFF",
  light: "#E8F4FD",
  gray: "#A0AEC0",
  text: "#2D3748",
  lightText: "#CBD5E0",
};

// ============================================================
// 封面
// ============================================================
{
  const slide = pres.addSlide();
  slide.background = { fill: C.deep };

  // 装饰线条
  slide.addShape("rect", {
    x: 0, y: 0, w: "100%", h: 0.06, fill: C.accent,
  });
  slide.addShape("rect", {
    x: 0, y: 7.44, w: "100%", h: 0.06, fill: C.accent,
  });

  // 标题
  slide.addText("AI 时代人类的何去何从", {
    x: 1, y: 2.0, w: 11.33, h: 2.0,
    fontSize: 44, color: C.white, bold: true, align: "center",
    fontFace: "微软雅黑",
    lineSpacingMultiple: 1.2,
  });

  // 副标题
  slide.addText("当机器越来越像人，人该往哪里去？", {
    x: 1, y: 4.2, w: 11.33, h: 0.8,
    fontSize: 22, color: C.accent, align: "center",
    fontFace: "微软雅黑",
  });

  // 日期
  slide.addText("2026 年 6 月 22 日", {
    x: 1, y: 5.5, w: 11.33, h: 0.5,
    fontSize: 16, color: C.gray, align: "center",
    fontFace: "微软雅黑",
  });
}

// ============================================================
// 目录
// ============================================================
{
  const slide = pres.addSlide();
  slide.background = { fill: C.white };

  slide.addShape("rect", {
    x: 0, y: 0, w: "100%", h: 1.2, fill: C.primary,
  });
  slide.addText("目 录", {
    x: 0.5, y: 0.15, w: 5, h: 0.9,
    fontSize: 32, color: C.white, bold: true,
    fontFace: "微软雅黑",
  });

  const items = [
    "一、AI 正在改变什么",
    "二、人类不可替代的是什么",
    "三、AI 时代的核心风险",
    "四、人类可能的出路",
    "五、个人的行动建议",
  ];

  items.forEach((t, i) => {
    const y = 1.6 + i * 1.05;
    // 序号圆圈
    slide.addShape("oval", {
      x: 1.5, y: y, w: 0.55, h: 0.55,
      fill: i < 4 ? C.accent : C.accent2,
    });
    slide.addText(String(i + 1), {
      x: 1.5, y: y, w: 0.55, h: 0.55,
      fontSize: 18, color: C.white, bold: true, align: "center",
      fontFace: "微软雅黑",
    });
    slide.addText(t, {
      x: 2.3, y: y + 0.05, w: 8, h: 0.5,
      fontSize: 20, color: C.text,
      fontFace: "微软雅黑",
    });
  });
}

// ============================================================
// 通用函数：内容页
// ============================================================
function addContentSlide(title, bullets, sectionNum) {
  const slide = pres.addSlide();
  slide.background = { fill: C.white };

  // 顶部色条
  slide.addShape("rect", {
    x: 0, y: 0, w: "100%", h: 1.2, fill: C.primary,
  });

  // 标题
  slide.addText(title, {
    x: 0.6, y: 0.15, w: 11, h: 0.9,
    fontSize: 28, color: C.white, bold: true,
    fontFace: "微软雅黑",
  });

  // 章节标签
  if (sectionNum) {
    slide.addShape("rect", {
      x: 0.6, y: 1.5, w: 1.0, h: 0.35,
      fill: C.accent, rectRadius: 0.15,
    });
    slide.addText(sectionNum, {
      x: 0.6, y: 1.5, w: 1.0, h: 0.35,
      fontSize: 13, color: C.white, bold: true, align: "center",
      fontFace: "微软雅黑",
    });
  }

  // 内容区域
  const startY = sectionNum ? 2.1 : 1.5;
  const bulletObjs = bullets.map((b) => ({
    text: b,
    options: {
      fontSize: 16,
      color: C.text,
      fontFace: "微软雅黑",
      lineSpacingMultiple: 1.5,
      bullet: { type: "bullet", character: "●", color: C.accent, indent: 15 },
    },
  }));

  slide.addText(bulletObjs, {
    x: sectionNum ? 1.8 : 0.8,
    y: startY,
    w: sectionNum ? 10.8 : 11.7,
    h: 5.0,
    valign: "top",
    paraSpaceBefore: 6,
    paraSpaceAfter: 4,
  });

  return slide;
}

// ============================================================
// 引言页
// ============================================================
{
  const slide = pres.addSlide();
  slide.background = { fill: C.white };

  slide.addShape("rect", {
    x: 0, y: 0, w: "100%", h: 1.2, fill: C.primary,
  });
  slide.addText("引言：我们站在什么样的十字路口", {
    x: 0.6, y: 0.15, w: 11, h: 0.9,
    fontSize: 28, color: C.white, bold: true,
    fontFace: "微软雅黑",
  });

  slide.addText(
    "2026 年，AI 已经能够撰写论文、编写代码、诊断疾病、创作音乐。\n" +
    "它下棋胜过人类冠军，翻译跨越所有语种，对话中以假乱真。\n\n" +
    "每一次突破都伴随着同一个问题：\n" +
    "当机器越来越像人，人该往哪里去？\n\n" +
    "这不是杞人忧天，也不是盲目乐观就能回避的问题。\n" +
    "这是每一个生活在 AI 时代的人都需要认真思考的命题。",
    {
      x: 1.2, y: 1.8, w: 10.5, h: 4.5,
      fontSize: 20, color: C.text,
      fontFace: "微软雅黑",
      lineSpacingMultiple: 1.6,
      align: "left",
    }
  );
}

// ============================================================
// 第一部分
// ============================================================
addContentSlide(
  "一、AI 正在改变什么",
  [
    "1.1 能力的重新分配\n凡是可以被"标准化"和"规模化"的能力，AI 都会超越人类。这不是趋势，是已经发生的事实。",
    "1.2 职业的结构性冲击\n已发生：翻译、客服、初级程序员、内容审核、基础设计——岗位正在缩减\n正在发生：医生辅助诊断、法律文件审查、金融分析、新闻报道——人机协作模式成型\n即将发生：教师个性化辅导、心理咨询、管理决策——AI 开始进入"高信任"领域",
    "关键洞察：被替代的不是"职业"本身，而是职业中可被标准化的那部分。\n剩下的部分，才是人类需要重新定义的立足点。",
  ],
  "PART 1"
);

// ============================================================
// 第二部分
// ============================================================
addContentSlide(
  "二、人类不可替代的是什么（上）",
  [
    "2.1 意义创造的能力\nAI 可以写一首诗，但它不会因失恋而心碎，不会因信仰而献身，不会因孩子的第一次叫"爸爸"而热泪盈眶。",
    "人类的独特性在于：我们的创造源于真实的生命体验。\n• 艺术的价值不在于"好看"，而在于背后的情感与故事\n• 哲学的价值不在于"逻辑严密"，而在于对存在本身的追问\n• 宗教的价值不在于"论证充分"，而在于对超越性的渴求",
    "AI 可以模仿这些产物，但无法拥有产生这些产物的内在驱动力。",
  ],
  "PART 2"
);

addContentSlide(
  "二、人类不可替代的是什么（下）",
  [
    "2.2 价值判断的终极责任\nAI 可以告诉你方案 A 的成功率是 73%，方案 B 是 68%。\n但 AI 不会告诉你哪个方案"更值得"。\n"值得"涉及：我们相信什么、我们在乎什么、我们愿意为什么付出代价。\n责任只能由人承担——不是因为人比 AI 聪明，而是因为责任只能由人承担。",
    "2.3 真实连接的力量\n两个人之间的信任、爱、共情、默契——建立在"都是真实存在的生命"的基础之上。\n真实连接的核心是"共同脆弱"——两个有限的生命彼此敞开，这种体验无法被算法复制。",
  ],
  "PART 2"
);

// ============================================================
// 第三部分
// ============================================================
addContentSlide(
  "三、AI 时代的核心风险",
  [
    "3.1 不平等的加剧\n掌握 AI 技术与资本的人，生产力呈指数级增长；被 AI 替代的劳动者，面临失业与技能贬值的双重打击。\nAI 时代的速度更快、冲击更大，留给社会适应的时间更短。",
    "3.2 人类能动性的退化\n如果 AI 帮我们做所有决定，我们还保有判断力吗？\n如果 AI 帮我们写所有文字，我们还保有表达力吗？\n大规模"认知外包"的风险不容忽视。",
    "3.3 权力的集中与失控\n技术垄断、信息操控、自主系统的风险——\n这些问题不是技术问题，是政治问题和伦理问题。",
  ],
  "PART 3"
);

// ============================================================
// 第四部分
// ============================================================
addContentSlide(
  "四、人类可能的出路（上）",
  [
    "4.1 从"劳动谋生"到"创造意义"\n艺术与文化创造：不是为了效率，而是为了表达\n社区与服务：人与人之间真实的关怀与互助\n探索与发现：科学、哲学、精神层面的追问\n体验与成长：把"活得好"本身作为一种追求",
    "4.2 从"知识掌握"到"问题提出"\nAI 时代，知道答案不再稀缺，稀缺的是提出好问题的能力。\n好问题能揭示被忽视的真相，打开新的可能性，重新定义游戏规则。\n教育的重心需要从"传授知识"转向"培养提问能力"。",
  ],
  "PART 4"
);

addContentSlide(
  "四、人类可能的出路（下）",
  [
    "4.3 从"效率竞争"到"深度体验"\nAI 比人类更高效。在效率赛道上和 AI 竞争，是注定失败的策略。\n但人类可以选择不比效率，比深度。\n在 AI 时代，"活得很深"可能比"做得很快"更有价值。",
    "4.4 重建社会契约\n教育体系改革：从知识传授转向能力培养\n社会保障升级：探索全民基本收入、终身学习账户、职业转型支持\n技术治理框架：建立 AI 伦理审查、算法透明度要求、数据权利保护\n新的分配机制：让 AI 创造的红利惠及更多人。",
  ],
  "PART 4"
);

// ============================================================
// 第五部分
// ============================================================
addContentSlide(
  "五、个人的行动建议",
  [
    "5.1 培养 AI 无法替代的能力\n深度思考、情感智慧、跨领域整合、创造力",
    "5.2 学会与 AI 协作\n把 AI 当作工具，而不是对手；学会用 AI 放大自己的能力；保持对 AI 能力的清醒认知",
    "5.3 关注真实的生活\n投入真实的人际关系，保持身体的感知能力，培养不需要屏幕的爱好，定期"断联"",
    "5.4 参与公共讨论\n关注 AI 伦理与治理，参与社区建设，推动技术向善",
  ],
  "PART 5"
);

// ============================================================
// 结语
// ============================================================
{
  const slide = pres.addSlide();
  slide.background = { fill: C.deep };

  slide.addShape("rect", {
    x: 0, y: 0, w: "100%", h: 0.06, fill: C.accent,
  });

  slide.addText(
    "人类的价值不在于"不可替代"，\n而在于"选择成为什么"",
    {
      x: 1, y: 1.5, w: 11.33, h: 2.0,
      fontSize: 36, color: C.white, bold: true, align: "center",
      fontFace: "微软雅黑",
      lineSpacingMultiple: 1.4,
    }
  );

  slide.addText(
    "机器可以被设计去追求目标，但目标本身是人类赋予的。\n" +
    "AI 可以帮我们发现世界"是什么"，\n" +
    "但"世界应该是什么"——这个问题，始终需要人类来回答。\n\n" +
    "未来不属于 AI，也不属于拒绝 AI 的人。\n" +
    "未来属于那些能在 AI 时代依然保持人性深度、\n" +
    "同时善用技术力量的人。",
    {
      x: 1.5, y: 4.0, w: 10.33, h: 2.5,
      fontSize: 18, color: C.lightText, align: "center",
      fontFace: "微软雅黑",
      lineSpacingMultiple: 1.5,
    }
  );

  slide.addText("我们何去何从？答案不在技术里，在每一个活着的人的心里。", {
    x: 1, y: 6.5, w: 11.33, h: 0.6,
    fontSize: 16, color: C.accent, align: "center",
    fontFace: "微软雅黑",
  });
}

// ============================================================
// 保存
// ============================================================
pres.writeFile("AI时代人类的何去何从.pptx").then((path) => {
  console.log("PPT 已生成:", path);
}).catch((err) => {
  console.error("生成失败:", err);
});

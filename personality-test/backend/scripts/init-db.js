const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '../data');

// 确保数据目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 测试题目（每个维度 10 题，共 40 题）
const questions = [
  // 维度 1: 外向 (E) vs 内向 (I)
  { id: 1, content: "在社交聚会中，你通常会主动认识新朋友", dimension: "EI", direction: 1 },
  { id: 2, content: "独处时你感到精力充沛", dimension: "EI", direction: -1 },
  { id: 3, content: "你更喜欢小组讨论而不是一对一交流", dimension: "EI", direction: 1 },
  { id: 4, content: "在人群中你经常保持沉默观察", dimension: "EI", direction: -1 },
  { id: 5, content: "你享受成为关注的焦点", dimension: "EI", direction: 1 },
  { id: 6, content: "你更喜欢深度的一对一对话", dimension: "EI", direction: -1 },
  { id: 7, content: "参加大型活动后你需要独处恢复精力", dimension: "EI", direction: -1 },
  { id: 8, content: "你乐于在会议上第一个发言", dimension: "EI", direction: 1 },
  { id: 9, content: "你有很多泛泛之交的朋友", dimension: "EI", direction: 1 },
  { id: 10, content: "你更喜欢安静的工作环境", dimension: "EI", direction: -1 },
  
  // 维度 2: 直觉 (N) vs 感觉 (S)
  { id: 11, content: "你更关注未来的可能性而非现实细节", dimension: "NS", direction: 1 },
  { id: 12, content: "你相信具体的经验和事实", dimension: "NS", direction: -1 },
  { id: 13, content: "你喜欢抽象的概念和理论", dimension: "NS", direction: 1 },
  { id: 14, content: "你注重实际和实用的解决方案", dimension: "NS", direction: -1 },
  { id: 15, content: "你经常思考事物的深层含义", dimension: "NS", direction: 1 },
  { id: 16, content: "你更相信已经验证过的方法", dimension: "NS", direction: -1 },
  { id: 17, content: "你喜欢想象和创新", dimension: "NS", direction: 1 },
  { id: 18, content: "你关注当下的具体体验", dimension: "NS", direction: -1 },
  { id: 19, content: "你擅长看到事物之间的关联", dimension: "NS", direction: 1 },
  { id: 20, content: "你更喜欢按部就班地做事", dimension: "NS", direction: -1 },
  
  // 维度 3: 理性 (T) vs 感性 (F)
  { id: 21, content: "做决定时你更依赖逻辑分析", dimension: "TF", direction: 1 },
  { id: 22, content: "做决定时你会考虑他人的感受", dimension: "TF", direction: -1 },
  { id: 23, content: "你认为诚实比和谐更重要", dimension: "TF", direction: 1 },
  { id: 24, content: "你尽量避免冲突和矛盾", dimension: "TF", direction: -1 },
  { id: 25, content: "你更看重公平而非人情", dimension: "TF", direction: 1 },
  { id: 26, content: "你容易对他人的情绪产生共鸣", dimension: "TF", direction: -1 },
  { id: 27, content: "你习惯客观分析问题", dimension: "TF", direction: 1 },
  { id: 28, content: "你重视人际关系的和谐", dimension: "TF", direction: -1 },
  { id: 29, content: "你认为规则应该被严格执行", dimension: "TF", direction: 1 },
  { id: 30, content: "你愿意为他人破例", dimension: "TF", direction: -1 },
  
  // 维度 4: 计划 (J) vs 灵活 (P)
  { id: 31, content: "你喜欢提前制定详细的计划", dimension: "JP", direction: 1 },
  { id: 32, content: "你更喜欢随性而为", dimension: "JP", direction: -1 },
  { id: 33, content: "截止日期前你习惯提前完成", dimension: "JP", direction: 1 },
  { id: 34, content: "你在压力下工作效率更高", dimension: "JP", direction: -1 },
  { id: 35, content: "你讨厌计划被打乱", dimension: "JP", direction: 1 },
  { id: 36, content: "你享受即兴和意外", dimension: "JP", direction: -1 },
  { id: 37, content: "你的工作和生活很有条理", dimension: "JP", direction: 1 },
  { id: 38, content: "你经常同时处理多件事", dimension: "JP", direction: -1 },
  { id: 39, content: "你喜欢把事情决定下来", dimension: "JP", direction: 1 },
  { id: 40, content: "你愿意保持选择的开放性", dimension: "JP", direction: -1 },
];

// 16 种性格类型描述
const personalityTypes = [
  {
    type_code: "ISTJ",
    type_name: "物流师",
    description: "务实、注重事实，具有强烈的责任感。你可靠、有条理，善于将想法转化为实际行动。",
    strengths: "诚实可靠、意志坚定、冷静务实、善于管理事务",
    weaknesses: "固执、过于传统、情感表达困难、容易过度工作",
    career_suggestions: "会计、审计、项目管理、行政管理、法律工作"
  },
  {
    type_code: "ISFJ",
    type_name: "守卫者",
    description: "温暖、有爱心，善于照顾他人。你重视和谐，愿意为他人付出，是可靠的伙伴。",
    strengths: "支持他人、耐心细致、忠诚可靠、观察力强",
    weaknesses: "过度谦虚、难以拒绝他人、压抑情感、抗拒变化",
    career_suggestions: "护理、教育、人力资源、客户服务、社会工作"
  },
  {
    type_code: "INFJ",
    type_name: "提倡者",
    description: "富有洞察力、理想主义，追求深层次的意义。你理解他人，有强烈的价值观。",
    strengths: "富有创造力、洞察力强、有原则、热情",
    weaknesses: "完美主义、容易倦怠、过于私密、敏感",
    career_suggestions: "心理咨询、写作、艺术、非营利组织、研究"
  },
  {
    type_code: "INTJ",
    type_name: "建筑师",
    description: "战略思维者，独立且有远见。你善于分析复杂问题，制定长期计划。",
    strengths: "战略思维、独立、决心强、知识渊博",
    weaknesses: "傲慢、情感表达困难、过度分析、批判性强",
    career_suggestions: "战略规划、科学研究、软件开发、投资分析"
  },
  {
    type_code: "ISTP",
    type_name: "鉴赏家",
    description: "灵活、实用，善于解决具体问题。你喜欢动手操作，享受当下的体验。",
    strengths: "乐观、精力充沛、创造力强、理性",
    weaknesses: "顽固、冒险、缺乏耐心、难以承诺",
    career_suggestions: "工程师、技术员、运动员、手工艺、紧急救援"
  },
  {
    type_code: "ISFP",
    type_name: "探险家",
    description: "艺术气质、敏感，善于欣赏美。你活在当下，追求真实和自我表达。",
    strengths: "有魅力、敏感、想象力丰富、热情",
    weaknesses: "过度独立、难以预测、容易倦怠、缺乏长远规划",
    career_suggestions: "艺术设计、音乐、摄影、护理、园艺"
  },
  {
    type_code: "INFP",
    type_name: "调停者",
    description: "理想主义、富有同情心，追求真实和意义。你重视价值观，善于理解他人。",
    strengths: "富有同情心、开放思维、创造力强、热情",
    weaknesses: "不切实际、自我隔离、情感化、缺乏条理",
    career_suggestions: "写作、心理咨询、艺术、教育、社会服务"
  },
  {
    type_code: "INTP",
    type_name: "逻辑学家",
    description: "好奇心强、善于分析，追求知识和真理。你喜欢探索抽象概念和理论。",
    strengths: "分析能力强、客观、富有想象力、诚实",
    weaknesses: "社交困难、自我怀疑、完美主义、脱离实际",
    career_suggestions: "科学研究、编程、哲学、数据分析、学术"
  },
  {
    type_code: "ESTP",
    type_name: "企业家",
    description: "精力充沛、善于感知，享受行动和冒险。你活在当下，善于应对变化。",
    strengths: "大胆、理性、原创、善于社交",
    weaknesses: "不耐烦、冒险、缺乏敏感、难以坚持",
    career_suggestions: "销售、创业、体育、执法、紧急救援"
  },
  {
    type_code: "ESFP",
    type_name: "表演者",
    description: "热情、活泼，善于带动气氛。你享受当下，喜欢与人互动。",
    strengths: "大胆、原创、审美、表演天赋",
    weaknesses: "敏感、冲突回避、缺乏规划、容易厌倦",
    career_suggestions: "演艺、销售、活动策划、旅游、公关"
  },
  {
    type_code: "ENFP",
    type_name: "竞选者",
    description: "热情、有创造力，善于激发他人。你充满可能性，追求自由和成长。",
    strengths: "好奇心强、观察力强、热情、善于社交",
    weaknesses: "过度思考、精力分散、情感化、缺乏条理",
    career_suggestions: "创意工作、咨询、教学、创业、媒体"
  },
  {
    type_code: "ENTP",
    type_name: "辩论家",
    description: "聪明、好奇，善于挑战传统思维。你喜欢智力游戏和创新。",
    strengths: "知识渊博、思维敏捷、原创、魅力",
    weaknesses: "好争论、缺乏敏感、难以专注、傲慢",
    career_suggestions: "创业、法律、咨询、科研、市场营销"
  },
  {
    type_code: "ESTJ",
    type_name: "总经理",
    description: "高效、有条理，善于管理和执行。你重视传统和秩序，是天然的领导者。",
    strengths: "奉献、有组织、诚实、果断",
    weaknesses: "固执、缺乏变通、过于评判、难以放松",
    career_suggestions: "管理、行政、金融、法律、军事"
  },
  {
    type_code: "ESFJ",
    type_name: "执政官",
    description: "热心、负责任，善于照顾他人。你重视和谐，是团队中的粘合剂。",
    strengths: "实用、忠诚、敏感、善于社交",
    weaknesses: "过度关心他人、自我价值感低、僵化、压抑情感",
    career_suggestions: "人力资源、教育、医疗、客户服务、管理"
  },
  {
    type_code: "ENFJ",
    type_name: "主人公",
    description: "有魅力、有领导力，善于激励他人。你关心他人成长，是天然的导师。",
    strengths: "宽容、可靠、有魅力、利他",
    weaknesses: "过度理想化、自我价值感低、过于顺从、难以做艰难决定",
    career_suggestions: "教育、咨询、人力资源、销售、非营利组织"
  },
  {
    type_code: "ENTJ",
    type_name: "指挥官",
    description: "果断、有战略眼光，善于领导和组织。你追求效率，是天生的领导者。",
    strengths: "高效、精力充沛、自信、意志坚定",
    weaknesses: "固执、傲慢、缺乏耐心、情感表达困难",
    career_suggestions: "高管、创业、管理咨询、法律、政治"
  }
];

// 保存数据
fs.writeFileSync(path.join(DATA_DIR, 'questions.json'), JSON.stringify(questions, null, 2), 'utf8');
fs.writeFileSync(path.join(DATA_DIR, 'types.json'), JSON.stringify(personalityTypes, null, 2), 'utf8');
fs.writeFileSync(path.join(DATA_DIR, 'results.json'), JSON.stringify([], null, 2), 'utf8');

console.log('✅ 数据库初始化完成！');
console.log(`📊 题目数量：${questions.length}`);
console.log(`🎭 性格类型：${personalityTypes.length}`);
console.log(`📁 数据文件：${DATA_DIR}`);

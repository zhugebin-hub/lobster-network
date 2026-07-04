const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const DATA_DIR = path.join(__dirname, 'data');
const TESTS_FILE = path.join(DATA_DIR, 'tests.json');
const RESULTS_FILE = path.join(DATA_DIR, 'results.json');

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}
if (!fs.existsSync(TESTS_FILE)) {
  fs.writeFileSync(TESTS_FILE, '[]');
}
if (!fs.existsSync(RESULTS_FILE)) {
  fs.writeFileSync(RESULTS_FILE, '[]');
}

function readTests() { return JSON.parse(fs.readFileSync(TESTS_FILE, 'utf8')); }
function readResults() { return JSON.parse(fs.readFileSync(RESULTS_FILE, 'utf8')); }
function writeTests(t) { fs.writeFileSync(TESTS_FILE, JSON.stringify(t, null, 2)); }
function writeResults(r) { fs.writeFileSync(RESULTS_FILE, JSON.stringify(r, null, 2)); }

// ========== 心理健康量表 ==========
const mentalHealthTests = [
  {
    id: 'phq9',
    name: 'PHQ-9 抑郁症筛查量表',
    description: '用于评估过去两周内抑郁症状的严重程度',
    category: '抑郁',
    icon: '😔',
    questions: [
      { id: 1, text: '做事时提不起劲或没有兴趣', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 2, text: '感到心情低落、沮丧或绝望', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 3, text: '入睡困难、睡不安稳或睡眠过多', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 4, text: '感觉疲倦或没有活力', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 5, text: '食欲不振或吃太多', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 6, text: '觉得自己很糟糕，或觉得自己很失败，让自己或家人失望', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 7, text: '对事物专注有困难，例如看报纸或看电视时', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 8, text: '动作或说话速度缓慢到别人可以觉察，或正好相反，烦躁或坐立不安', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 9, text: '有不如死掉或用某种方式伤害自己的念头', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 4, level: '没有抑郁', color: '#28a745', advice: '🌟 你的心理状态良好！继续保持积极的生活方式，规律作息、适度运动、保持社交。建议每天花些时间做让自己开心的事情，与亲友保持联系。' },
        { max: 9, level: '轻度抑郁', color: '#ffc107', advice: '🌤️ 你有一些轻度抑郁症状。建议：1）保持规律作息和充足睡眠；2）每天进行30分钟有氧运动；3）多与亲友交流；4）尝试正念冥想放松自己；5）如果症状持续超过两周，建议寻求专业心理咨询。' },
        { max: 14, level: '中度抑郁', color: '#fd7e14', advice: '🌥️ 你的抑郁症状已经达到中度水平，需要重视。建议：1）尽快预约心理咨询师进行专业评估；2）保持规律的日常生活节奏；3）避免独自长时间待着；4）适度运动有助于改善情绪；5）可以尝试写情绪日记记录自己的感受。' },
        { max: 19, level: '中重度抑郁', color: '#dc3545', advice: '⚠️ 你的抑郁症状较重，强烈建议尽快寻求专业帮助。建议：1）立即预约精神科医生或心理咨询师；2）告诉信任的家人或朋友你的感受；3）避免做出重大决定；4）每天尽量保持基本的生活规律；5）如有自伤想法，请立即拨打心理援助热线：400-161-9995。' },
        { max: 27, level: '重度抑郁', color: '#721c24', advice: '🚨 你的抑郁症状非常严重，请立即寻求专业医疗帮助。建议：1）尽快前往医院精神科就诊；2）告诉家人或朋友你需要帮助；3）拨打心理危机干预热线：北京 010-82951332，全国 400-161-9995；4）不要独自承受，你并不孤单；5）记住，抑郁症是可以治疗的，寻求帮助是勇敢的表现。' }
      ]
    }
  },
  {
    id: 'gad7',
    name: 'GAD-7 焦虑症筛查量表',
    description: '用于评估过去两周内焦虑症状的严重程度',
    category: '焦虑',
    icon: '😰',
    questions: [
      { id: 1, text: '感觉紧张、焦虑或急切', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 2, text: '不能够停止或控制担忧', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 3, text: '对各种各样的事情担忧过多', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 4, text: '很难静下心来', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 5, text: 'Restless（坐立不安），以至于很难静下来', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 6, text: '变得容易烦恼或急躁', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] },
      { id: 7, text: '感到似乎将有可怕的事情发生', options: ['完全不会', '好几天', '一半以上的天数', '几乎每天'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 4, level: '没有焦虑', color: '#28a745', advice: '🌟 你的焦虑水平正常！继续保持轻松的心态，享受生活中的美好。建议保持运动习惯和良好社交，这些都是维持心理健康的好方法。' },
        { max: 9, level: '轻度焦虑', color: '#ffc107', advice: '🌤️ 你有轻度焦虑感，这是很常见的。建议：1）每天进行深呼吸练习（腹式呼吸）；2）减少咖啡因摄入；3）保持规律运动；4）尝试写"担忧日记"，把担心的事写下来并理性分析；5）学习放松技巧如渐进性肌肉放松。' },
        { max: 14, level: '中度焦虑', color: '#fd7e14', advice: '🌥️ 你的焦虑程度已经达到中度，需要关注。建议：1）预约心理咨询师进行专业评估；2）学习正念冥想，每天10-15分钟；3）减少信息过载，适当远离社交媒体；4）建立固定的放松时间；5）避免用酒精或药物来缓解焦虑。' },
        { max: 21, level: '重度焦虑', color: '#dc3545', advice: '⚠️ 你的焦虑症状较重，已经可能影响到日常生活。强烈建议：1）尽快寻求精神科医生或心理咨询师的帮助；2）学习 grounding 技巧（如5-4-3-2-1感官法）来应对急性焦虑；3）告诉信任的人你的状况；4）拨打心理援助热线：400-161-9995。记住，焦虑症是可以有效治疗的。' }
      ]
    }
  },
  {
    id: 'psqi',
    name: '睡眠质量评估',
    description: '评估你的睡眠质量和可能存在的睡眠问题',
    category: '睡眠',
    icon: '😴',
    questions: [
      { id: 1, text: '你通常多久才能入睡？', options: ['30分钟以内', '31-60分钟', '61-90分钟', '超过90分钟'], scores: [0, 1, 2, 3] },
      { id: 2, text: '你在夜间睡眠中是否经常醒来？', options: ['从不', '偶尔（每周1-2次）', '有时（每周3-4次）', '经常（每周5次以上）'], scores: [0, 1, 2, 3] },
      { id: 3, text: '你早上醒来后感觉如何？', options: ['精神饱满', '比较精神', '有些疲倦', '非常疲倦'], scores: [0, 1, 2, 3] },
      { id: 4, text: '白天你是否经常感到困倦？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] },
      { id: 5, text: '你的睡眠环境是否安静舒适？', options: ['非常舒适', '比较舒适', '一般', '不太舒适'], scores: [0, 1, 2, 3] },
      { id: 6, text: '睡前你是否经常使用手机或电脑？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] },
      { id: 7, text: '你是否需要依赖药物或酒精才能入睡？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 5, level: '睡眠质量良好', color: '#28a745', advice: '🌙 你的睡眠质量很好！继续保持：1）保持固定的作息时间；2）睡前避免剧烈运动；3）保持卧室温度适宜（18-22℃）；4）睡前可以泡个热水脚或喝温牛奶。' },
        { max: 10, level: '轻度睡眠问题', color: '#ffc107', advice: '🌤️ 你的睡眠有一些小问题。建议：1）建立固定的睡前仪式（如阅读、听轻音乐）；2）睡前1小时远离电子屏幕；3）下午3点后避免咖啡因；4）白天适度运动有助于夜间睡眠；5）卧室保持黑暗和安静。' },
        { max: 15, level: '中度睡眠问题', color: '#fd7e14', advice: '🌥️ 你的睡眠问题需要重视。建议：1）建立严格的作息时间表，包括周末；2）睡前进行放松练习（渐进性肌肉放松或冥想）；3）如果躺下20分钟无法入睡，起来做放松活动；4）减少午睡时间（不超过30分钟）；5）如持续失眠，建议就诊睡眠专科。' },
        { max: 21, level: '严重睡眠障碍', color: '#dc3545', advice: '⚠️ 你的睡眠问题较为严重，已影响健康。建议：1）尽快就诊睡眠专科或精神科；2）记录一周的睡眠日记；3）避免自行服用安眠药；4）白天尽量接触自然光照；5）建立"床只用于睡觉"的条件反射。良好的睡眠是心理健康的基础，请认真对待。' }
      ]
    }
  },
  {
    id: 'stress',
    name: '压力水平评估',
    description: '评估你当前承受的压力程度及应对能力',
    category: '压力',
    icon: '😤',
    questions: [
      { id: 1, text: '你感到无法控制生活中重要的事情吗？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] },
      { id: 2, text: '你感到事情按照你的意愿发展吗？', options: ['总是', '经常', '有时', '从不'], scores: [3, 2, 1, 0] },
      { id: 3, text: '你感到紧张或有压力吗？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] },
      { id: 4, text: '你觉得能够有效地处理生活中的烦心事吗？', options: ['总是', '经常', '有时', '从不'], scores: [3, 2, 1, 0] },
      { id: 5, text: '你感到事情堆积如山，无法应对吗？', options: ['从不', '偶尔', '有时', '经常'], scores: [0, 1, 2, 3] },
      { id: 6, text: '你的身体健康状况如何？', options: ['很好', '较好', '一般', '较差'], scores: [0, 1, 2, 3] },
      { id: 7, text: '你有可以倾诉心事的人吗？', options: ['有很多', '有几个', '很少', '几乎没有'], scores: [0, 1, 2, 3] },
      { id: 8, text: '你是否有足够的时间做自己喜欢的事？', options: ['总是有', '经常有', '偶尔有', '几乎没有'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 7, level: '压力水平正常', color: '#28a745', advice: '💪 你的压力水平在正常范围内，应对能力良好！继续保持：1）维持现有的健康生活方式；2）保持社交活动；3）培养兴趣爱好；4）学会适度放松。良好的压力管理是你的一大优势。' },
        { max: 14, level: '轻度压力', color: '#ffc107', advice: '🌤️ 你承受着一些压力，但仍在可控范围内。建议：1）识别主要压力来源；2）学习时间管理技巧，合理分配任务；3）每天安排15分钟"自我时间"；4）练习深呼吸和放松技巧；5）与亲友分享你的感受。' },
        { max: 20, level: '中度压力', color: '#fd7e14', advice: '🌥️ 你的压力水平较高，需要积极管理。建议：1）列出压力源并按可控性排序；2）学会说"不"，减少不必要的负担；3）每天至少30分钟运动；4）练习正念冥想；5）考虑寻求心理咨询；6）保证充足的睡眠时间。' },
        { max: 24, level: '重度压力', color: '#dc3545', advice: '⚠️ 你承受着极大的压力，已经可能影响到身心健康。强烈建议：1）立即寻求专业心理咨询；2）重新评估当前的生活安排，做出必要调整；3）每天保证基本的生活需求（饮食、睡眠）；4）与信任的人分享你的困境；5）拨打心理援助热线：400-161-9995。请记住，寻求帮助是明智的选择。' }
      ]
    }
  },
  {
    id: 'self-esteem',
    name: '自尊水平评估（Rosenberg量表）',
    description: '评估你的自我价值感和自尊水平',
    category: '自尊',
    icon: '🪞',
    questions: [
      { id: 1, text: '我总体上对自己感到满意', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 2, text: '我觉得自己有一些值得骄傲的品质', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 3, text: '我觉得自己是个有价值的人', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 4, text: '我能够像大多数人一样把事情做好', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 5, text: '我对自己持积极态度', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 6, text: '我经常拿自己的短处和别人的长处比较', options: ['非常符合', '比较符合', '比较不符合', '非常不符合'], scores: [0, 1, 2, 3] },
      { id: 7, text: '我对自己 overall 的发展感到满意', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 8, text: '我相信自己是一个值得被爱的人', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 7, level: '自尊水平较低', color: '#dc3545', advice: '💗 你的自尊水平偏低，这可能会影响你的心理健康。建议：1）每天记录3件自己做得好的事；2）停止与别人比较，关注自己的成长；3）练习自我同情，像对待朋友一样对待自己；4）挑战消极的自我对话；5）培养一个能带来成就感的爱好；6）考虑寻求心理咨询帮助提升自我价值感。' },
        { max: 14, level: '自尊水平一般', color: '#ffc107', advice: '🌤️ 你的自尊水平处于中等，有提升空间。建议：1）每天对自己说一些鼓励的话；2）设定小目标并庆祝达成；3）关注自己的优点而非缺点；4）减少社交媒体上与他人比较的时间；5）学会接受赞美；6）培养自我接纳的态度。' },
        { max: 21, level: '自尊水平良好', color: '#28a745', advice: '🌟 你的自尊水平良好，能够积极地看待自己！继续保持：1）保持对自己的客观评价；2）在自信的同时保持谦逊；3）帮助他人提升自尊；4）面对挫折时保持积极的自我对话。良好的自尊是心理健康的重要基石。' },
        { max: 24, level: '自尊水平很高', color: '#28a745', advice: '🌟 你的自尊水平很高，对自己有积极的认知！继续保持健康的心态，同时注意：1）保持谦逊和开放的心态；2）接纳自己的不完美；3）在自信的同时也要学会倾听他人的意见。' }
      ]
    }
  },
  {
    id: 'social',
    name: '社交能力评估',
    description: '评估你的社交能力和人际关系状况',
    category: '社交',
    icon: '👥',
    questions: [
      { id: 1, text: '我在社交场合感到自在和放松', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 2, text: '我能够轻松地与陌生人开始对话', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 3, text: '我有可以信赖的朋友', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 4, text: '我害怕在众人面前说话或表现', options: ['非常符合', '比较符合', '比较不符合', '非常不符合'], scores: [0, 1, 2, 3] },
      { id: 5, text: '我能够表达自己的想法和感受', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] },
      { id: 6, text: '我担心别人对我的评价', options: ['非常符合', '比较符合', '比较不符合', '非常不符合'], scores: [0, 1, 2, 3] },
      { id: 7, text: '我能够处理人际冲突', options: ['非常不符合', '比较不符合', '比较符合', '非常符合'], scores: [0, 1, 2, 3] }
    ],
    scoring: {
      levels: [
        { max: 7, level: '社交困难', color: '#dc3545', advice: '💗 你在社交方面面临一些挑战。建议：1）从小的社交互动开始（如和邻居打招呼）；2）参加兴趣小组或社团活动；3）练习社交技巧，可以从角色扮演开始；4）记住大多数人都是友善的；5）考虑参加社交技能训练课程；6）寻求心理咨询师的帮助。' },
        { max: 14, level: '社交能力一般', color: '#ffc107', advice: '🌤️ 你的社交能力处于中等水平。建议：1）主动参加一些社交活动；2）练习倾听技巧，这是建立关系的关键；3）尝试主动发起对话；4）参加志愿活动是认识新朋友的好方式；5）学会在社交中设定健康的边界。' },
        { max: 21, level: '社交能力良好', color: '#28a745', advice: '🌟 你的社交能力良好，能够较好地与他人互动！继续保持：1）维护好现有的友谊；2）拓展社交圈子；3）学会在社交中保持真实自我；4）帮助那些在社交方面有困难的人。良好的人际关系是幸福的重要来源。' },
        { max: 21, level: '社交能力优秀', color: '#28a745', advice: '🌟 你的社交能力非常出色！你善于与人交往，人际关系良好。建议：1）利用你的社交能力帮助他人；2）在社交中保持真诚；3）注意平衡社交和个人时间；4）继续学习沟通技巧。' }
      ]
    }
  }
];

// 初始化量表数据
function initTests() {
  const existingTests = readTests();
  if (existingTests.length === 0) {
    writeTests(mentalHealthTests);
    console.log('✅ 心理健康量表初始化完成，共 ' + mentalHealthTests.length + ' 个量表');
  } else {
    console.log('📋 量表已存在，共 ' + existingTests.length + ' 个');
  }
}

// 获取所有量表
app.get('/api/tests', (req, res) => {
  res.json(readTests());
});

// 获取单个量表详情
app.get('/api/tests/:id', (req, res) => {
  const tests = readTests();
  const test = tests.find(t => t.id === req.params.id);
  if (!test) return res.status(404).json({ error: '量表不存在' });
  res.json(test);
});

// 提交测试结果
app.post('/api/results', (req, res) => {
  const { user_name, test_id, test_name, answers, total_score, level, advice } = req.body;
  const results = readResults();
  const newResult = {
    id: Date.now(),
    user_name,
    test_id,
    test_name,
    answers,
    total_score,
    level,
    advice,
    created_at: new Date().toISOString()
  };
  results.push(newResult);
  writeResults(results);
  res.json({ success: true, result: newResult });
});

// 获取所有结果
app.get('/api/results', (req, res) => {
  const { user_name, test_id } = req.query;
  let results = readResults();
  if (user_name) results = results.filter(r => r.user_name === user_name);
  if (test_id) results = results.filter(r => r.test_id === test_id);
  results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  res.json(results);
});

// 删除结果
app.delete('/api/results/:id', (req, res) => {
  let results = readResults();
  results = results.filter(r => r.id !== parseInt(req.params.id));
  writeResults(results);
  res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
initTests();
app.listen(PORT, () => {
  console.log(`🧠 心理健康测试系统已启动：http://localhost:${PORT}`);
  console.log(`📁 数据目录：${DATA_DIR}`);
});

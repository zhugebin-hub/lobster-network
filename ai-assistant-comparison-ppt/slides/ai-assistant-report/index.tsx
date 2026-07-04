import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

export const design: DesignSystem = {
  palette: { bg: '#0b1120', text: '#f1f5f9', accent: '#3b82f6' },
  fonts: {
    display: 'system-ui, -apple-system, sans-serif',
    body: 'system-ui, -apple-system, sans-serif',
  },
  typeScale: { hero: 160, body: 36 },
  radius: 12,
};

const accent = '#3b82f6';
const accentLight = '#60a5fa';
const muted = '#94a3b8';
const dimBg = 'rgba(255,255,255,0.04)';
const dimBorder = 'rgba(255,255,255,0.08)';

const fill = {
  width: '100%',
  height: '100%',
  fontFamily: 'var(--osd-font-body)',
} as const;

const EASE_OUT = 'cubic-bezier(0, 0, 0.2, 1)';
const EASE_IN = 'cubic-bezier(0.4, 0, 1, 1)';

export const transition = {
  duration: 200,
  exit: { duration: 140, easing: EASE_IN, keyframes: [
    { opacity: 1, transform: 'translateY(0)' },
    { opacity: 0, transform: 'translateY(-4px)' },
  ] },
  enter: { duration: 200, delay: 80, easing: EASE_OUT, keyframes: [
    { opacity: 0, transform: 'translateY(6px)' },
    { opacity: 1, transform: 'translateY(0)' },
  ] },
};

// ===== COVER =====
const Cover: Page = () => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '0 160px',
  }}>
    <div style={{
      fontSize: 24,
      color: accent,
      letterSpacing: '0.25em',
      fontWeight: 600,
      marginBottom: 40,
    }}>
      2026 年度深度分析报告
    </div>
    <h1 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 'var(--osd-size-hero)',
      fontWeight: 900,
      lineHeight: 1.1,
      margin: '0 0 40px 0',
      letterSpacing: '-0.02em',
    }}>
      主流 AI 助手<br />
      <span style={{ color: accent }}>性能深度比较</span>
    </h1>
    <p style={{
      fontSize: 'var(--osd-size-body)',
      color: muted,
      lineHeight: 1.6,
      maxWidth: 900,
    }}>
      覆盖 Claude · ChatGPT · Gemini · 通义千问 · DeepSeek<br />
      智能水平 · 推理能力 · 编程 · 多模态 · 中文能力 · 性价比
    </p>
    <div style={{
      marginTop: 64,
      display: 'flex',
      gap: 48,
      alignItems: 'center',
    }}>
      <span style={{ fontSize: 24, color: muted }}>编制：戴建华</span>
      <span style={{ fontSize: 24, color: 'rgba(255,255,255,0.15)' }}>|</span>
      <span style={{ fontSize: 24, color: muted }}>2026年6月</span>
    </div>
  </div>
);

Cover.transition = {
  duration: 280,
  exit: { duration: 160, easing: EASE_IN, keyframes: [
    { opacity: 1, transform: 'translateY(0)' },
    { opacity: 0, transform: 'translateY(-6px)' },
  ] },
  enter: { duration: 280, delay: 100, easing: EASE_OUT, keyframes: [
    { opacity: 0, transform: 'translateY(12px)', filter: 'blur(4px)' },
    { opacity: 1, transform: 'translateY(0)', filter: 'blur(0)' },
  ] },
};

// ===== SECTION DIVIDER =====
const Divider: Page = ({ title, num }: { title: string; num: string }) => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '0 160px',
  }}>
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', marginBottom: 32 }}>{num}</div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 120,
      fontWeight: 900,
      lineHeight: 1.1,
      margin: 0,
    }}>{title}</h2>
  </div>
);

// ===== CONTENT PAGE =====
const Content: Page = ({ heading, bullets, accentNum }: {
  heading: string;
  bullets: string[];
  accentNum?: string;
}) => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    padding: 120,
    display: 'flex',
    flexDirection: 'column',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 64,
      fontWeight: 800,
      margin: 0,
      lineHeight: 1.2,
    }}>{heading}</h2>
    {accentNum && (
      <div style={{ fontSize: 80, fontWeight: 900, color: accent, marginTop: 32, lineHeight: 1 }}>
        {accentNum}
      </div>
    )}
    <ul style={{
      fontSize: 36,
      lineHeight: 1.7,
      marginTop: accentNum ? 48 : 64,
      paddingLeft: 32,
      color: '#cbd5e1',
    }}>
      {bullets.map((b, i) => (
        <li key={i} style={{ marginBottom: 16 }}>{b}</li>
      ))}
    </ul>
  </div>
);

// ===== TABLE PAGE =====
const TablePage: Page = ({ heading, cols, rows }: {
  heading: string;
  cols: string[];
  rows: string[][];
}) => {
  const colW = Math.floor((1680) / cols.length);
  return (
    <div style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: 'var(--osd-text)',
      padding: 100,
      display: 'flex',
      flexDirection: 'column',
    }}>
      <h2 style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 52,
        fontWeight: 800,
        margin: '0 0 48px 0',
      }}>{heading}</h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: cols.map(() => `${colW}px`).join(' '),
        gap: 0,
        fontSize: 28,
        borderRadius: 12,
        overflow: 'hidden',
        border: `1px solid ${dimBorder}`,
      }}>
        {/* Header */}
        {cols.map((c, i) => (
          <div key={i} style={{
            padding: '16px 20px',
            fontWeight: 700,
            color: accent,
            background: dimBg,
            borderBottom: `1px solid ${dimBorder}`,
          }}>{c}</div>
        ))}
        {/* Rows */}
        {rows.map((row, ri) =>
          row.map((cell, ci) => (
            <div key={`${ri}-${ci}`} style={{
              padding: '12px 20px',
              color: ci === 0 ? '#e2e8f0' : '#cbd5e1',
              background: ri % 2 === 0 ? 'transparent' : dimBg,
              borderBottom: `1px solid ${dimBorder}`,
              fontSize: ri === 0 ? 28 : 26,
            }}>{cell}</div>
          ))
        )}
      </div>
    </div>
  );
};

// ===== COMPARISON CARDS =====
const CardRow: Page = ({ heading, cards }: {
  heading: string;
  cards: { label: string; value: string; color?: string }[];
}) => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    padding: 120,
    display: 'flex',
    flexDirection: 'column',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 56,
      fontWeight: 800,
      margin: '0 0 56px 0',
    }}>{heading}</h2>
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${cards.length}, 1fr)`,
      gap: 32,
    }}>
      {cards.map((c, i) => (
        <div key={i} style={{
          background: dimBg,
          border: `1px solid ${dimBorder}`,
          borderRadius: 16,
          padding: '32px 28px',
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}>
          <div style={{
            fontSize: 24,
            color: muted,
            fontWeight: 600,
            letterSpacing: '0.05em',
          }}>{c.label}</div>
          <div style={{
            fontSize: 40,
            fontWeight: 900,
            color: c.color || accent,
            lineHeight: 1.2,
          }}>{c.value}</div>
        </div>
      ))}
    </div>
  </div>
);

// ===== SLIDES =====
const Agenda: Page = () => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    padding: 120,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 72,
      fontWeight: 900,
      margin: '0 0 64px 0',
    }}>报告目录</h2>
    {[
      '智能水平综合排名',
      '推理与知识能力',
      'Agentic 智能体能力',
      '编程能力对比',
      '多模态能力（图像/视频）',
      '速度与延迟',
      '价格与性价比',
      '中文能力专项评估',
      '适用场景推荐',
      '关键趋势洞察',
    ].map((item, i) => (
      <div key={i} style={{
        display: 'flex',
        alignItems: 'center',
        gap: 32,
        padding: '20px 0',
        borderBottom: `1px solid ${dimBorder}`,
      }}>
        <span style={{
          fontSize: 28,
          fontWeight: 800,
          color: accent,
          width: 48,
          textAlign: 'right',
        }}>{String(i + 1).padStart(2, '0')}</span>
        <span style={{ fontSize: 36, color: '#cbd5e1' }}>{item}</span>
      </div>
    ))}
  </div>
);

// ===== SUMMARY PAGE =====
const Summary: Page = () => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    padding: 120,
    display: 'flex',
    flexDirection: 'column',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 64,
      fontWeight: 900,
      margin: '0 0 48px 0',
    }}>总结与选型建议</h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {[
        { scenario: '追求最强智能', pick: 'Claude Fable 5 / Opus 4.8', note: 'Intelligence Index 排名第1、2' },
        { scenario: '预算有限', pick: 'DeepSeek V4 Pro / Qwen3.7 Plus', note: '智能够用，价格仅 Claude 的 1/50' },
        { scenario: '多模态需求', pick: 'Gemini 2.5 Pro', note: '图像/视频理解绝对领先' },
        { scenario: '中文场景', pick: '通义千问', note: '中文理解生成最优' },
        { scenario: '日常通用', pick: 'GPT-5.5', note: '综合能力均衡，生态最成熟' },
      ].map((item, i) => (
        <div key={i} style={{
          display: 'flex',
          gap: 32,
          alignItems: 'baseline',
          padding: '20px 24px',
          background: dimBg,
          borderRadius: 12,
          border: `1px solid ${dimBorder}`,
        }}>
          <span style={{ fontSize: 28, color: accent, fontWeight: 700, minWidth: 140 }}>{item.scenario}</span>
          <span style={{ fontSize: 36, fontWeight: 800, color: '#f1f5f9' }}>{item.pick}</span>
          <span style={{ fontSize: 28, color: muted, marginLeft: 'auto' }}>{item.note}</span>
        </div>
      ))}
    </div>
  </div>
);

// ===== ENDING =====
const Ending: Page = () => (
  <div style={{
    ...fill,
    background: 'var(--osd-bg)',
    color: 'var(--osd-text)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '0 160px',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 100,
      fontWeight: 900,
      margin: '0 0 32px 0',
      textAlign: 'center',
    }}>感谢阅读</h2>
    <p style={{
      fontSize: 36,
      color: muted,
      textAlign: 'center',
      lineHeight: 1.8,
    }}>
      主流AI助手性能深度比较分析报告<br />
      编制：戴建华 · 2026年6月
    </p>
    <div style={{
      marginTop: 64,
      fontSize: 24,
      color: 'rgba(255,255,255,0.2)',
    }}>
      数据来源：Artificial Analysis · LMSYS Chatbot Arena · 各厂商官方文档
    </div>
  </div>
);

Ending.transition = {
  duration: 280,
  exit: { duration: 160, easing: EASE_IN, keyframes: [
    { opacity: 1, transform: 'translateY(0)' },
    { opacity: 0, transform: 'translateY(-6px)' },
  ] },
  enter: { duration: 280, delay: 100, easing: EASE_OUT, keyframes: [
    { opacity: 0, transform: 'translateY(12px)', filter: 'blur(4px)' },
    { opacity: 1, transform: 'translateY(0)', filter: 'blur(0)' },
  ] },
};

export const meta: SlideMeta = {
  title: 'AI助手性能比较分析报告',
  createdAt: '2026-06-15T07:33:12.860Z',
};

export default [
  Cover,
  Agenda,
  // Section 1
  () => <Divider num="01" title="智能水平综合排名" />,
  () => <Content
    heading="AI 智能水平排名"
    accentNum="🥇 Claude Fable 5: 64.9"
    bullets={[
      'Claude Fable 5 — 64.9分，10项基准中5项第一，领先第二名近5分',
      'Claude Opus 4.8 — 约60分，科学推理与长上下文推理卓越',
      'GPT-5.5 (xhigh) — 约55分，指令遵循与通用任务能力强',
      'Gemini 2.5 Pro — 约52分，视觉推理（MMMU-Pro）领先',
      'Qwen3.7 Plus — 约45分，中文理解最优，性价比极高',
      'DeepSeek V4 Pro — 约43分，代码生成（SciCode）突出',
    ]}
  />,
  () => <Content
    heading="关键发现"
    bullets={[
      'Anthropic 包揽前两名，是近年来最大单代性能跳跃',
      'Claude Fable 5 引入"自适应推理"机制',
      '安全审查时自动降级到 Opus 4.8（fallback 约8%任务）',
      'HLE（人类最终考试）得分53%，领先第二名7个以上百分点',
    ]}
  />,
  // Section 2
  () => <Divider num="02" title="推理与知识能力" />,
  () => <TablePage
    heading="推理与知识能力对比"
    cols={['基准测试', 'Claude F5', 'GPT-5.5', 'Gemini 2.5', 'Qwen 3.7', 'DeepSeek V4']}
    rows={[
      ['Humanity Last Exam', '53% 🏆', '38%', '40%', '28%', '30%'],
      ['GPQA 科学推理', '领先 🏆', '次优', '第三', '中等', '中等'],
      ['AA-Omniscience', '40 🏆', '33', '35', '28', '25'],
      ['长上下文推理', '领先 🏆', '优秀', '优秀', '良好', '良好'],
    ]}
  />,
  // Section 3
  () => <Divider num="03" title="Agentic 智能体能力" />,
  () => <CardRow
    heading="Agentic 能力：真实工作 Elo 评分"
    cards={[
      { label: 'Claude Fable 5', value: 'Elo 1932 🏆', color: '#3b82f6' },
      { label: 'GPT-5.5', value: 'Elo ~1850' },
      { label: 'Gemini 2.5 Pro', value: 'Elo ~1820' },
      { label: 'Qwen 3.7 Plus', value: 'Elo ~1750' },
      { label: 'DeepSeek V4 Pro', value: 'Elo ~1780' },
    ]}
  />,
  () => <Content
    heading="Agentic 能力关键发现"
    bullets={[
      'Claude 在 Agentic 能力上拉开显著差距',
      'GDPval-AA（真实工作）得分比 Opus 4.8 大幅提升',
      'Terminal-Bench Hard（终端编程）Claude 领先',
      'τ²-Bench Telecom（工具调用）Claude 领先',
      '2026年竞争焦点已从"回答问题"转向"完成任务"',
    ]}
  />,
  // Section 4
  () => <Divider num="04" title="编程能力" />,
  () => <CardRow
    heading="编程能力对比"
    cards={[
      { label: 'Claude Fable 5', value: '最优 🏆', color: '#3b82f6' },
      { label: 'GPT-5.5', value: '最优', color: '#3b82f6' },
      { label: 'Gemini 2.5 Pro', value: '优秀' },
      { label: 'Qwen 3.7 Plus', value: '良好' },
      { label: 'DeepSeek V4 Pro', value: '优秀 🌟', color: '#10b981' },
    ]}
  />,
  () => <Content
    heading="编程能力亮点"
    bullets={[
      'Claude 和 GPT-5.5 在代码生成质量上并列最优',
      'DeepSeek 表现超出综合排名，开发者高性价比之选',
      'SciCode 代码评测：Claude 领先，DeepSeek 同级竞争',
      '代码理解与调试：Claude 最优，GPT/DeepSeek/Gemini 优秀',
    ]}
  />,
  // Section 5
  () => <Divider num="05" title="多模态能力" />,
  () => <TablePage
    heading="多模态能力对比"
    cols={['能力', 'Gemini', 'GPT-5.5', 'Claude', 'Qwen', 'DeepSeek']}
    rows={[
      ['图像理解', '最强 🏆', '优秀', '优秀', '良好', '弱'],
      ['图像生成', '优秀', 'DALL-E', '无', '有', '无'],
      ['视频理解', '最强 🏆', '优秀', '有', '有', '弱'],
      ['视觉推理', '第一 🏆', '第二', '第三', '第四', '—'],
    ]}
  />,
  () => <Content
    heading="多模态领域格局"
    bullets={[
      'Gemini 在多模态领域保持绝对领先',
      'Google 的多模态训练数据优势显著',
      'GPT-5.5 通过 DALL-E 集成提供图像生成能力',
      'DeepSeek 在多模态方面较弱，专注文本与代码',
    ]}
  />,
  // Section 6
  () => <Divider num="06" title="速度与延迟" />,
  () => <TablePage
    heading="速度与延迟对比"
    cols={['指标', 'Claude Opus', 'GPT-5.5', 'Gemini 2.5', 'Qwen 3.7', 'DeepSeek V4']}
    rows={[
      ['输出速度 (tok/s)', '~2.2', '~8', '~15', '~25 🏆', '~12'],
      ['首字延迟 (TTFT)', '~1.5s', '~1.0s', '~0.8s', '~0.6s 🏆', '~1.2s'],
      ['上下文窗口', '100万 🏆', '12.8万', '200万 🏆', '25.6万', '25.6万'],
    ]}
  />,
  () => <Content
    heading="速度性能关键发现"
    bullets={[
      '速度排序：Qwen > Gemini > DeepSeek > GPT > Claude',
      'Claude 因自适应推理模式，速度最慢但智能最高',
      '上下文窗口：Claude (100万) 和 Gemini (200万) 遥遥领先',
      '长文档处理首选 Claude 或 Gemini',
    ]}
  />,
  // Section 7
  () => <Divider num="07" title="价格与性价比" />,
  () => <TablePage
    heading="价格对比（每百万token，美元）"
    cols={['模型', '输入价格', '输出价格', '性价比']}
    rows={[
      ['Claude Fable 5', '$10.00', '$50.00', '最贵，智能最高'],
      ['Claude Opus 4.8', '$5.00', '$25.00', '高端性价比'],
      ['GPT-5.5', '~$5.00', '~$20.00', '均衡'],
      ['Gemini 2.5 Pro', '~$2.50', '~$10.00', '多模态性价比优'],
      ['Qwen3.7 Plus', '~$0.50', '~$2.00', '极致性价比 🏆'],
      ['DeepSeek V4 Pro', '~$0.25', '~$1.00', '最低价 🏆'],
    ]}
  />,
  () => <Content
    heading="性价比排序"
    accentNum="DeepSeek → Qwen → Gemini → GPT → Claude"
    bullets={[
      'DeepSeek 价格仅 Claude 的约 1/50',
      'Qwen 中文能力最优的同时价格极低',
      'Claude 最贵，但智能水平确实最高',
      '大规模批量调用：首选 Qwen 或 DeepSeek',
    ]}
  />,
  // Section 8
  () => <Divider num="08" title="中文能力专项评估" />,
  () => <TablePage
    heading="中文能力对比"
    cols={['维度', '通义千问', 'DeepSeek', 'Claude', 'GPT-5.5', 'Gemini']}
    rows={[
      ['中文理解', 'S级 🏆', 'S级 🏆', 'A级', 'A级', 'B+'],
      ['中文生成', 'S级 🏆', 'S级', 'A级', 'A级', 'B+'],
      ['中文长文本', 'S级', 'S级', 'S级', 'A级', 'A级'],
      ['文化语境', '最优 🏆', '优秀', '良好', '良好', '一般'],
    ]}
  />,
  () => <Content
    heading="中文场景选型建议"
    bullets={[
      '通义千问和 DeepSeek 是中文场景最佳选择',
      '中文文化语境理解显著优于海外模型',
      'Claude 100万上下文窗口适合超长中文文档',
      '中文代码注释：Qwen 和 DeepSeek 均为 S 级',
    ]}
  />,
  // Section 9
  () => <Divider num="09" title="适用场景推荐" />,
  () => <Summary />,
  // Section 10
  () => <Divider num="10" title="关键趋势洞察" />,
  () => <Content
    heading="五大关键趋势"
    bullets={[
      'Anthropic 正在拉开差距 — Claude F5 领先约5分',
      '推理模式成为标配 — 自适应推理 + fallback 机制',
      '中国模型性价比碾压 — 智能接近一线，价格1/50',
      '多模态仍是 Google 领地 — Gemini 持续领先',
      'Agentic 能力成新战场 — 从回答问题到完成任务',
    ]}
  />,
  Ending,
] satisfies Page[];

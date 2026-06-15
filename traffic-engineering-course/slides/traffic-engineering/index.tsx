import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

// ─── Panel-tweakable design tokens ────────────────────────────────────────────
export const design: DesignSystem = {
  palette: {
    bg: '#0a1628',
    text: '#f0f4f8',
    accent: '#4fc3f7',
  },
  fonts: {
    display: '"Inter", "Noto Sans SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif',
    body: '"Inter", "Noto Sans SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif',
  },
  typeScale: {
    hero: 144,
    body: 32,
  },
  radius: 16,
};

// ─── Local constants ──────────────────────────────────────────────────────────
const palette = {
  bg: design.palette.bg,
  text: design.palette.text,
  accent: design.palette.accent,
  surface: '#0f2035',
  surfaceHi: '#152a42',
  surfaceMax: '#1a3550',
  textSoft: '#c4d4e0',
  muted: '#5a7a94',
  dim: '#2d4a63',
  border: 'rgba(79, 195, 247, 0.12)',
  borderBright: 'rgba(79, 195, 247, 0.25)',
  accentSoft: '#81d4fa',
  accent2: '#29b6f6',
  green: '#66bb6a',
  amber: '#ffb74d',
  red: '#ef5350',
  purple: '#ab47bc',
};

const font = {
  sans: design.fonts.body,
  display: design.fonts.display,
  mono: '"JetBrains Mono", "SF Mono", ui-monospace, Menlo, monospace',
};

const fill = {
  width: '100%',
  height: '100%',
  background: 'var(--osd-bg)',
  color: 'var(--osd-text)',
  fontFamily: 'var(--osd-font-body)',
  letterSpacing: '-0.01em',
  overflow: 'hidden',
  position: 'relative' as const,
};

// ─── Shared styles ────────────────────────────────────────────────────────────
const styles = `
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  .fadeUp { opacity: 0; animation: fadeUp 0.8s cubic-bezier(.2,.7,.2,1) forwards; }
  .fadeIn { opacity: 0; animation: fadeIn 1s ease forwards; }
  .slideIn { opacity: 0; animation: slideIn 0.7s cubic-bezier(.2,.7,.2,1) forwards; }
`;

const Styles = () => <style>{styles}</style>;

// ─── Shared components ────────────────────────────────────────────────────────
const GridBg = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      backgroundImage:
        'linear-gradient(rgba(79,195,247,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(79,195,247,0.04) 1px, transparent 1px)',
      backgroundSize: '80px 80px',
      maskImage: 'radial-gradient(ellipse at center, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 70%)',
      WebkitMaskImage: 'radial-gradient(ellipse at center, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 70%)',
    }}
  />
);

const Eyebrow = ({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) => (
  <div
    style={{
      fontFamily: font.mono,
      fontSize: 20,
      letterSpacing: '0.15em',
      textTransform: 'uppercase',
      color: palette.muted,
      ...style,
    }}
  >
    {children}
  </div>
);

const Card = ({
  children,
  delay = 0,
  style,
}: {
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
}) => (
  <div
    className="fadeUp"
    style={{
      animationDelay: `${delay}s`,
      background: palette.surface,
      border: `1px solid ${palette.border}`,
      borderRadius: 'var(--osd-radius)',
      padding: '32px',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      ...style,
    }}
  >
    {children}
  </div>
);

const BulletPoint = ({ children, delay = 0, color = palette.textSoft }: { children: React.ReactNode; delay?: number; color?: string }) => (
  <div className="slideIn" style={{ animationDelay: `${delay}s`, display: 'flex', gap: 16, alignItems: 'flex-start' }}>
    <span style={{ color: palette.accent, marginTop: 4, flexShrink: 0 }}>▸</span>
    <span style={{ fontSize: 28, color, lineHeight: 1.5 }}>{children}</span>
  </div>
);

const SectionDivider = ({ number, title, subtitle }: { number: string; title: string; subtitle: string }) => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '140px 140px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: 40,
      }}
    >
      <Eyebrow className="fadeUp" style={{ animationDelay: '0.1s' }}>{number}</Eyebrow>
      <h1
        className="fadeUp"
        style={{
          fontFamily: 'var(--osd-font-display)',
          fontSize: 120,
          fontWeight: 700,
          letterSpacing: '-0.03em',
          lineHeight: 1.1,
          margin: 0,
          color: palette.text,
          animationDelay: '0.2s',
        }}
      >
        {title}
      </h1>
      <p
        className="fadeUp"
        style={{
          fontSize: 32,
          color: palette.textSoft,
          maxWidth: 1200,
          lineHeight: 1.5,
          animationDelay: '0.35s',
        }}
      >
        {subtitle}
      </p>
    </div>
  </div>
);

// ─── Slide 1: Cover ──────────────────────────────────────────────────────────
const Cover: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    {/* Decorative road lines */}
    <div
      style={{
        position: 'absolute',
        right: 120,
        top: 0,
        bottom: 0,
        width: 4,
        background: `repeating-linear-gradient(to bottom, ${palette.accent}40 0px, ${palette.accent}40 40px, transparent 40px, transparent 80px)`,
      }}
    />
    <div
      style={{
        position: 'absolute',
        right: 200,
        top: 0,
        bottom: 0,
        width: 4,
        background: `repeating-linear-gradient(to bottom, ${palette.accent}25 0px, ${palette.accent}25 40px, transparent 40px, transparent 80px)`,
      }}
    />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '140px 140px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <div className="fadeUp">
        <Eyebrow>高等学校 · 交通运输类专业核心课程</Eyebrow>
      </div>

      <div>
        <h1
          className="fadeUp"
          style={{
            fontFamily: 'var(--osd-font-display)',
            fontSize: 'var(--osd-size-hero)',
            lineHeight: 1.05,
            fontWeight: 800,
            margin: 0,
            letterSpacing: '-0.04em',
            animationDelay: '0.15s',
          }}
        >
          交通工程学
          <br />
          <span
            style={{
              fontSize: 80,
              fontWeight: 400,
              color: palette.accentSoft,
              letterSpacing: '-0.02em',
            }}
          >
            Traffic Engineering
          </span>
        </h1>
        <p
          className="fadeUp"
          style={{
            marginTop: 48,
            maxWidth: 1000,
            fontSize: 32,
            lineHeight: 1.6,
            color: palette.textSoft,
            animationDelay: '0.35s',
          }}
        >
          系统学习交通流理论、交通规划、交通管理与控制的核心理论与实践方法
        </p>
      </div>

      <div
        className="fadeUp"
        style={{
          animationDelay: '0.55s',
          display: 'flex',
          gap: 60,
          fontFamily: font.mono,
          fontSize: 20,
          color: palette.muted,
        }}
      >
        <span>📚 理论体系</span>
        <span>🔬 分析方法</span>
        <span>🛣️ 工程实践</span>
        <span>🚦 智能交通</span>
      </div>
    </div>
  </div>
);

// ─── Slide 2: Course Overview ────────────────────────────────────────────────
const CourseOverview: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 48,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>课程概述</Eyebrow>
        <h2
          style={{
            marginTop: 16,
            marginBottom: 0,
            fontFamily: 'var(--osd-font-display)',
            fontSize: 80,
            fontWeight: 700,
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
          }}
        >
          为什么要学习交通工程学？
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, minHeight: 0 }}>
        <Card delay={0.1}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>🌆</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text }}>城市化挑战</div>
          <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.6 }}>
            中国城镇化率已超过 65%，城市交通拥堵、停车难、出行效率低下成为制约城市发展的瓶颈问题
          </div>
        </Card>
        <Card delay={0.2}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>📊</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text }}>数据驱动决策</div>
          <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.6 }}>
            运用交通调查、数据分析和模型预测，为交通规划、设计和管理提供科学依据
          </div>
        </Card>
        <Card delay={0.3}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>🤖</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text }}>智慧交通发展</div>
          <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.6 }}>
            车路协同、自动驾驶、MaaS 等新技术正在重塑交通系统，需要新型工程人才
          </div>
        </Card>
        <Card delay={0.4}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>🌱</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text }}>可持续发展</div>
          <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.6 }}>
            双碳目标下，构建绿色、低碳、高效的综合交通运输体系是国家战略需求
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// ─── Slide 3: Table of Contents ──────────────────────────────────────────────
const TableOfContents: Page = () => {
  const chapters = [
    { num: '01', title: '交通工程学导论', desc: '学科定义、发展历程、研究对象', color: palette.accent },
    { num: '02', title: '交通流理论', desc: '交通流特性、宏观微观模型、通行能力', color: palette.green },
    { num: '03', title: '交通调查与数据分析', desc: '流量速度密度调查、OD 调查、数据方法', color: palette.amber },
    { num: '04', title: '道路交通规划', desc: '四阶段法、交通生成与分布、方式划分', color: palette.purple },
    { num: '05', title: '交叉口设计与信号控制', desc: '渠化设计、信号配时、延误分析', color: palette.red },
    { num: '06', title: '交通管理与智能交通系统', desc: '交通组织、ITS 架构、车路协同', color: palette.accent2 },
  ];

  return (
    <div style={fill}>
      <Styles />
      <GridBg />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          padding: '100px 120px',
          display: 'flex',
          flexDirection: 'column',
          gap: 40,
        }}
      >
        <div className="fadeUp">
          <Eyebrow>课程目录</Eyebrow>
          <h2
            style={{
              marginTop: 16,
              marginBottom: 0,
              fontFamily: 'var(--osd-font-display)',
              fontSize: 80,
              fontWeight: 700,
              letterSpacing: '-0.03em',
            }}
          >
            六大核心模块
          </h2>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 20, justifyContent: 'center' }}>
          {chapters.map((ch, i) => (
            <div
              key={ch.num}
              className="fadeUp"
              style={{
                animationDelay: `${0.1 + i * 0.08}s`,
                display: 'flex',
                alignItems: 'center',
                gap: 32,
                padding: '24px 32px',
                background: palette.surface,
                border: `1px solid ${palette.border}`,
                borderLeft: `4px solid ${ch.color}`,
                borderRadius: '0 var(--osd-radius) var(--osd-radius) 0',
              }}
            >
              <div
                style={{
                  fontFamily: font.mono,
                  fontSize: 28,
                  fontWeight: 700,
                  color: ch.color,
                  width: 60,
                }}
              >
                {ch.num}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 36, fontWeight: 600, color: palette.text }}>{ch.title}</div>
                <div style={{ fontSize: 22, color: palette.muted, marginTop: 4 }}>{ch.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ─── Slide 4: Chapter 1 - Introduction ───────────────────────────────────────
const Chapter1Intro: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第一章 · 导论</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          什么是交通工程学？
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, minHeight: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <Card delay={0.1}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>学科定义</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7 }}>
              交通工程学是研究交通流特性、交通系统规划、设计、管理与控制的综合性工程学科，
              涉及人、车、路、环境四要素的相互关系与优化配置
            </div>
          </Card>
          <Card delay={0.2}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>研究对象</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7 }}>
              • 交通流特性与规律<br />
              • 道路通行能力与服务水平<br />
              • 交通规划与设计方法<br />
              • 交通管理与控制技术
            </div>
          </Card>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <Card delay={0.3}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>发展历程</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7 }}>
              1930s 美国起步 → 1950s 形成体系 → 1970s 引入计算机 → 2000s 智能交通 → 2020s 车路协同与自动驾驶
            </div>
          </Card>
          <Card delay={0.4}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>相关学科</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7 }}>
              城市规划 · 土木工程 · 系统工程 · 运筹学 · 计算机科学 · 环境科学 · 行为科学
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
);

// ─── Slide 5: Traffic Flow Basics ────────────────────────────────────────────
const TrafficFlowBasics: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第二章 · 交通流理论</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          交通流三参数：流量、速度、密度
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 32, minHeight: 0 }}>
        <Card delay={0.1} style={{ borderTop: `4px solid ${palette.accent}` }}>
          <div style={{ fontSize: 64, fontWeight: 800, color: palette.accent, textAlign: 'center' }}>Q</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text, textAlign: 'center' }}>流量 (Flow)</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 12 }}>
            单位时间内通过某断面的车辆数
            <br /><br />
            单位：pcu/h（标准车/小时）
            <br /><br />
            <span style={{ fontFamily: font.mono, color: palette.accentSoft }}>Q = N / T</span>
          </div>
        </Card>

        <Card delay={0.2} style={{ borderTop: `4px solid ${palette.green}` }}>
          <div style={{ fontSize: 64, fontWeight: 800, color: palette.green, textAlign: 'center' }}>V</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text, textAlign: 'center' }}>速度 (Speed)</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 12 }}>
            车辆行驶的快慢程度
            <br /><br />
            地点速度 vs 区间速度
            <br /><br />
            <span style={{ fontFamily: font.mono, color: palette.green }}>V = L / T</span>
          </div>
        </Card>

        <Card delay={0.3} style={{ borderTop: `4px solid ${palette.amber}` }}>
          <div style={{ fontSize: 64, fontWeight: 800, color: palette.amber, textAlign: 'center' }}>K</div>
          <div style={{ fontSize: 32, fontWeight: 600, color: palette.text, textAlign: 'center' }}>密度 (Density)</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 12 }}>
            单位长度道路上存在的车辆数
            <br /><br />
            单位：pcu/km
            <br /><br />
            <span style={{ fontFamily: font.mono, color: palette.amber }}>K = N / L</span>
          </div>
        </Card>
      </div>

      <div className="fadeUp" style={{ animationDelay: '0.4s', textAlign: 'center', fontSize: 32, color: palette.textSoft, padding: '20px 40px', background: palette.surface, borderRadius: 'var(--osd-radius)', border: `1px solid ${palette.border}` }}>
        基本关系式：<span style={{ fontFamily: font.mono, color: palette.accent, fontWeight: 600 }}>Q = V × K</span>
        &nbsp;&nbsp;— 交通流理论的核心方程
      </div>
    </div>
  </div>
);

// ─── Slide 6: Fundamental Diagram ────────────────────────────────────────────
const FundamentalDiagram: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第二章 · 交通流理论</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          交通流基本图与 Greenshields 模型
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 40, minHeight: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <Card delay={0.1}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>速度-密度关系</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7, fontFamily: font.mono }}>
              V = Vf × (1 - K / Kj)
            </div>
            <div style={{ fontSize: 22, color: palette.textSoft, marginTop: 8 }}>
              Vf：自由流速度 &nbsp;|&nbsp; Kj：阻塞密度
            </div>
          </Card>

          <Card delay={0.2}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>流量-密度关系</div>
            <div style={{ fontSize: 24, color: palette.textSoft, lineHeight: 1.7, fontFamily: font.mono }}>
              Q = Vf × K - (Vf / Kj) × K²
            </div>
            <div style={{ fontSize: 22, color: palette.textSoft, marginTop: 8 }}>
              抛物线关系，存在最大通行能力 Qm
            </div>
          </Card>

          <Card delay={0.3}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>关键状态点</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6 }}>
              • 自由流状态：K→0, V→Vf, Q→0<br />
              • 最佳密度：Km = Kj / 2，对应最大流量 Qm<br />
              • 阻塞状态：K→Kj, V→0, Q→0
            </div>
          </Card>
        </div>

        <Card delay={0.2} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: palette.surfaceHi }}>
          <div style={{ fontSize: 24, color: palette.muted, marginBottom: 24 }}>交通流基本图示意</div>
          {/* Q-K diagram */}
          <svg width="480" height="360" viewBox="0 0 480 360">
            <defs>
              <linearGradient id="curveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={palette.accent} />
                <stop offset="100%" stopColor={palette.green} />
              </linearGradient>
            </defs>
            {/* Axes */}
            <line x1="60" y1="300" x2="440" y2="300" stroke={palette.muted} strokeWidth="2" />
            <line x1="60" y1="300" x2="60" y2="40" stroke={palette.muted} strokeWidth="2" />
            <text x="250" y="340" fill={palette.muted} fontSize="20" textAnchor="middle">密度 K</text>
            <text x="30" y="170" fill={palette.muted} fontSize="20" textAnchor="middle" transform="rotate(-90 30 170)">流量 Q</text>
            {/* Parabolic curve */}
            <path d="M 60 300 Q 250 60 440 300" fill="none" stroke="url(#curveGrad)" strokeWidth="4" />
            {/* Max point */}
            <circle cx="250" cy="180" r="8" fill={palette.amber} />
            <text x="250" y="160" fill={palette.amber} fontSize="18" textAnchor="middle" fontWeight="600">Qm</text>
            {/* Labels */}
            <text x="60" y="330" fill={palette.muted} fontSize="16" textAnchor="middle">0</text>
            <text x="440" y="330" fill={palette.muted} fontSize="16" textAnchor="middle">Kj</text>
            <text x="250" y="330" fill={palette.accentSoft} fontSize="16" textAnchor="middle">Km</text>
          </svg>
          <div style={{ fontSize: 20, color: palette.muted, marginTop: 16, textAlign: 'center' }}>
            Q-K 抛物线关系 &nbsp;|&nbsp; 顶点为最大通行能力
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// ─── Slide 7: Road Capacity ──────────────────────────────────────────────────
const RoadCapacity: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第二章 · 交通流理论</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          道路通行能力与服务水平
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, minHeight: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Card delay={0.1}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>通行能力分类</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              <strong style={{ color: palette.text }}>基本通行能力：</strong>理想条件下的最大流量<br />
              <strong style={{ color: palette.text }}>可能通行能力：</strong>实际道路条件下的修正值<br />
              <strong style={{ color: palette.text }}>设计通行能力：</strong>考虑服务水平的折减值
            </div>
          </Card>

          <Card delay={0.2}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>修正系数</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              C = C₀ × fw × fv × fp × ...<br /><br />
              车道宽度修正 fw、大型车修正 fv、驾驶员特性 fp、坡度修正、视距修正等
            </div>
          </Card>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Card delay={0.3}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>服务水平 (LOS)</div>
            <div style={{ fontSize: 20, color: palette.textSoft, lineHeight: 1.6 }}>
              <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}><span style={{ color: palette.green, fontWeight: 600 }}>A级</span> 自由流，驾驶自由度大</div>
              <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}><span style={{ color: palette.green, fontWeight: 600 }}>B级</span> 稳定流，轻微受限</div>
              <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}><span style={{ color: palette.amber, fontWeight: 600 }}>C级</span> 稳定流，明显受限</div>
              <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}><span style={{ color: palette.amber, fontWeight: 600 }}>D级</span> 接近不稳定流</div>
              <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}><span style={{ color: palette.red, fontWeight: 600 }}>E级</span> 通行能力极限</div>
              <div style={{ display: 'flex', gap: 12 }}><span style={{ color: palette.red, fontWeight: 600 }}>F级</span> 强制流，严重拥堵</div>
            </div>
          </Card>

          <Card delay={0.4}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.purple }}>典型数值参考</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              高速公路基本车道：2000-2400 pcu/h<br />
              城市主干道：1600-1800 pcu/h<br />
              城市次干道：1400-1600 pcu/h
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
);

// ─── Slide 8: Chapter 3 - Traffic Survey ─────────────────────────────────────
const TrafficSurvey: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第三章 · 交通调查与数据分析</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          交通调查类型与方法
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 28, minHeight: 0 }}>
        <Card delay={0.1} style={{ borderTop: `4px solid ${palette.accent}` }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>交通量调查</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 连续式调查（24h/7d）<br />
            • 间歇式调查（高峰时段）<br />
            • 自动化采集（线圈/视频）<br />
            • 关键指标：AADT、DHV、K值
          </div>
        </Card>

        <Card delay={0.2} style={{ borderTop: `4px solid ${palette.green}` }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>速度调查</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 地点速度测量（雷达/线圈）<br />
            • 区间速度测量（牌照匹配）<br />
            • 行驶速度与行程速度<br />
            • 85%位车速用于限速设定
          </div>
        </Card>

        <Card delay={0.3} style={{ borderTop: `4px solid ${palette.amber}` }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>OD 调查</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 起讫点调查（Origin-Destination）<br />
            • 家庭访问/路边询问/明信片<br />
            • 手机信令/GPS 大数据<br />
            • OD 表编制与分布预测
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// ─── Slide 9: Chapter 4 - Traffic Planning ───────────────────────────────────
const TrafficPlanning: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第四章 · 道路交通规划</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          交通规划四阶段法
        </h2>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 24, justifyContent: 'center' }}>
        {/* Stage 1 */}
        <div className="fadeUp" style={{ animationDelay: '0.1s', display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: palette.accent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, fontWeight: 700, flexShrink: 0 }}>1</div>
          <Card delay={0.15} style={{ flex: 1 }}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>交通生成 (Trip Generation)</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6 }}>
              预测各交通小区的出行发生量与吸引量。常用方法：回归分析法、交叉分类法、原单位法。
              影响因素：人口、就业、土地利用、汽车保有量等
            </div>
          </Card>
        </div>

        {/* Arrow */}
        <div style={{ textAlign: 'center', fontSize: 32, color: palette.muted }}>↓</div>

        {/* Stage 2 */}
        <div className="fadeUp" style={{ animationDelay: '0.2s', display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: palette.green, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, fontWeight: 700, flexShrink: 0 }}>2</div>
          <Card delay={0.25} style={{ flex: 1 }}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>交通分布 (Trip Distribution)</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6 }}>
              确定各小区之间的出行交换量。常用模型：重力模型（Gravity Model）、Fratar 法、机会模型。
              核心思想：出行量与产生量/吸引量成正比，与阻抗成反比
            </div>
          </Card>
        </div>

        {/* Arrow */}
        <div style={{ textAlign: 'center', fontSize: 32, color: palette.muted }}>↓</div>

        {/* Stage 3 */}
        <div className="fadeUp" style={{ animationDelay: '0.3s', display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: palette.amber, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, fontWeight: 700, flexShrink: 0 }}>3</div>
          <Card delay={0.35} style={{ flex: 1 }}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>方式划分 (Mode Split)</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6 }}>
              预测各交通方式的分担率。常用方法：Logit 模型、Probit 模型、转移曲线法。
              影响因素：出行时间、费用、舒适度、可达性、政策引导
            </div>
          </Card>
        </div>

        {/* Arrow */}
        <div style={{ textAlign: 'center', fontSize: 32, color: palette.muted }}>↓</div>

        {/* Stage 4 */}
        <div className="fadeUp" style={{ animationDelay: '0.4s', display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ width: 80, height: 80, borderRadius: '50%', background: palette.purple, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, fontWeight: 700, flexShrink: 0 }}>4</div>
          <Card delay={0.45} style={{ flex: 1 }}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.purple }}>交通分配 (Traffic Assignment)</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6 }}>
              将 OD 出行量分配到路网各路段。常用算法：全有全无法、用户均衡 (UE)、系统最优 (SO)、随机用户均衡 (SUE)。
              Wardrop 两大原理是分配的理论基础
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
);

// ─── Slide 10: Chapter 5 - Intersection Design ───────────────────────────────
const IntersectionDesign: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第五章 · 交叉口设计与信号控制</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          平面交叉口信号控制设计
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, minHeight: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Card delay={0.1}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>信号配时参数</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              <strong>周期长度 C：</strong>信号灯完成一轮变化所需时间<br />
              <strong>绿信比 λ：</strong>有效绿灯时间与周期之比<br />
              <strong>相位：</strong>同时获得通行权的交通流组合<br />
              <strong>损失时间 L：</strong>启动损失 + 清空时间
            </div>
          </Card>

          <Card delay={0.2}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>Webster 配时方法</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7, fontFamily: font.mono }}>
              C₀ = (1.5L + 5) / (1 - Y)
            </div>
            <div style={{ fontSize: 20, color: palette.textSoft, marginTop: 8 }}>
              L：总损失时间 &nbsp;|&nbsp; Y：各相位最大流量比之和<br />
              最佳周期使车辆总延误最小
            </div>
          </Card>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Card delay={0.3}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>交叉口渠化设计</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              • 车道功能划分（直行/左转/右转）<br />
              • 导流岛与标线设计<br />
              • 左转待转区设置<br />
              • 行人与非机动车过街设施<br />
              • 视距三角形保证
            </div>
          </Card>

          <Card delay={0.4}>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.red }}>延误分析</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7 }}>
              <strong>控制延误：</strong>信号灯引起的停车延误<br />
              HCM 延误公式考虑：均匀延误 + 增量延误<br />
              服务水平分级：A（&lt;10s）→ F（&gt;80s）
            </div>
          </Card>
        </div>
      </div>
    </div>
  </div>
);

// ─── Slide 11: Chapter 6 - ITS ───────────────────────────────────────────────
const IntelligentTransport: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>第六章 · 交通管理与智能交通系统</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em' }}>
          智能交通系统 (ITS) 与前沿技术
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 28, minHeight: 0 }}>
        <Card delay={0.1} style={{ borderTop: `4px solid ${palette.accent}` }}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>🚦</div>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>交通管理系统</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 交通信号自适应控制<br />
            • 区域协调控制 (SCATS/SCOOT)<br />
            • 交通诱导与信息发布<br />
            • 事件检测与应急管理
          </div>
        </Card>

        <Card delay={0.2} style={{ borderTop: `4px solid ${palette.green}` }}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>🚗</div>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>车路协同 (V2X)</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 车与车通信 (V2V)<br />
            • 车与基础设施通信 (V2I)<br />
            • C-V2X 与 5G 通信<br />
            • 自动驾驶协同感知<br />
            • 智能网联汽车测试
          </div>
        </Card>

        <Card delay={0.3} style={{ borderTop: `4px solid ${palette.amber}` }}>
          <div style={{ fontSize: 40, marginBottom: 8 }}>📱</div>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>MaaS 与大数据</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.6, marginTop: 8 }}>
            • 出行即服务 (Mobility as a Service)<br />
            • 手机信令/公交 IC 卡数据<br />
            • 浮动车 GPS 轨迹分析<br />
            • 人工智能在交通中的应用
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// ─── Slide 12: Summary ───────────────────────────────────────────────────────
const Summary: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '140px 140px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <div className="fadeUp">
        <Eyebrow>课程总结</Eyebrow>
        <h2
          style={{
            marginTop: 24,
            fontSize: 100,
            fontWeight: 700,
            letterSpacing: '-0.04em',
            lineHeight: 1.05,
            margin: 0,
          }}
        >
          核心知识体系回顾
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28 }}>
        {[
          { title: '交通流理论', icon: '📈', desc: '掌握流量-速度-密度关系，理解通行能力与服务水平' },
          { title: '交通调查', icon: '📋', desc: '熟练运用各类交通调查方法，掌握数据处理与分析技能' },
          { title: '交通规划', icon: '🗺️', desc: '理解四阶段法原理，能够进行交通需求预测与方案评价' },
          { title: '信号控制', icon: '🚦', desc: '掌握交叉口渠化设计与信号配时优化方法' },
        ].map((item, i) => (
          <Card key={item.title} delay={0.1 + i * 0.1}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>{item.icon}</div>
            <div style={{ fontSize: 28, fontWeight: 600, color: palette.text }}>{item.title}</div>
            <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.5 }}>{item.desc}</div>
          </Card>
        ))}
      </div>

      <div
        className="fadeUp"
        style={{
          animationDelay: '0.6s',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontFamily: font.mono,
          fontSize: 20,
          color: palette.muted,
        }}
      >
        <span>理论 + 实践 + 创新 = 现代交通工程人才</span>
        <span>交通工程学</span>
      </div>
    </div>
  </div>
);

// ─── Slide 13: Homework ──────────────────────────────────────────────────────
const Homework: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '100px 120px',
        display: 'flex',
        flexDirection: 'column',
        gap: 48,
      }}
    >
      <div className="fadeUp">
        <Eyebrow>课后任务</Eyebrow>
        <h2 style={{ marginTop: 16, fontSize: 80, fontWeight: 700, letterSpacing: '-0.03em' }}>
          思考题与实践作业
        </h2>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, minHeight: 0 }}>
        <Card delay={0.1}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.accent }}>📝 思考题</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7, marginTop: 8 }}>
            1. 交通流三参数之间有什么关系？画出基本图并解释<br />
            2. 通行能力与服务水平有何区别与联系？<br />
            3. 四阶段法中每个阶段的作用是什么？<br />
            4. 如何优化一个拥堵交叉口的信号配时？<br />
            5. 智能交通系统如何解决城市交通问题？
          </div>
        </Card>

        <Card delay={0.2}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.green }}>🔧 实践作业</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7, marginTop: 8 }}>
            1. 选择一个交叉口，进行 15 分钟交通量调查<br />
            2. 使用 Webster 方法计算最佳信号周期<br />
            3. 分析调查路段的服务水平等级<br />
            4. 提出改善建议并撰写调查报告<br />
            5. 查阅一篇智能交通相关论文并做课堂分享
          </div>
        </Card>

        <Card delay={0.3} style={{ gridColumn: '1 / 3' }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: palette.amber }}>📚 推荐阅读</div>
          <div style={{ fontSize: 22, color: palette.textSoft, lineHeight: 1.7, marginTop: 8 }}>
            • 《交通工程学》（第 5 版），任福田主编，人民交通出版社<br />
            • 《交通流理论》，王炜等，科学出版社<br />
            • Highway Capacity Manual (HCM 6th Edition), TRB<br />
            • Transportation Engineering: An Introduction, C.J. Khisty
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// ─── Slide 14: AI Marker ─────────────────────────────────────────────────────
const AIMarker: Page = () => (
  <div style={fill}>
    <Styles />
    <GridBg />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: '140px 140px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 40,
      }}
    >
      <div className="fadeUp" style={{ textAlign: 'center' }}>
        <h2 style={{ fontSize: 72, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 24 }}>
          感谢观看
        </h2>
        <p style={{ fontSize: 32, color: palette.textSoft, maxWidth: 800 }}>
          交通工程学 —— 让出行更美好，让城市更智慧
        </p>
      </div>

      <div
        className="fadeUp"
        style={{
          animationDelay: '0.3s',
          marginTop: 40,
          padding: '24px 48px',
          background: palette.surface,
          border: `1px solid ${palette.border}`,
          borderRadius: 'var(--osd-radius)',
          fontSize: 24,
          color: palette.muted,
        }}
      >
        本文由 AI 辅助创作 · 交通工程学课程 PPT · 2026 年
      </div>
    </div>
  </div>
);

// ─── Slide export ────────────────────────────────────────────────────────────
export const meta: SlideMeta = {
  title: '交通工程学 Traffic Engineering',
};

export default [
  Cover,
  CourseOverview,
  TableOfContents,
  SectionDivider({ number: '第一章', title: '交通工程学导论', subtitle: '学科定义、发展历程、研究对象与学科体系' }),
  Chapter1Intro,
  SectionDivider({ number: '第二章', title: '交通流理论', subtitle: '交通流特性、宏观微观模型与通行能力分析' }),
  TrafficFlowBasics,
  FundamentalDiagram,
  RoadCapacity,
  SectionDivider({ number: '第三章', title: '交通调查与数据分析', subtitle: '流量速度密度调查、OD 调查与数据处理方法' }),
  TrafficSurvey,
  SectionDivider({ number: '第四章', title: '道路交通规划', subtitle: '四阶段法：交通生成、分布、方式划分与交通分配' }),
  TrafficPlanning,
  SectionDivider({ number: '第五章', title: '交叉口设计与信号控制', subtitle: '渠化设计、信号配时、延误分析与服务水平评价' }),
  IntersectionDesign,
  SectionDivider({ number: '第六章', title: '交通管理与智能交通系统', subtitle: '交通组织优化、ITS 架构、车路协同与前沿技术' }),
  IntelligentTransport,
  Summary,
  Homework,
  AIMarker,
] satisfies Page[];

import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

export const design: DesignSystem = {
  palette: { bg: '#0a0e1a', text: '#f0f2f5', accent: '#f59e0b' },
  fonts: {
    display: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif',
    body: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  typeScale: { hero: 160, body: 36 },
  radius: 12,
};

const muted = '#8b95a8';
const accent = 'var(--osd-accent)';
const text = 'var(--osd-text)';

const fill = { width: '100%', height: '100%' } as const;

/* ─── Page 1: Cover ─── */
const Cover: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(135deg, #0a0e1a 0%, #1a1f3a 50%, #0a0e1a 100%)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 120px',
    }}
  >
    <div style={{ fontSize: 120, marginBottom: 16 }}>🦞</div>
    <div
      style={{
        fontSize: 28,
        color: accent,
        letterSpacing: '0.3em',
        fontWeight: 600,
        marginBottom: 24,
      }}
    >
      LOBSTER NETWORK
    </div>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 'var(--osd-size-hero)',
        fontWeight: 900,
        lineHeight: 1.05,
        margin: '0 0 32px 0',
        textAlign: 'center',
        letterSpacing: '-0.03em',
      }}
    >
      小龙虾网络
    </h1>
    <p
      style={{
        fontSize: 44,
        color: accent,
        fontWeight: 500,
        textAlign: 'center',
        margin: 0,
      }}
    >
      对话即创造 — 多 Agent 协作开源框架
    </p>
    <p style={{ fontSize: 28, color: muted, marginTop: 48, textAlign: 'center' }}>
      一人一世界观 · 世界是对话 · 世界是编程的
    </p>
    <p style={{ fontSize: 22, color: muted, marginTop: 64 }}>
      v0.4.0 · MIT License · 23 commits · 41 tests passing
    </p>
  </div>
);

/* ─── Page 2: One-Liner ─── */
const OneLiner: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      一句话介绍
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        lineHeight: 1.2,
        margin: '64px 0 0 0',
        color: text,
      }}
    >
      基于"对话即创造"理论的
    </h2>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        lineHeight: 1.2,
        margin: '0 0 48px 0',
        color: accent,
      }}
    >
      多智能体协作开源框架
    </h2>
    <p style={{ fontSize: 'var(--osd-size-body)', color: muted, lineHeight: 1.7, margin: 0 }}>
      将哲学命题"对话产生涌现"工程化为可运行的 AI Agent 网络系统。
    </p>
    <div
      style={{
        marginTop: 64,
        padding: '32px 48px',
        background: 'rgba(245,158,11,0.08)',
        borderRadius: 12,
        borderLeft: '4px solid #f59e0b',
      }}
    >
      <p style={{ fontSize: 36, color: text, lineHeight: 1.5, margin: 0, fontStyle: 'italic' }}>
        "如果每个 Agent 都是一个独特的认知视角，<br />
        让它们持续对话，会产生什么<br />
        <span style={{ color: accent, fontWeight: 700 }}>单人永远算不到的东西？</span>"
      </p>
    </div>
  </div>
);

/* ─── Page 3: Core Theory ─── */
const CoreTheory: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      核心理论
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      三层世界观
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {[
        {
          num: '01',
          title: '一人一世界',
          desc: '每个节点拥有独特的认知种子：视角 × 知识 × 价值观',
          icon: '🌍',
        },
        {
          num: '02',
          title: '世界是对话',
          desc: '对话不是传递，是交叉编译——涌现生成器',
          icon: '💬',
        },
        {
          num: '03',
          title: '世界是编程的',
          desc: '世界按需渲染，非预设——程序化生成的知识地图',
          icon: '⚡',
        },
      ].map((item) => (
        <div
          key={item.num}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 32,
            padding: '24px 32px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 48 }}>{item.icon}</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 22, color: accent, fontWeight: 600 }}>{item.num}</div>
            <div style={{ fontSize: 44, fontWeight: 700, marginTop: 4 }}>{item.title}</div>
            <div style={{ fontSize: 32, color: muted, marginTop: 4 }}>{item.desc}</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 4: Architecture ─── */
const Architecture: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      系统架构
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      四层设计
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {[
        {
          layer: '应用层',
          color: '#22d3ee',
          items: ['围棋训练系统', '海报设计系统', '… 可扩展领域'],
        },
        {
          layer: '运营层',
          color: '#a78bfa',
          items: ['任务调度', '学生 Agent', '教练系统', '监控工具'],
        },
        {
          layer: '框架层',
          color: '#f59e0b',
          items: ['节点模型', '对话引擎', '涌现检测', '世界状态', '因陀罗网拓扑'],
        },
        {
          layer: '基础设施层',
          color: '#34d399',
          items: ['SSH 通道', '消息协议', '配置管理', '日志系统'],
        },
      ].map((l) => (
        <div
          key={l.layer}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 24,
            padding: '16px 28px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            borderLeft: `4px solid ${l.color}`,
          }}
        >
          <div
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: l.color,
              minWidth: 140,
            }}
          >
            {l.layer}
          </div>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            {l.items.map((item) => (
              <span
                key={item}
                style={{
                  fontSize: 30,
                  color: muted,
                  padding: '4px 16px',
                  background: 'rgba(255,255,255,0.04)',
                  borderRadius: 8,
                }}
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 5: Core Modules ─── */
const CoreModules: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      核心模块
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      五大引擎
    </h2>
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 24,
      }}
    >
      {[
        { icon: '🧠', title: '节点系统', desc: '认知编译系统，拥有独特的灵魂种子' },
        { icon: '💬', title: '对话引擎', desc: '认知交叉编译，涌现生成器' },
        { icon: '✨', title: '涌现检测', desc: '4 因子加权算法 + 稀有度系统' },
        { icon: '🗺️', title: '世界地图', desc: '按需渲染，宝藏系统，增量同步' },
      ].map((m) => (
        <div
          key={m.title}
          style={{
            padding: '28px 32px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 44 }}>{m.icon}</div>
          <div style={{ fontSize: 36, fontWeight: 700, marginTop: 8 }}>{m.title}</div>
          <div style={{ fontSize: 28, color: muted, marginTop: 6 }}>{m.desc}</div>
        </div>
      ))}
    </div>
    <div
      style={{
        marginTop: 24,
        padding: '28px 32px',
        background: 'rgba(245,158,11,0.06)',
        borderRadius: 12,
        border: '1px solid rgba(245,158,11,0.2)',
        display: 'flex',
        alignItems: 'center',
        gap: 24,
      }}
    >
      <div style={{ fontSize: 44 }}>🕸️</div>
      <div>
        <div style={{ fontSize: 36, fontWeight: 700 }}>因陀罗网拓扑 (IndraNet)</div>
        <div style={{ fontSize: 28, color: muted, marginTop: 4 }}>
          全互联网络——每颗宝珠映照所有宝珠，每个新节点自动全连接
        </div>
      </div>
    </div>
  </div>
);

/* ─── Page 6: Time Arbitrage ─── */
const TimeArbitrage: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      v0.3.0 新特性
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      ⏱️ 时间套利引擎
    </h2>
    <p style={{ fontSize: 32, color: muted, margin: '0 0 32px 0' }}>
      利用节点在时间维度上的结构性差异——差异不是低效，是套利机会
    </p>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20 }}>
      {[
        { title: '速率套利', desc: '快节点生成原始洞见，慢节点深化验证' },
        { title: '错峰套利', desc: '深夜时段高强度训练（00:00-06:00）' },
        { title: '反思套利', desc: '基于遗忘曲线的最佳复习时机' },
        { title: '复利套利', desc: '多轮对话链式涌现，指数级增长' },
        { title: '时距套利', desc: '知识价值倒 U 曲线，48-72h 达峰' },
      ].map((item) => (
        <div
          key={item.title}
          style={{
            padding: '20px 24px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 10,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 32, fontWeight: 700, color: accent }}>{item.title}</div>
          <div style={{ fontSize: 26, color: muted, marginTop: 6 }}>{item.desc}</div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 7: Applications ─── */
const Applications: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      应用领域
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      已验证的跨领域迁移
    </h2>
    <div style={{ display: 'flex', gap: 24 }}>
      <div
        style={{
          flex: 1,
          padding: '28px',
          background: 'rgba(34,211,238,0.06)',
          borderRadius: 12,
          border: '1px solid rgba(34,211,238,0.15)',
        }}
      >
        <div style={{ fontSize: 48 }}>🎮</div>
        <div style={{ fontSize: 36, fontWeight: 800, marginTop: 12, color: '#22d3ee' }}>
          围棋训练系统
        </div>
        <div style={{ fontSize: 24, color: muted, marginTop: 12, lineHeight: 1.6 }}>
          • 总对局 17,205+<br />
          • 3 类差异化 Agent<br />
          • 19×19 完整规则引擎<br />
          • 四层反馈循环
        </div>
      </div>
      <div
        style={{
          flex: 1,
          padding: '28px',
          background: 'rgba(167,139,250,0.06)',
          borderRadius: 12,
          border: '1px solid rgba(167,139,250,0.15)',
        }}
      >
        <div style={{ fontSize: 48 }}>🎨</div>
        <div style={{ fontSize: 36, fontWeight: 800, marginTop: 12, color: '#a78bfa' }}>
          海报设计系统
        </div>
        <div style={{ fontSize: 24, color: muted, marginTop: 12, lineHeight: 1.6 }}>
          • HTML + Playwright 渲染<br />
          • ImageGen 插图生成<br />
          • python-pptx 自动组装<br />
          • 跨领域迁移验证
        </div>
      </div>
      <div
        style={{
          flex: 1,
          padding: '28px',
          background: 'rgba(52,211,153,0.06)',
          borderRadius: 12,
          border: '1px solid rgba(52,211,153,0.15)',
        }}
      >
        <div style={{ fontSize: 48 }}>🏠</div>
        <div style={{ fontSize: 36, fontWeight: 800, marginTop: 12, color: '#34d399' }}>
          新生选寝系统
        </div>
        <div style={{ fontSize: 24, color: muted, marginTop: 12, lineHeight: 1.6 }}>
          • 7 个 Phase 全部完成<br />
          • 10 个标准业务能力<br />
          • 钉钉对话入口 + 定时汇报<br />
          • 验收 10/10 ✅ 100 人测试
        </div>
      </div>
    </div>
  </div>
);

/* ─── Page 8: Protocol ─── */
const Protocol: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      协议层
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 16px 0',
      }}
    >
      OADP 开放 Agent 对话协议
    </h2>
    <p style={{ fontSize: 28, color: muted, margin: '0 0 40px 0' }}>
      6 个核心规范文档，共 1,367 行，定义多 Agent 协作的标准化协议
    </p>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
      {[
        { file: 'protocol.md', title: 'OADP 核心协议', desc: '消息格式 / 对话流程 / 涌现计算 / 错误处理' },
        { file: 'drp.md', title: '对话渲染协议', desc: '7 步渲染流程 / 涌现检测算法 / 对话模板' },
        { file: 'world-map.md', title: '世界地图索引协议', desc: '地图结构 / 同步机制 / 冲突解决 / 权限控制' },
        { file: 'soul_schema.md', title: '灵魂种子格式', desc: 'SOUL.md Markdown + JSON Schema 规范' },
        { file: 'memory_schema.md', title: '记忆格式规范', desc: 'MEMORY.md 格式与更新规则' },
        { file: 'portal.md', title: '传送门协议', desc: '结构 / 生命周期 / 知识传承链' },
      ].map((p) => (
        <div
          key={p.file}
          style={{
            padding: '20px 24px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 10,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 22, color: '#34d399', fontFamily: 'monospace' }}>
            spec/{p.file}
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, marginTop: 4 }}>{p.title}</div>
          <div style={{ fontSize: 26, color: muted, marginTop: 4 }}>{p.desc}</div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 9: Team ─── */
const Team: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      团队协作
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      六人协作网络
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20 }}>
      {[
        { name: '诸葛斌', role: '项目架构师', icon: '👤', task: '方向决策 · 跨域整合 · 开源发起' },
        { name: '信电大虾', role: '核心开发', icon: '🦐', task: '代码实现 · 文档撰写' },
        { name: '诸葛马', role: '架构师/教练', icon: '🐴', task: '训练系统设计 · 代码审查' },
        { name: '诸葛虾', role: 'SDK 开发', icon: '🦐', task: 'SDK 开发 · 自动化测试' },
        { name: '虾尔', role: '世界地图', icon: '🦞', task: '世界地图引擎 · 渲染协议' },
        { name: '小陈', role: '文档', icon: '📝', task: '文档编写' },
      ].map((m) => (
        <div
          key={m.name}
          style={{
            padding: '24px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
            textAlign: 'center' as const,
          }}
        >
          <div style={{ fontSize: 48 }}>{m.icon}</div>
          <div style={{ fontSize: 36, fontWeight: 700, marginTop: 8 }}>{m.name}</div>
          <div style={{ fontSize: 24, color: accent, marginTop: 4 }}>{m.role}</div>
          <div style={{ fontSize: 24, color: muted, marginTop: 8 }}>{m.task}</div>
        </div>
      ))}
    </div>
    <div
      style={{
        marginTop: 28,
        padding: '20px 28px',
        background: 'rgba(245,158,11,0.06)',
        borderRadius: 10,
        border: '1px solid rgba(245,158,11,0.15)',
      }}
    >
      <div style={{ fontSize: 28, color: muted }}>
        <span style={{ color: accent, fontWeight: 600 }}>协作流程：</span>
        NFS 双向通道实时同步 + GitHub Issue → PR → 审查 → 合并
      </div>
    </div>
  </div>
);

/* ─── Page 10: Roadmap ─── */
const Roadmap: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      开发路线图
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      从 v0.1 到 v1.0
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {[
        { v: 'v0.1.0', title: '核心引擎', desc: '节点模型、对话引擎、涌现检测', status: '✅ 完成' },
        { v: 'v0.2.0', title: '统一框架', desc: '运营系统整合、调度器迭代', status: '✅ 完成' },
        { v: 'v0.3.0', title: '时间套利引擎', desc: '五维套利模型', status: '✅ 完成' },
        { v: 'v0.4.0', title: '业务小龙虾落地', desc: '新生选寝系统（7 Phase 完成）', status: '✅ 当前' },
        { v: 'v0.5.0', title: '通信集成', desc: 'SSH 通信 + 消息协议', status: '🔲 计划中' },
        { v: 'v0.6.0', title: '领域扩展', desc: '更多应用领域接入', status: '🔲 计划中' },
        { v: 'v1.0.0', title: '正式 Release', desc: '第一个稳定版本发布', status: '🔲 计划中' },
      ].map((item) => (
        <div
          key={item.v}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 28,
            padding: '20px 28px',
            background: item.status.includes('✅') ? 'rgba(34,211,238,0.06)' : 'rgba(255,255,255,0.02)',
            borderRadius: 12,
            border: `1px solid ${item.status.includes('✅') ? 'rgba(34,211,238,0.15)' : 'rgba(255,255,255,0.06)'}`,
          }}
        >
          <div
            style={{
              fontSize: 32,
              fontWeight: 800,
              color: item.status.includes('✅') ? '#22d3ee' : muted,
              minWidth: 110,
            }}
          >
            {item.v}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 36, fontWeight: 700 }}>{item.title}</div>
            <div style={{ fontSize: 28, color: muted }}>{item.desc}</div>
          </div>
          <div style={{ fontSize: 28, fontWeight: 600, color: item.status.includes('✅') ? '#22d3ee' : muted }}>
            {item.status}
          </div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 11: Stats ─── */
const Stats: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 120px',
    }}
  >
    <div style={{ fontSize: 24, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      仓库统计
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      项目数据一览
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 28 }}>
      {[
        { num: '23', unit: '次提交', label: 'Git Commits' },
        { num: '75+', unit: '文件', label: 'Total Files' },
        { num: '41', unit: '个测试', label: 'Tests Passing' },
        { num: '20K+', unit: '行代码', label: 'Lines of Code' },
      ].map((s) => (
        <div
          key={s.label}
          style={{
            textAlign: 'center' as const,
            padding: '32px 20px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 80, fontWeight: 900, color: accent, lineHeight: 1 }}>{s.num}</div>
          <div style={{ fontSize: 32, color: muted, marginTop: 8 }}>{s.unit}</div>
          <div style={{ fontSize: 22, color: muted, marginTop: 4 }}>{s.label}</div>
        </div>
      ))}
    </div>
    <div
      style={{
        marginTop: 40,
        padding: '24px 32px',
        background: 'rgba(245,158,11,0.06)',
        borderRadius: 12,
        border: '1px solid rgba(245,158,11,0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: 20,
      }}
    >
      <div style={{ fontSize: 36 }}>📦</div>
      <div>
        <div style={{ fontSize: 32, fontWeight: 700, color: accent }}>GitHub 仓库</div>
        <div style={{ fontSize: 26, color: muted }}>
          github.com/zhugebin-hub/lobster-network · MIT License
        </div>
      </div>
    </div>
  </div>
);

/* ─── Page 12: Closing ─── */
const Closing: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(135deg, #0a0e1a 0%, #1a1f3a 50%, #0a0e1a 100%)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 120px',
    }}
  >
    <div style={{ fontSize: 120, marginBottom: 24 }}>🦞</div>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 'var(--osd-size-hero)',
        fontWeight: 900,
        lineHeight: 1.05,
        margin: '0 0 32px 0',
        textAlign: 'center',
        letterSpacing: '-0.03em',
      }}
    >
      你不停对话
    </h1>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 'var(--osd-size-hero)',
        fontWeight: 900,
        lineHeight: 1.05,
        margin: '0 0 48px 0',
        textAlign: 'center',
        letterSpacing: '-0.03em',
        color: accent,
      }}
    >
      世界就不停扩展
    </h1>
    <div
      style={{
        fontSize: 32,
        color: muted,
        textAlign: 'center',
        lineHeight: 1.8,
      }}
    >
      一人一世界观 · 世界是对话 · 世界是编程的<br />
      <span style={{ color: accent, fontWeight: 600 }}>Lobster Network v0.4.0</span>
    </div>
    <div style={{ fontSize: 24, color: muted, marginTop: 48 }}>
      github.com/zhugebin-hub/lobster-network
    </div>
  </div>
);

export const meta: SlideMeta = { title: '小龙虾网络 Lobster Network — 项目介绍' };
export default [Cover, OneLiner, CoreTheory, Architecture, CoreModules, TimeArbitrage, Applications, Protocol, Team, Roadmap, Stats, Closing] satisfies Page[];

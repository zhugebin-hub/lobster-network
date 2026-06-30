import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

// ─── Design tokens ────────────────────────────────────────────
export const design: DesignSystem = {
  palette: {
    bg: '#0a1628',
    text: '#e8ecf1',
    accent: '#3b82f6',
  },
  fonts: {
    display: '"PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif',
    body: '"PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif',
  },
  typeScale: { hero: 160, body: 36 },
  radius: 16,
};

const muted = '#7a8ba3';
const accent = '#3b82f6';
const accentLight = '#60a5fa';
const cardBg = 'rgba(59, 130, 246, 0.08)';
const cardBorder = 'rgba(59, 130, 246, 0.2)';

const fill = {
  width: '100%',
  height: '100%',
  fontFamily: 'var(--osd-font-body)',
} as const;

// ─── Cover ────────────────────────────────────────────────────
const Cover: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(135deg, #0a1628 0%, #0f2847 50%, #0a1628 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    {/* Decorative circles */}
    <div style={{ position: 'absolute', top: 80, right: 120, width: 400, height: 400, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.1)' }} />
    <div style={{ position: 'absolute', bottom: 60, left: 80, width: 280, height: 280, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.04)', border: '1px solid rgba(59, 130, 246, 0.08)' }} />

    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 40, fontWeight: 500 }}>
      数 字 员 工 实 践 汇 报
    </div>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 100,
        fontWeight: 900,
        margin: '0 0 40px 0',
        lineHeight: 1.15,
        textAlign: 'center',
        background: 'linear-gradient(90deg, #60a5fa, #a78bfa)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}
    >
      从规划到落地
    </h1>
    <p style={{ fontSize: 38, color: muted, maxWidth: 900, textAlign: 'center', lineHeight: 1.6 }}>
      构建智能化组织，释放AI生产力
    </p>
    <div style={{ marginTop: 80, display: 'flex', gap: 48, alignItems: 'center' }}>
      <div style={{ width: 48, height: 1, background: accent }} />
      <span style={{ fontSize: 28, color: muted }}>2026年6月</span>
      <div style={{ width: 48, height: 1, background: accent }} />
    </div>
  </div>
);

// ─── Agenda ───────────────────────────────────────────────────
const Agenda: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontFamily: 'var(--osd-font-display)', fontSize: 72, fontWeight: 800, margin: 0, marginBottom: 80 }}>
      汇报目录
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, maxWidth: 1400 }}>
      {[
        { num: '01', title: '背景与趋势', desc: '数字化转型浪潮与AI技术突破' },
        { num: '02', title: '数字员工定义', desc: '能力边界与技术架构' },
        { num: '03', title: '落地方案设计', desc: '整体架构与实施路径' },
        { num: '04', title: '典型应用场景', desc: '客服、运营、数据分析等' },
        { num: '05', title: '成本与收益', desc: 'ROI分析与投资回报' },
        { num: '06', title: '下一步计划', desc: '实施路线图与里程碑' },
      ].map((item) => (
        <div key={item.num} style={{ padding: '32px 40px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16, display: 'flex', alignItems: 'center', gap: 24 }}>
          <span style={{ fontSize: 56, fontWeight: 900, color: accent, fontFamily: 'monospace', minWidth: 80 }}>{item.num}</span>
          <div>
            <div style={{ fontSize: 36, fontWeight: 700, marginBottom: 8 }}>{item.title}</div>
            <div style={{ fontSize: 26, color: muted }}>{item.desc}</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ─── Section: Background ─────────────────────────────────────
const SectionDivider: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 01</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>背景与趋势</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>为什么现在是数字员工的最佳时机</p>
  </div>
);

// ─── Background: Industry Trends ──────────────────────────────
const BackgroundTrends: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 64 }}>
      <span style={{ color: accent }}>01</span> 行业背景
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 40 }}>
      {[
        { icon: '🤖', value: '78%', label: '企业计划部署AI员工', source: 'Gartner 2026' },
        { icon: '💰', value: '¥2.3万亿', label: '中国AI市场规模', source: 'IDC预测' },
        { icon: '⚡', value: '40%+', label: '人力成本可降低', source: '麦肯锡报告' },
      ].map((stat) => (
        <div key={stat.label} style={{ padding: '40px 32px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16, textAlign: 'center' }}>
          <div style={{ fontSize: 56, marginBottom: 16 }}>{stat.icon}</div>
          <div style={{ fontSize: 52, fontWeight: 900, color: accentLight, marginBottom: 16 }}>{stat.value}</div>
          <div style={{ fontSize: 28, marginBottom: 8 }}>{stat.label}</div>
          <div style={{ fontSize: 22, color: muted }}>{stat.source}</div>
        </div>
      ))}
    </div>
    <div style={{ marginTop: 48, fontSize: 30, color: muted, lineHeight: 1.6, borderLeft: `3px solid ${accent}`, paddingLeft: 24 }}>
      大语言模型能力突破 + 自动化技术成熟 + 企业数字化基础完备 = <span style={{ color: accentLight, fontWeight: 700 }}>数字员工规模化落地窗口已开启</span>
    </div>
  </div>
);

// ─── Section: Definition ─────────────────────────────────────
const SectionDef: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 02</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>数字员工定义</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>能力边界与技术架构</p>
  </div>
);

// ─── What is Digital Employee ─────────────────────────────────
const WhatIsDigitalEmployee: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>02</span> 什么是数字员工？
    </h2>
    <div style={{ display: 'flex', gap: 60, alignItems: 'flex-start' }}>
      {/* Left: Definition */}
      <div style={{ flex: 1 }}>
        <div style={{ padding: '40px 36px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16, marginBottom: 32 }}>
          <div style={{ fontSize: 28, color: accent, marginBottom: 16, fontWeight: 600 }}>核心定义</div>
          <p style={{ fontSize: 30, lineHeight: 1.7, margin: 0 }}>
            基于AI技术的<span style={{ color: accentLight, fontWeight: 700 }}>软件机器人</span>，
            能够模拟人类员工的认知能力，独立完成特定业务流程中的工作任务。
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { title: '理解能力', desc: '自然语言处理、意图识别、上下文理解' },
            { title: '决策能力', desc: '规则引擎、智能判断、异常处理' },
            { title: '执行能力', desc: 'API调用、系统操作、多平台协作' },
            { title: '学习能力', desc: '持续优化、知识更新、自我迭代' },
          ].map((item) => (
            <div key={item.title} style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: accent, flexShrink: 0 }} />
              <span style={{ fontSize: 28, fontWeight: 700, minWidth: 120 }}>{item.title}</span>
              <span style={{ fontSize: 26, color: muted }}>{item.desc}</span>
            </div>
          ))}
        </div>
      </div>
      {/* Right: Comparison */}
      <div style={{ flex: 1, padding: '36px 32px', background: 'rgba(59, 130, 246, 0.04)', border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
        <div style={{ fontSize: 32, fontWeight: 700, marginBottom: 32, textAlign: 'center' }}>vs 传统RPA</div>
        {[
          { left: '规则驱动', right: '语义驱动', good: true },
          { left: '固定流程', right: '灵活适应', good: true },
          { left: '结构化数据', right: '非结构化数据', good: true },
          { left: '需要人工配置', right: '自主学习', good: true },
        ].map((row) => (
          <div key={row.left} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <span style={{ fontSize: 26, color: muted }}>{row.left}</span>
            <span style={{ fontSize: 26, color: accentLight, fontWeight: 600 }}>→ {row.right}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// ─── Architecture ─────────────────────────────────────────────
const Architecture: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>02</span> 技术架构
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 1500 }}>
      {[
        { layer: '交互层', items: ['自然语言对话', '多模态输入', '语音/文字/图像'], color: '#10b981' },
        { layer: '大脑层', items: ['大语言模型 (LLM)', '知识图谱', '推理与规划引擎'], color: accent },
        { layer: '能力层', items: ['API调用', '代码执行', '文档处理', '数据分析'], color: '#8b5cf6' },
        { layer: '执行层', items: ['RPA自动化', '业务流程编排', '多系统对接'], color: '#f59e0b' },
      ].map((l, i) => (
        <div key={l.layer} style={{ display: 'flex', alignItems: 'center', gap: 24, padding: '24px 32px', background: `${l.color}10`, border: `1px solid ${l.color}30`, borderRadius: 12 }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: l.color, minWidth: 100, textAlign: 'center' }}>{l.layer}</div>
          <div style={{ width: 3, height: 48, background: l.color, borderRadius: 2, flexShrink: 0 }} />
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            {l.items.map((item) => (
              <span key={item} style={{ fontSize: 28, padding: '8px 20px', background: `${l.color}15`, borderRadius: 8 }}>{item}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ─── Section: Implementation ──────────────────────────────────
const SectionImpl: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 03</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>落地方案设计</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>整体架构与实施路径</p>
  </div>
);

// ─── Implementation Roadmap ───────────────────────────────────
const ImplementationRoadmap: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 64 }}>
      <span style={{ color: accent }}>03</span> 三阶段实施路径
    </h2>
    <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start' }}>
      {[
        { phase: '第一阶段', time: '1-3个月', tag: '试点验证', items: ['选取1-2个高频场景', '部署基础版数字员工', '跑通业务流程闭环', '评估效果并优化'], color: '#10b981' },
        { phase: '第二阶段', time: '3-6个月', tag: '规模推广', items: ['扩展至5-8个场景', '建立数字员工管理平台', '培训业务人员协同', '形成标准化SOP'], color: accent },
        { phase: '第三阶段', time: '6-12个月', tag: '全面融合', items: ['覆盖核心业务线', '数字员工自主运营', '人机协同常态化', '持续迭代优化'], color: '#8b5cf6' },
      ].map((p) => (
        <div key={p.phase} style={{ flex: 1, padding: '32px 28px', background: `${p.color}08`, border: `1px solid ${p.color}30`, borderRadius: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 26, color: p.color, fontWeight: 700 }}>{p.phase}</span>
            <span style={{ fontSize: 22, color: muted }}>{p.time}</span>
          </div>
          <div style={{ fontSize: 32, fontWeight: 800, marginBottom: 24 }}>{p.tag}</div>
          {p.items.map((item) => (
            <div key={item} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 14 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
              <span style={{ fontSize: 26, color: muted }}>{item}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

// ─── Key Success Factors ──────────────────────────────────────
const KeySuccessFactors: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>03</span> 成功关键要素
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, maxWidth: 1400 }}>
      {[
        { icon: '🎯', title: '明确业务目标', desc: '从痛点出发，而非技术驱动。先选高频、低风险的场景验证价值。' },
        { icon: '🔗', title: '高层支持与跨部门协作', desc: '一把手工程，IT与业务部门紧密配合，确保数据与流程打通。' },
        { icon: '📊', title: '可量化指标体系', desc: '建立ROI、效率提升、错误率下降等量化指标，持续跟踪。' },
        { icon: '🔒', title: '安全与合规保障', desc: '数据隐私保护、权限管控、操作审计，确保合规运行。' },
      ].map((item) => (
        <div key={item.title} style={{ padding: '36px 32px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>{item.icon}</div>
          <div style={{ fontSize: 34, fontWeight: 700, marginBottom: 12 }}>{item.title}</div>
          <div style={{ fontSize: 28, color: muted, lineHeight: 1.6 }}>{item.desc}</div>
        </div>
      ))}
    </div>
  </div>
);

// ─── Section: Use Cases ───────────────────────────────────────
const SectionUseCases: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 04</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>典型应用场景</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>客服、运营、数据分析等</p>
  </div>
);

// ─── Use Cases ────────────────────────────────────────────────
const UseCases: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>04</span> 核心应用场景
    </h2>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
      {[
        { icon: '💬', title: '智能客服', tasks: ['7×24在线应答', '智能工单分派', '情绪识别与升级', '知识库自动更新'], metric: '响应时间↓80%' },
        { icon: '📝', title: '内容运营', tasks: ['文章自动生成', '社交媒体发布', '数据报表编写', '多语言翻译'], metric: '产出效率↑5倍' },
        { icon: '📈', title: '数据分析', tasks: ['数据采集与清洗', '自动报表生成', '异常检测预警', '趋势预测分析'], metric: '分析效率↑10倍' },
        { icon: '🔄', title: '流程自动化', tasks: ['审批流程处理', '合同审查比对', '财务对账结算', '系统间数据同步'], metric: '人工干预↓70%' },
      ].map((uc) => (
        <div key={uc.title} style={{ padding: '32px 28px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <span style={{ fontSize: 40 }}>{uc.icon}</span>
              <span style={{ fontSize: 36, fontWeight: 700 }}>{uc.title}</span>
            </div>
            <span style={{ fontSize: 22, color: accentLight, fontWeight: 700, padding: '6px 16px', background: 'rgba(59, 130, 246, 0.15)', borderRadius: 8 }}>{uc.metric}</span>
          </div>
          {uc.tasks.map((t) => (
            <div key={t} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: accent, flexShrink: 0 }} />
              <span style={{ fontSize: 26, color: muted }}>{t}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

// ─── Section: ROI ─────────────────────────────────────────────
const SectionROI: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 05</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>成本与收益</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>ROI分析与投资回报</p>
  </div>
);

// ─── ROI Analysis ─────────────────────────────────────────────
const ROIAnalysis: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>05</span> 投入产出分析
    </h2>
    <div style={{ display: 'flex', gap: 48, alignItems: 'flex-start' }}>
      {/* Cost */}
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 36, fontWeight: 700, marginBottom: 24, color: '#f59e0b' }}>投入成本</div>
        {[
          { item: 'AI模型与平台', cost: '¥20-50万/年' },
          { item: '开发集成费用', cost: '¥10-30万/场景' },
          { item: '运维与培训', cost: '¥5-10万/年' },
          { item: '合计（首年）', cost: '¥50-100万' },
        ].map((c) => (
          <div key={c.item} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <span style={{ fontSize: 28, color: muted }}>{c.item}</span>
            <span style={{ fontSize: 28, fontWeight: 600 }}>{c.cost}</span>
          </div>
        ))}
      </div>
      {/* Return */}
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 36, fontWeight: 700, marginBottom: 24, color: '#10b981' }}>预期收益</div>
        {[
          { item: '人力成本节省', value: '40-60%' },
          { item: '处理效率提升', value: '5-10倍' },
          { item: '错误率降低', value: '90%+' },
          { item: '投资回收期', value: '6-12个月' },
        ].map((r) => (
          <div key={r.item} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <span style={{ fontSize: 28, color: muted }}>{r.item}</span>
            <span style={{ fontSize: 28, fontWeight: 600, color: '#10b981' }}>{r.value}</span>
          </div>
        ))}
      </div>
    </div>
    <div style={{ marginTop: 48, padding: '28px 36px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 16, textAlign: 'center' }}>
      <span style={{ fontSize: 32 }}>💡 结论：</span>
      <span style={{ fontSize: 32, color: '#10b981', fontWeight: 700 }}>数字员工投入产出比显著，首年即可收回成本，长期ROI持续增长</span>
    </div>
  </div>
);

// ─── Section: Next Steps ──────────────────────────────────────
const SectionNext: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(180deg, #0a1628 0%, #162544 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
    }}
  >
    <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>CHAPTER 06</div>
    <h1 style={{ fontSize: 120, fontWeight: 900, margin: 0, lineHeight: 1.1 }}>下一步计划</h1>
    <p style={{ fontSize: 36, color: muted, marginTop: 32 }}>实施路线图与里程碑</p>
  </div>
);

// ─── Next Steps ───────────────────────────────────────────────
const NextSteps: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 120 }}>
    <h2 style={{ fontSize: 60, fontWeight: 800, margin: 0, marginBottom: 48 }}>
      <span style={{ color: accent }}>06</span> 立即行动计划
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1400 }}>
      {[
        { week: '第1-2周', action: '需求调研与场景筛选', detail: '访谈业务部门，识别高频重复性工作任务', deliverable: '场景需求清单' },
        { week: '第3-4周', action: '技术方案设计与PoC验证', detail: '完成架构设计，选取1个场景进行概念验证', deliverable: 'PoC验证报告' },
        { week: '第5-8周', action: '试点上线与迭代优化', detail: '部署首个数字员工，收集反馈并持续优化', deliverable: '试点运行数据' },
        { week: '第9-12周', action: '效果评估与规模推广', detail: '总结试点经验，制定推广计划，扩大应用场景', deliverable: '推广实施方案' },
      ].map((step, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 32, padding: '28px 32px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
          <div style={{ fontSize: 26, fontWeight: 800, color: accent, minWidth: 110, textAlign: 'center', padding: '12px 0', background: `${accent}15`, borderRadius: 10 }}>{step.week}</div>
          <div style={{ width: 3, height: 60, background: accent, borderRadius: 2, flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 34, fontWeight: 700, marginBottom: 8 }}>{step.action}</div>
            <div style={{ fontSize: 26, color: muted }}>{step.detail}</div>
          </div>
          <div style={{ fontSize: 24, color: '#10b981', fontWeight: 600, padding: '10px 20px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: 10, whiteSpace: 'nowrap' }}>
            📋 {step.deliverable}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ─── Closing ──────────────────────────────────────────────────
const Closing: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(135deg, #0a1628 0%, #0f2847 50%, #0a1628 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    <div style={{ position: 'absolute', top: 60, right: 100, width: 350, height: 350, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.08)' }} />
    <div style={{ position: 'absolute', bottom: 40, left: 60, width: 240, height: 240, borderRadius: '50%', background: 'rgba(139, 92, 246, 0.04)', border: '1px solid rgba(139, 92, 246, 0.08)' }} />

    <div style={{ fontSize: 28, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>THANK YOU</div>
    <h1 style={{ fontSize: 96, fontWeight: 900, margin: '0 0 32px 0', lineHeight: 1.1, textAlign: 'center', background: 'linear-gradient(90deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
      感谢聆听
    </h1>
    <p style={{ fontSize: 36, color: muted, maxWidth: 700, textAlign: 'center', lineHeight: 1.6, marginBottom: 60 }}>
      拥抱AI时代，让数字员工成为企业新生产力
    </p>
    <div style={{ display: 'flex', gap: 48, alignItems: 'center' }}>
      <div style={{ width: 48, height: 1, background: accent }} />
      <span style={{ fontSize: 26, color: muted }}>敬请批评指正</span>
      <div style={{ width: 48, height: 1, background: accent }} />
    </div>
  </div>
);

export const meta: SlideMeta = { title: '数字员工落地汇报' };
export default [Cover, Agenda, SectionDivider, BackgroundTrends, SectionDef, WhatIsDigitalEmployee, Architecture, SectionImpl, ImplementationRoadmap, KeySuccessFactors, SectionUseCases, UseCases, SectionROI, ROIAnalysis, SectionNext, NextSteps, Closing] satisfies Page[];

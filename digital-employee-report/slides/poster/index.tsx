import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

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
  typeScale: { hero: 120, body: 32 },
  radius: 16,
};

const muted = '#7a8ba3';
const accent = '#3b82f6';
const accentLight = '#60a5fa';
const cardBg = 'rgba(59, 130, 246, 0.08)';
const cardBorder = 'rgba(59, 130, 246, 0.2)';
const green = '#10b981';
const orange = '#f59e0b';

const fill = {
  width: '100%',
  height: '100%',
  fontFamily: 'var(--osd-font-body)',
} as const;

// ─── COVER: Main Title ──────────────────────────────────
const Cover: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(135deg, #0a1628 0%, #0f2847 50%, #0a1628 100%)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '0 100px',
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    {/* Decorative circles */}
    <div style={{ position: 'absolute', top: -100, right: -50, width: 500, height: 500, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.08)' }} />
    <div style={{ position: 'absolute', bottom: -80, left: -40, width: 350, height: 350, borderRadius: '50%', background: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.06)' }} />

    {/* Top badge */}
    <div style={{ marginBottom: 40, padding: '12px 40px', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: 30 }}>
      <span style={{ fontSize: 28, color: accentLight, fontWeight: 700, letterSpacing: '0.1em' }}>清华大学出版社 · 重磅新书</span>
    </div>

    {/* Main title */}
    <h1 style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 72,
      fontWeight: 900,
      margin: '0 0 32px 0',
      lineHeight: 1.2,
      textAlign: 'center',
      maxWidth: 1400,
    }}>
      <span style={{ background: 'linear-gradient(90deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        智能体赋能高校教学新范式
      </span>
    </h1>
    <p style={{ fontSize: 38, color: muted, margin: '0 0 48px 0', textAlign: 'center', lineHeight: 1.4 }}>
      小龙虾 + Manus 一站式解决方案
    </p>

    {/* Divider */}
    <div style={{ width: 120, height: 3, background: 'linear-gradient(90deg, #3b82f6, #a78bfa)', borderRadius: 2, marginBottom: 48 }} />

    {/* Author + Time */}
    <div style={{ display: 'flex', gap: 64, alignItems: 'center' }}>
      {/* Author */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{
          width: 80, height: 80, borderRadius: '50%', overflow: 'hidden',
          border: '3px solid rgba(59, 130, 246, 0.4)',
        }}>
          <img src="./assets/author.png" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
        <div>
          <div style={{ fontSize: 30, fontWeight: 700, color: 'var(--osd-text)' }}>诸葛斌 教授</div>
          <div style={{ fontSize: 22, color: muted }}>浙江工商大学 · 萨塞克斯人工智能学院</div>
        </div>
      </div>

      {/* Time */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ fontSize: 48, fontWeight: 900, color: accentLight }}>6月24日</div>
        <div style={{ fontSize: 26, color: muted }}>下午 3:00-4:00</div>
      </div>
    </div>
  </div>
);

// ─── Content: Five Scenarios ────────────────────────────
const Scenarios: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 100 }}>
    {/* Title */}
    <div style={{ textAlign: 'center', marginBottom: 64 }}>
      <div style={{ fontSize: 26, color: accent, letterSpacing: '0.3em', marginBottom: 16, fontWeight: 600 }}>直播亮点</div>
      <h2 style={{ fontSize: 56, fontWeight: 900, margin: 0 }}>五大教学场景</h2>
      <p style={{ fontSize: 30, color: muted, marginTop: 16 }}>现场实操 · 2小时教案制作压缩至10分钟</p>
    </div>

    {/* 5 cards */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28, maxWidth: 1500, margin: '0 auto' }}>
      {[
        { icon: '📄', title: '课件智能生成', desc: '"小龙虾三部曲"精品课件', color: '#3b82f6' },
        { icon: '🌿', title: '教学案例开发', desc: '烟草数据挖掘、网络课程动画、微信小程序等', color: '#10b981' },
        { icon: '✍️', title: '论文协作写作', desc: '从选题到IEEE成稿全流程', color: '#a78bfa' },
        { icon: '🎬', title: '教学视频制作', desc: 'PPT自动转教学视频', color: '#f59e0b' },
        { icon: '📊', title: '数据可视化', desc: '一键生成可发表图表', color: '#ef4444' },
      ].map((s) => (
        <div key={s.title} style={{ display: 'flex', alignItems: 'center', gap: 28, padding: '28px 36px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
          <div style={{ fontSize: 48, width: 72, textAlign: 'center' }}>{s.icon}</div>
          <div style={{ width: 3, height: 56, background: s.color, borderRadius: 2 }} />
          <div>
            <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 6 }}>{s.title}</div>
            <div style={{ fontSize: 26, color: muted }}>{s.desc}</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ─── Benefits ───────────────────────────────────────────
const Benefits: Page = () => (
  <div style={{ ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)', padding: 100 }}>
    <div style={{ textAlign: 'center', marginBottom: 56 }}>
      <div style={{ fontSize: 26, color: green, letterSpacing: '0.3em', marginBottom: 16, fontWeight: 600 }}>入群福利</div>
      <h2 style={{ fontSize: 56, fontWeight: 900, margin: 0 }}>扫码加入读者服务群</h2>
      <p style={{ fontSize: 28, color: muted, marginTop: 12 }}>此群长期有效</p>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28, maxWidth: 1400, margin: '0 auto' }}>
      {[
        { icon: '🦞', title: '小龙虾AI体验', desc: '群内部署OpenClaw智能体，实时体验课件生成、教案制作等AI能力' },
        { icon: '📚', title: '教学资料包', desc: '小龙虾三部曲课件、数据挖掘案例、16章教学动画、微信小程序等全套Manus实战案例' },
        { icon: '🎁', title: '免费样书赠送', desc: '直播间专享10本《Manus智能体全攻略》免费样书（名额有限，抽奖获得）' },
        { icon: '💬', title: '教学交流社区', desc: '高校教师AI教学实践交流、问题解答、经验分享' },
      ].map((b) => (
        <div key={b.title} style={{ padding: '32px 28px', background: cardBg, border: `1px solid ${cardBorder}`, borderRadius: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 12 }}>
            <span style={{ fontSize: 40 }}>{b.icon}</span>
            <span style={{ fontSize: 32, fontWeight: 800 }}>{b.title}</span>
          </div>
          <div style={{ fontSize: 24, color: muted, lineHeight: 1.5 }}>{b.desc}</div>
        </div>
      ))}
    </div>

    {/* QR code */}
    <div style={{ marginTop: 48, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 40 }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: 220, height: 220, borderRadius: 16, overflow: 'hidden',
          background: '#fff', padding: 12,
          border: '3px solid rgba(59, 130, 246, 0.4)',
        }}>
          <img src="./assets/qr.png" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        </div>
        <div style={{ fontSize: 24, color: muted, marginTop: 12 }}>扫码加群</div>
      </div>
    </div>
  </div>
);

// ─── CLOSING ────────────────────────────────────────────
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
      padding: '0 100px',
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    <div style={{ position: 'absolute', top: -60, right: 80, width: 350, height: 350, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.04)', border: '1px solid rgba(59, 130, 246, 0.06)' }} />

    <div style={{ fontSize: 28, color: accent, letterSpacing: '0.3em', marginBottom: 32 }}>📖 清华大学出版社</div>
    <h1 style={{ fontSize: 80, fontWeight: 900, margin: '0 0 24px 0', textAlign: 'center', background: 'linear-gradient(90deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
      《Manus智能体全攻略》
    </h1>
    <p style={{ fontSize: 34, color: muted, textAlign: 'center', marginBottom: 56 }}>
      AI赋能高校教学新范式 · 小龙虾 + Manus 一站式解决方案
    </p>

    <div style={{ display: 'flex', gap: 64, alignItems: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 44, fontWeight: 900, color: accentLight }}>6月24日</div>
        <div style={{ fontSize: 26, color: muted }}>下午 3:00-4:00</div>
      </div>
      <div style={{ width: 3, height: 80, background: accent, borderRadius: 2 }} />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 30, fontWeight: 700, marginBottom: 8 }}>诸葛斌 教授</div>
        <div style={{ fontSize: 22, color: muted }}>浙江工商大学 · 萨塞克斯人工智能学院</div>
        <div style={{ fontSize: 20, color: muted, marginTop: 4 }}>2025全国高校人工智能教育大会优秀案例一等奖</div>
      </div>
    </div>

    {/* QR code */}
    <div style={{ marginTop: 56, textAlign: 'center' }}>
      <div style={{
        width: 180, height: 180, borderRadius: 16, overflow: 'hidden',
        background: '#fff', padding: 10,
        border: '2px solid rgba(59, 130, 246, 0.3)',
      }}>
        <img src="./assets/qr.png" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
      </div>
      <div style={{ fontSize: 22, color: muted, marginTop: 10 }}>扫码加入读者服务群</div>
    </div>
  </div>
);

export const meta: SlideMeta = { title: 'Manus直播海报' };
export default [Cover, Scenarios, Benefits, Closing] satisfies Page[];

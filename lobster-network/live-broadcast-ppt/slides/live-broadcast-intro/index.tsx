import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

export const design: DesignSystem = {
  palette: { bg: '#0b1120', text: '#f0f4f8', accent: '#3b82f6' },
  fonts: {
    display: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif',
    body: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  typeScale: { hero: 140, body: 36 },
  radius: 12,
};

const muted = '#94a3b8';
const accent = '#3b82f6';
const text = 'var(--osd-text)';

const fill = { width: '100%', height: '100%' } as const;

/* ─── Page 1: Cover ─── */
const Cover: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(160deg, #0b1120 0%, #1e3a5f 40%, #0b1120 100%)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 120px',
    }}
  >
    <div
      style={{
        fontSize: 24,
        color: '#60a5fa',
        letterSpacing: '0.3em',
        fontWeight: 600,
        marginBottom: 32,
      }}
    >
      直播课程
    </div>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 80,
        fontWeight: 900,
        lineHeight: 1.15,
        margin: '0 0 24px 0',
        textAlign: 'center',
        letterSpacing: '-0.02em',
        color: '#f0f4f8',
      }}
    >
      智能体赋能高校教学新范式
    </h1>
    <h2
      style={{
        fontSize: 48,
        fontWeight: 600,
        margin: '0 0 48px 0',
        textAlign: 'center',
        color: accent,
      }}
    >
      小龙虾 + Manus 一站式解决方案
    </h2>
    <div style={{ display: 'flex', gap: 48, alignItems: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 22, color: muted }}>主讲人</div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4 }}>诸葛斌 教授</div>
      </div>
      <div style={{ width: 2, height: 48, background: 'rgba(255,255,255,0.15)' }} />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 22, color: muted }}>时间</div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4 }}>6月27日 周五 15:00</div>
      </div>
    </div>
    <div style={{ marginTop: 48, fontSize: 24, color: muted }}>
      《Manus智能体全攻略》· 清华大学出版社
    </div>
  </div>
);

/* ─── Page 2: Book Intro ─── */
const BookIntro: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 140px',
    }}
  >
    <div style={{ fontSize: 22, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      所用图书
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        margin: '32px 0 40px 0',
      }}
    >
      《Manus智能体全攻略》
    </h2>
    <div style={{ display: 'flex', gap: 40, alignItems: 'flex-start' }}>
      <div style={{ flex: 1 }}>
        {[
          { label: '出版社', value: '清华大学出版社' },
          { label: '作者', value: '诸葛斌 等' },
          { label: '定位', value: '国内首本智能体教学实战指南' },
        ].map((item) => (
          <div key={item.label} style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 22, color: muted, marginBottom: 4 }}>{item.label}</div>
            <div style={{ fontSize: 36, fontWeight: 600 }}>{item.value}</div>
          </div>
        ))}
      </div>
      <div
        style={{
          width: 240,
          height: 320,
          background: 'linear-gradient(135deg, #1e3a5f, #2563eb)',
          borderRadius: 12,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 24,
          flexShrink: 0,
        }}
      >
        <div style={{ fontSize: 48, marginBottom: 12 }}>📘</div>
        <div style={{ fontSize: 28, fontWeight: 700, textAlign: 'center', lineHeight: 1.3 }}>
          Manus智能体<br />全攻略
        </div>
        <div style={{ fontSize: 18, color: muted, marginTop: 12 }}>清华大学出版社</div>
      </div>
    </div>
  </div>
);

/* ─── Page 3: Broadcast Content ─── */
const Content: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 22, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      直播内容
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        margin: '32px 0 24px 0',
      }}
    >
      解读 + 实操，一次搞定
    </h2>
    <p style={{ fontSize: 32, color: muted, margin: '0 0 48px 0', lineHeight: 1.7 }}>
      解读清华版《Manus智能体全攻略》，现场演示五大教学场景，
      实操 2 小时教案制作压缩至 <span style={{ color: '#60a5fa', fontWeight: 700 }}>10 分钟</span>
    </p>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
      {[
        { icon: '📚', title: '课件智能生成', desc: '"小龙虾三部曲"精品课件' },
        { icon: '🔬', title: '教学案例开发', desc: '烟草数据挖掘、网络课程动画等' },
        { icon: '📝', title: '论文协作写作', desc: '从选题到 IEEE 成稿全流程' },
        { icon: '🎬', title: '教学视频制作', desc: 'PPT 自动转教学视频' },
      ].map((item) => (
        <div
          key={item.title}
          style={{
            padding: '28px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 44 }}>{item.icon}</div>
          <div style={{ fontSize: 32, fontWeight: 700, marginTop: 8 }}>{item.title}</div>
          <div style={{ fontSize: 26, color: muted, marginTop: 6 }}>{item.desc}</div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 4: 5 Scenarios ─── */
const Scenarios: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 22, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      五大教学场景
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        margin: '32px 0 48px 0',
      }}
    >
      从课件到视频，全流程覆盖
    </h2>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {[
        { num: '01', title: '课件智能生成', detail: '"小龙虾三部曲"精品课件自动化生成' },
        { num: '02', title: '教学案例开发', detail: '烟草数据挖掘案例 · 网络课程动画 · 微信小程序实战' },
        { num: '03', title: '论文协作写作', detail: '从选题到 IEEE 成稿，全流程 AI 辅助' },
        { num: '04', title: '教学视频制作', detail: 'PPT 自动转教学视频，无需专业剪辑' },
        { num: '05', title: '教案快速制作', detail: '2 小时教案制作压缩至 10 分钟' },
      ].map((item) => (
        <div
          key={item.num}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 28,
            padding: '20px 28px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 28, fontWeight: 800, color: accent, minWidth: 60 }}>
            {item.num}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 36, fontWeight: 700 }}>{item.title}</div>
            <div style={{ fontSize: 26, color: muted, marginTop: 4 }}>{item.detail}</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 5: Author ─── */
const Author: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 140px',
    }}
  >
    <div style={{ fontSize: 22, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      主讲人
    </div>
    <div style={{ display: 'flex', gap: 48, marginTop: 40, alignItems: 'center' }}>
      <div
        style={{
          width: 200,
          height: 260,
          background: 'linear-gradient(135deg, #1e3a5f, #2563eb)',
          borderRadius: 16,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          flexShrink: 0,
        }}
      >
        <div style={{ fontSize: 64 }}>👤</div>
        <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>诸葛斌</div>
      </div>
      <div style={{ flex: 1 }}>
        <h2
          style={{
            fontSize: 56,
            fontWeight: 800,
            margin: '0 0 8px 0',
          }}
        >
          诸葛斌 教授
        </h2>
        <div style={{ fontSize: 28, color: accent, marginBottom: 24 }}>
          浙江工商大学 · 信息与电子工程学院 / 萨塞克斯人工智能学院
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            '研究方向：互联网应用开发与 AI 教育',
            '获浙江省技术发明一等奖',
            '联合阿里钉钉撰写国内首本低代码开发教材',
            '获 2025 全国高校人工智能教育大会优秀案例一等奖',
          ].map((item) => (
            <div
              key={item}
              style={{
                fontSize: 28,
                color: muted,
                paddingLeft: 20,
                borderLeft: '3px solid #3b82f6',
              }}
            >
              {item}
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

/* ─── Page 6: Benefits ─── */
const Benefits: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: text,
      padding: 120,
    }}
  >
    <div style={{ fontSize: 22, color: accent, letterSpacing: '0.2em', fontWeight: 600 }}>
      入群福利
    </div>
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 800,
        margin: '32px 0 16px 0',
      }}
    >
      扫码加入读者服务群
    </h2>
    <p style={{ fontSize: 28, color: muted, margin: '0 0 48px 0' }}>
      此群长期有效，群成员可获得以下福利
    </p>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
      {[
        {
          icon: '🤖',
          title: '小龙虾 AI 体验',
          desc: '群内部署 OpenClaw 智能体，实时体验课件生成、教案制作等 AI 能力',
        },
        {
          icon: '📦',
          title: '教学资料包',
          desc: '小龙虾三部曲课件、数据挖掘案例、16 章教学动画、微信小程序案例等全套 Manus 实战案例',
        },
        {
          icon: '🎁',
          title: '免费样书抽奖',
          desc: '直播间专享 10 本《Manus智能体全攻略》免费样书赠送（名额有限，抽奖获得）',
        },
        {
          icon: '💬',
          title: '教学交流社区',
          desc: '"智能体"系列课程教学交流社区——高校教师 AI 教学实践交流、问题解答、经验分享',
        },
      ].map((item) => (
        <div
          key={item.title}
          style={{
            padding: '28px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{ fontSize: 44 }}>{item.icon}</div>
          <div style={{ fontSize: 32, fontWeight: 700, marginTop: 8 }}>{item.title}</div>
          <div style={{ fontSize: 26, color: muted, marginTop: 6, lineHeight: 1.5 }}>
            {item.desc}
          </div>
        </div>
      ))}
    </div>
  </div>
);

/* ─── Page 7: Closing ─── */
const Closing: Page = () => (
  <div
    style={{
      ...fill,
      background: 'linear-gradient(160deg, #0b1120 0%, #1e3a5f 40%, #0b1120 100%)',
      color: text,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 120px',
    }}
  >
    <div style={{ fontSize: 24, color: '#60a5fa', letterSpacing: '0.3em', fontWeight: 600 }}>
      敬请期待
    </div>
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 72,
        fontWeight: 900,
        lineHeight: 1.15,
        margin: '32px 0 24px 0',
        textAlign: 'center',
      }}
    >
      智能体赋能高校教学新范式
    </h1>
    <h2
      style={{
        fontSize: 40,
        fontWeight: 600,
        margin: '0 0 48px 0',
        color: accent,
      }}
    >
      小龙虾 + Manus 一站式解决方案
    </h2>
    <div style={{ display: 'flex', gap: 48, alignItems: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 22, color: muted }}>📅 日期</div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4 }}>6月27日 周五</div>
      </div>
      <div style={{ width: 2, height: 48, background: 'rgba(255,255,255,0.15)' }} />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 22, color: muted }}>⏰ 时间</div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4 }}>下午 15:00 - 16:00</div>
      </div>
      <div style={{ width: 2, height: 48, background: 'rgba(255,255,255,0.15)' }} />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 22, color: muted }}>👤 主讲人</div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 4 }}>诸葛斌 教授</div>
      </div>
    </div>
    <div
      style={{
        marginTop: 56,
        padding: '24px 40px',
        background: 'rgba(59,130,246,0.1)',
        borderRadius: 12,
        border: '1px solid rgba(59,130,246,0.3)',
      }}
    >
      <div style={{ fontSize: 32, fontWeight: 600, color: '#60a5fa' }}>
        📱 请提前扫码加入读者服务群
      </div>
      <div style={{ fontSize: 24, color: muted, marginTop: 8 }}>
        享 4 大专属福利 · 群长期有效
      </div>
    </div>
  </div>
);

export const meta: SlideMeta = { title: '直播课程介绍 - 智能体赋能高校教学新范式' };
export default [Cover, BookIntro, Content, Scenarios, Author, Benefits, Closing] satisfies Page[];

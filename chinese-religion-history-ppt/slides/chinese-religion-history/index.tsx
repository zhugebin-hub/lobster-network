import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';

export const design: DesignSystem = {
  palette: { bg: '#0c1929', text: '#f0ead6', accent: '#c9a961' },
  fonts: {
    display: '"Noto Serif SC", "Source Han Serif SC", "SimSun", system-ui, serif',
    body: '"Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", system-ui, sans-serif',
  },
  typeScale: { hero: 120, body: 36 },
  radius: 12,
};

const muted = '#8a9bb5';
const accentLight = '#d4b978';
const cardBg = 'rgba(201, 169, 97, 0.08)';
const cardBorder = 'rgba(201, 169, 97, 0.25)';

const fill = {
  width: '100%',
  height: '100%',
  fontFamily: 'var(--osd-font-body)',
} as const;

/* ===== Slide 1: Cover ===== */
const Cover: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
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
    {/* Decorative top line */}
    <div style={{
      position: 'absolute', top: 80, left: '50%', transform: 'translateX(-50%)',
      width: 120, height: 3, background: 'var(--osd-accent)',
    }} />
    {/* Decorative bottom line */}
    <div style={{
      position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)',
      width: 120, height: 3, background: 'var(--osd-accent)',
    }} />

    <div style={{
      fontSize: 32, color: 'var(--osd-accent)', letterSpacing: '0.3em',
      fontWeight: 500, marginTop: 100,
    }}>
      佛教 · 果顺
    </div>

    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 100,
        fontWeight: 900,
        margin: '48px 0 32px 0',
        lineHeight: 1.2,
        textAlign: 'center',
        maxWidth: 1400,
      }}
    >
      中国宗教史的<br />历史逻辑与规律性特征
    </h1>

    <p style={{
      fontSize: 40, color: muted, maxWidth: 1200, textAlign: 'center',
      lineHeight: 1.6,
    }}>
      ——以政教关系与宗教中国化为主线
    </p>
  </div>
);

/* ===== Slide 2: Agenda ===== */
const Agenda: Page = () => {
  const items = [
    { num: '壹', title: '政教关系的权力结构', sub: '国家主导下的宗教生存逻辑' },
    { num: '贰', title: '宗教中国化的历史必然', sub: '从"外来"到"本土"的文化适应' },
    { num: '叁', title: '三教融合的文化逻辑', sub: '和而不同的中国智慧' },
    { num: '肆', title: '宗教兴衰的周期律', sub: '盛世兴教与乱世避祸' },
    { num: '伍', title: '宗教与社会治理', sub: '从"消极避世"到"积极入世"' },
  ];

  return (
    <div style={{
      ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
      padding: '120px 140px',
    }}>
      <div style={{
        fontSize: 28, color: 'var(--osd-accent)', letterSpacing: '0.25em',
        fontWeight: 600, marginBottom: 16,
      }}>
        目 录
      </div>
      <h2 style={{
        fontFamily: 'var(--osd-font-display)', fontSize: 72, fontWeight: 800,
        margin: '0 0 56px 0', lineHeight: 1.2,
      }}>
        五条规律概览
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
        {items.map((item, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 32,
            padding: '20px 36px',
            background: cardBg,
            border: `1px solid ${cardBorder}`,
            borderRadius: 12,
          }}>
            <span style={{
              fontSize: 40, fontWeight: 800, color: 'var(--osd-accent)',
              width: 60, textAlign: 'center', flexShrink: 0,
              fontFamily: 'var(--osd-font-display)',
            }}>
              {item.num}
            </span>
            <div>
              <div style={{ fontSize: 36, fontWeight: 700, lineHeight: 1.3 }}>
                {item.title}
              </div>
              <div style={{ fontSize: 26, color: muted, marginTop: 4 }}>
                {item.sub}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ===== Slide 3: 规律一 政教关系 ===== */
const Law1: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <div style={{
      fontSize: 26, color: 'var(--osd-accent)', letterSpacing: '0.2em',
      fontWeight: 600, marginBottom: 12,
    }}>
      规律一
    </div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 48px 0', lineHeight: 1.2,
    }}>
      政教关系的权力结构
    </h2>
    <p style={{
      fontSize: 32, color: accentLight, marginBottom: 40, lineHeight: 1.4,
    }}>
      国家主导下的宗教生存逻辑
    </p>

    {/* Two columns */}
    <div style={{ display: 'flex', gap: 64 }}>
      {/* Left column */}
      <div style={{ flex: 1 }}>
        <h3 style={{
          fontSize: 34, fontWeight: 700, marginBottom: 24, color: accentLight,
        }}>
          历史证据
        </h3>
        <ul style={{
          fontSize: 30, lineHeight: 1.7, paddingLeft: 28, color: 'var(--osd-text)',
        }}>
          <li style={{ marginBottom: 16 }}>汉武帝"罢黜百家，独尊儒术"——确立国家意识形态</li>
          <li style={{ marginBottom: 16 }}>北魏太武帝、唐武宗、北周武帝三次灭佛——皇权直接干预</li>
          <li style={{ marginBottom: 16 }}>梁武帝受菩萨戒、宋徽宗崇道排佛——皇权扶持与打压并存</li>
          <li style={{ marginBottom: 16 }}>新中国各宗教爱国组织相继成立——国家框架内合法存在</li>
        </ul>
      </div>

      {/* Right column - quote card */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
        padding: '48px 40px', background: cardBg, borderRadius: 16,
        border: `1px solid ${cardBorder}`,
      }}>
        <div style={{
          fontSize: 80, fontFamily: 'var(--osd-font-display)', color: 'var(--osd-accent)',
          lineHeight: 1, marginBottom: 16,
        }}>
          "
        </div>
        <p style={{
          fontSize: 40, fontWeight: 700, lineHeight: 1.5, color: 'var(--osd-text)',
          fontFamily: 'var(--osd-font-display)',
        }}>
          不依国主，<br />则法事难立
        </p>
        <p style={{
          fontSize: 28, color: muted, marginTop: 20, textAlign: 'right',
        }}>
          —— 道安
        </p>
      </div>
    </div>

    {/* Bottom key takeaway */}
    <div style={{
      marginTop: 40, padding: '24px 36px',
      background: 'rgba(201, 169, 97, 0.12)', borderRadius: 10,
      borderLeft: '4px solid var(--osd-accent)',
    }}>
      <p style={{ fontSize: 30, lineHeight: 1.5, margin: 0 }}>
        <strong>核心结论：</strong>宗教不是脱离社会的独立王国，而是在国家法律和政策框架内运作的社会子系统。
      </p>
    </div>
  </div>
);

/* ===== Slide 4: 规律二 宗教中国化 ===== */
const Law2: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <div style={{
      fontSize: 26, color: 'var(--osd-accent)', letterSpacing: '0.2em',
      fontWeight: 600, marginBottom: 12,
    }}>
      规律二
    </div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 48px 0', lineHeight: 1.2,
    }}>
      宗教中国化的历史必然
    </h2>
    <p style={{
      fontSize: 32, color: accentLight, marginBottom: 44, lineHeight: 1.4,
    }}>
      从"外来"到"本土"的文化适应
    </p>

    {/* Timeline style */}
    <div style={{ display: 'flex', gap: 36, justifyContent: 'space-between' }}>
      {[
        { era: '两汉之际', title: '佛教传入', desc: '依附道家方术\n以"格义"释佛理' },
        { era: '魏晋时期', title: '玄学奠基', desc: '玄学流行为佛教\n传播奠定基础' },
        { era: '隋唐', title: '完成转变', desc: '天台宗创立\n第一个中国化宗派' },
        { era: '唐代', title: '禅宗兴起', desc: '惠能顿悟法门\n直指人心，契合中国思维' },
      ].map((item, i) => (
        <div key={i} style={{
          flex: 1, padding: '32px 24px', background: cardBg,
          border: `1px solid ${cardBorder}`, borderRadius: 14,
          textAlign: 'center',
        }}>
          <div style={{
            fontSize: 24, color: 'var(--osd-accent)', fontWeight: 700,
            letterSpacing: '0.15em', marginBottom: 12,
          }}>
            {item.era}
          </div>
          <div style={{
            fontSize: 34, fontWeight: 800, marginBottom: 16,
            fontFamily: 'var(--osd-font-display)',
          }}>
            {item.title}
          </div>
          <div style={{
            fontSize: 24, color: muted, lineHeight: 1.6, whiteSpace: 'pre-line',
          }}>
            {item.desc}
          </div>
        </div>
      ))}
    </div>

    {/* Bottom note */}
    <div style={{
      marginTop: 44, padding: '24px 36px',
      background: 'rgba(201, 169, 97, 0.12)', borderRadius: 10,
      borderLeft: '4px solid var(--osd-accent)',
    }}>
      <p style={{ fontSize: 30, lineHeight: 1.5, margin: 0 }}>
        <strong>核心结论：</strong>宗教中国化不是外在的政治要求，而是宗教在中国生存发展的<strong>内在需要</strong>。
      </p>
    </div>
  </div>
);

/* ===== Slide 5: 规律三 三教融合 ===== */
const Law3: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <div style={{
      fontSize: 26, color: 'var(--osd-accent)', letterSpacing: '0.2em',
      fontWeight: 600, marginBottom: 12,
    }}>
      规律三
    </div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 48px 0', lineHeight: 1.2,
    }}>
      三教融合的文化逻辑
    </h2>
    <p style={{
      fontSize: 32, color: accentLight, marginBottom: 44, lineHeight: 1.4,
    }}>
      和而不同的中国智慧
    </p>

    {/* Three pillars */}
    <div style={{ display: 'flex', gap: 40, marginBottom: 48 }}>
      {[
        { name: '儒', color: '#c9a961', desc: '入世精神\n经世致用' },
        { name: '释', color: '#7eb8c9', desc: '明心见性\n慈悲济世' },
        { name: '道', color: '#8bc97e', desc: '道法自然\n清静无为' },
      ].map((religion, i) => (
        <div key={i} style={{
          flex: 1, textAlign: 'center',
          padding: '40px 24px', background: cardBg, borderRadius: 14,
          border: `2px solid ${religion.color}40`,
        }}>
          <div style={{
            fontSize: 80, fontWeight: 900, fontFamily: 'var(--osd-font-display)',
            color: religion.color, marginBottom: 16, lineHeight: 1,
          }}>
            {religion.name}
          </div>
          <div style={{
            fontSize: 28, color: muted, lineHeight: 1.7, whiteSpace: 'pre-line',
          }}>
            {religion.desc}
          </div>
        </div>
      ))}
    </div>

    {/* Historical examples */}
    <div style={{ display: 'flex', gap: 36 }}>
      {[
        { period: '魏晋南北朝', content: '佛道竞争互鉴，佛教吸收道教修行方法，道教借鉴佛教教义体系' },
        { period: '唐宋', content: '白居易、柳宗元兼融三教；延寿编《宗镜录》倡"禅教合一"' },
        { period: '明代', content: '王阳明心学受禅宗影响；晚明四大高僧主张三教一致' },
      ].map((ex, i) => (
        <div key={i} style={{
          flex: 1, padding: '24px 28px',
          background: cardBg, borderRadius: 12,
          border: `1px solid ${cardBorder}`,
        }}>
          <div style={{
            fontSize: 24, color: 'var(--osd-accent)', fontWeight: 700,
            marginBottom: 10,
          }}>
            {ex.period}
          </div>
          <div style={{ fontSize: 26, color: 'var(--osd-text)', lineHeight: 1.5 }}>
            {ex.content}
          </div>
        </div>
      ))}
    </div>

    {/* Key phrase */}
    <div style={{
      marginTop: 36, textAlign: 'center',
      fontSize: 36, fontWeight: 700, color: accentLight,
      fontFamily: 'var(--osd-font-display)',
    }}>
      "道并行而不相悖" —— 中国文化的包容性
    </div>
  </div>
);

/* ===== Slide 6: 规律四 兴衰周期律 ===== */
const Law4: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <div style={{
      fontSize: 26, color: 'var(--osd-accent)', letterSpacing: '0.2em',
      fontWeight: 600, marginBottom: 12,
    }}>
      规律四
    </div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 48px 0', lineHeight: 1.2,
    }}>
      宗教兴衰的周期律
    </h2>
    <p style={{
      fontSize: 32, color: accentLight, marginBottom: 44, lineHeight: 1.4,
    }}>
      盛世兴教与乱世避祸
    </p>

    {/* Two columns: prosperity vs decline */}
    <div style={{ display: 'flex', gap: 48 }}>
      {/* Prosperity */}
      <div style={{
        flex: 1, padding: '36px 32px',
        background: 'rgba(139, 201, 126, 0.1)',
        border: '1px solid rgba(139, 201, 126, 0.3)',
        borderRadius: 14,
      }}>
        <div style={{
          fontSize: 44, fontWeight: 800, color: '#8bc97e',
          marginBottom: 24, fontFamily: 'var(--osd-font-display)',
        }}>
          ▲ 盛世兴教
        </div>
        <ul style={{
          fontSize: 28, lineHeight: 1.8, paddingLeft: 24, color: 'var(--osd-text)',
        }}>
          <li style={{ marginBottom: 12 }}>唐代佛教鼎盛：玄奘译经、武则天推崇</li>
          <li style={{ marginBottom: 12 }}>禅宗分灯，五家七宗蔚为大观</li>
          <li style={{ marginBottom: 12 }}>国力强盛，文化繁荣</li>
          <li style={{ marginBottom: 12 }}>改革开放后：寺观恢复，宗教教育重建</li>
        </ul>
      </div>

      {/* Decline */}
      <div style={{
        flex: 1, padding: '36px 32px',
        background: 'rgba(201, 126, 126, 0.1)',
        border: '1px solid rgba(201, 126, 126, 0.3)',
        borderRadius: 14,
      }}>
        <div style={{
          fontSize: 44, fontWeight: 800, color: '#c97e7e',
          marginBottom: 24, fontFamily: 'var(--osd-font-display)',
        }}>
          ▼ 乱世受挫
        </div>
        <ul style={{
          fontSize: 28, lineHeight: 1.8, paddingLeft: 24, color: 'var(--osd-text)',
        }}>
          <li style={{ marginBottom: 12 }}>"三武一宗"灭佛——社会动荡期</li>
          <li style={{ marginBottom: 12 }}>太平天国冲击传统宗教</li>
          <li style={{ marginBottom: 12 }}>义和团运动冲击天主教、基督教</li>
          <li style={{ marginBottom: 12 }}>"文革"期间：宗教活动全面停滞</li>
        </ul>
      </div>
    </div>

    {/* Bottom takeaway */}
    <div style={{
      marginTop: 40, padding: '24px 36px',
      background: 'rgba(201, 169, 97, 0.12)', borderRadius: 10,
      borderLeft: '4px solid var(--osd-accent)',
    }}>
      <p style={{ fontSize: 30, lineHeight: 1.5, margin: 0 }}>
        <strong>核心结论：</strong>宗教的健康发展离不开国家的<strong>长治久安</strong>。
      </p>
    </div>
  </div>
);

/* ===== Slide 7: 规律五 社会治理 ===== */
const Law5: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <div style={{
      fontSize: 26, color: 'var(--osd-accent)', letterSpacing: '0.2em',
      fontWeight: 600, marginBottom: 12,
    }}>
      规律五
    </div>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 48px 0', lineHeight: 1.2,
    }}>
      宗教与社会治理
    </h2>
    <p style={{
      fontSize: 32, color: accentLight, marginBottom: 44, lineHeight: 1.4,
    }}>
      从"消极避世"到"积极入世"
    </p>

    {/* Evolution arrow */}
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 24, marginBottom: 48,
    }}>
      <div style={{
        padding: '20px 36px', background: 'rgba(201, 126, 126, 0.15)',
        borderRadius: 12, border: '1px solid rgba(201, 126, 126, 0.3)',
        fontSize: 32, fontWeight: 700, color: '#c97e7e',
      }}>
        出世倾向
      </div>
      <div style={{ fontSize: 48, color: muted }}>→</div>
      <div style={{
        padding: '20px 36px', background: 'rgba(201, 169, 97, 0.15)',
        borderRadius: 12, border: '1px solid var(--osd-accent)',
        fontSize: 32, fontWeight: 700, color: 'var(--osd-accent)',
      }}>
        入世参与
      </div>
    </div>

    {/* Historical evidence */}
    <div style={{ display: 'flex', gap: 36 }}>
      {[
        {
          title: '佛教公益',
          items: ['南北朝：寺院设"无尽藏"借贷救济', '唐代："悲田院"收容孤寡残疾', '宋代：赈灾、施医、修桥铺路'],
        },
        {
          title: '道教实践',
          items: ['《太平经》"太平"社会理想', '全真道"真功真行"——修行与社会实践结合'],
        },
        {
          title: '当代发展',
          items: ['太虚大师"人生佛教"→"人间佛教"', '慈善、教育、生态全面参与', '2021全国宗教工作会议：宗教是社会治理"参与者"'],
        },
      ].map((col, i) => (
        <div key={i} style={{
          flex: 1, padding: '28px 28px',
          background: cardBg, borderRadius: 14,
          border: `1px solid ${cardBorder}`,
        }}>
          <div style={{
            fontSize: 32, fontWeight: 800, color: 'var(--osd-accent)',
            marginBottom: 20, fontFamily: 'var(--osd-font-display)',
          }}>
            {col.title}
          </div>
          <ul style={{
            fontSize: 26, lineHeight: 1.8, paddingLeft: 22, color: 'var(--osd-text)',
          }}>
            {col.items.map((item, j) => (
              <li key={j} style={{ marginBottom: 10 }}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  </div>
);

/* ===== Slide 8: Conclusion ===== */
const Conclusion: Page = () => (
  <div style={{
    ...fill, background: 'var(--osd-bg)', color: 'var(--osd-text)',
    padding: '100px 140px',
  }}>
    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 64, fontWeight: 800,
      margin: '0 0 52px 0', lineHeight: 1.2, textAlign: 'center',
    }}>
      结语
    </h2>

    {/* Five laws summary */}
    <div style={{
      display: 'flex', flexWrap: 'wrap', gap: 20, justifyContent: 'center',
      marginBottom: 52,
    }}>
      {[
        '国家主导的\n政教关系格局',
        '宗教中国化的\n历史必然',
        '三教融合的\n文化逻辑',
        '宗教兴衰的\n周期律',
        '宗教在社会治理中的\n角色演变',
      ].map((item, i) => (
        <div key={i} style={{
          width: 280, padding: '28px 24px', textAlign: 'center',
          background: cardBg, borderRadius: 12,
          border: `1px solid ${cardBorder}`,
        }}>
          <div style={{
            fontSize: 48, fontWeight: 900, color: 'var(--osd-accent)',
            fontFamily: 'var(--osd-font-display)', marginBottom: 12,
          }}>
            {['壹', '贰', '叁', '肆', '伍'][i]}
          </div>
          <div style={{ fontSize: 26, lineHeight: 1.5, whiteSpace: 'pre-line' }}>
            {item}
          </div>
        </div>
      ))}
    </div>

    {/* Key quotes */}
    <div style={{
      padding: '32px 40px', background: 'rgba(201, 169, 97, 0.1)',
      borderRadius: 14, borderLeft: '4px solid var(--osd-accent)',
    }}>
      <p style={{ fontSize: 30, lineHeight: 1.7, margin: '0 0 16px 0' }}>
        宗教中国化不是今天才提出的新命题，而是<strong>千年不变的历史趋势</strong>。
      </p>
      <p style={{ fontSize: 30, lineHeight: 1.7, margin: 0 }}>
        周恩来总理明确指出：<strong>到了共产主义社会仍然有可能存在宗教。</strong>
      </p>
    </div>
  </div>
);

/* ===== Slide 9: Closing ===== */
const Closing: Page = () => (
  <div
    style={{
      ...fill,
      background: 'var(--osd-bg)',
      color: 'var(--osd-text)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '0 160px',
      position: 'relative',
    }}
  >
    <div style={{
      position: 'absolute', top: 80, left: '50%', transform: 'translateX(-50%)',
      width: 120, height: 3, background: 'var(--osd-accent)',
    }} />

    <h2 style={{
      fontFamily: 'var(--osd-font-display)', fontSize: 100, fontWeight: 900,
      margin: '0 0 32px 0', lineHeight: 1.2,
    }}>
      感谢聆听
    </h2>

    <p style={{
      fontSize: 36, color: muted, marginBottom: 64,
    }}>
      敬请批评指正
    </p>

    <div style={{
      padding: '28px 48px', background: cardBg, borderRadius: 14,
      border: `1px solid ${cardBorder}`, textAlign: 'center',
    }}>
      <p style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
        果顺
      </p>
      <p style={{ fontSize: 26, color: muted, margin: 0 }}>
        中国宗教史纲要 · 学习总结
      </p>
    </div>

    <div style={{
      position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)',
      width: 120, height: 3, background: 'var(--osd-accent)',
    }} />
  </div>
);

export const meta: SlideMeta = { title: '中国宗教史的历史逻辑与规律性特征' };
export default [Cover, Agenda, Law1, Law2, Law3, Law4, Law5, Conclusion, Closing] satisfies Page[];

#!/usr/bin/env python3
"""生成直播宣传海报 HTML 文件"""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<title>Manus智能体全攻略 直播海报</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px;
    height: 1920px;
    font-family: "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
    background: linear-gradient(160deg, #0a1628 0%, #0f2847 40%, #0a1628 70%, #1a0a28 100%);
    color: #e8ecf1;
    overflow: hidden;
    position: relative;
  }
  /* Decorative circles */
  .circle1 {
    position: absolute; top: -120px; right: -100px;
    width: 500px; height: 500px; border-radius: 50%;
    background: rgba(59, 130, 246, 0.06);
    border: 1px solid rgba(59, 130, 246, 0.1);
  }
  .circle2 {
    position: absolute; bottom: -80px; left: -60px;
    width: 380px; height: 380px; border-radius: 50%;
    background: rgba(16, 185, 129, 0.04);
    border: 1px solid rgba(16, 185, 129, 0.08);
  }
  .circle3 {
    position: absolute; top: 50%; right: -150px;
    width: 400px; height: 400px; border-radius: 50%;
    background: rgba(167, 139, 250, 0.04);
    border: 1px solid rgba(167, 139, 250, 0.08);
  }
  .content {
    position: relative; z-index: 1;
    padding: 80px 60px 60px;
    display: flex; flex-direction: column;
    height: 100%;
  }
  /* Top badge */
  .badge {
    align-self: center;
    padding: 14px 50px;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 40px;
    font-size: 28px;
    color: #60a5fa;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 40px;
  }
  /* Main title */
  .title {
    text-align: center;
    font-size: 76px;
    font-weight: 900;
    line-height: 1.2;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
  }
  .subtitle {
    text-align: center;
    font-size: 38px;
    color: #7a8ba3;
    margin-bottom: 40px;
    font-weight: 500;
  }
  .divider {
    width: 140px; height: 4px;
    background: linear-gradient(90deg, #3b82f6, #a78bfa);
    border-radius: 2px;
    margin: 0 auto 40px;
  }
  /* Scenarios */
  .scenarios {
    display: flex; flex-direction: column; gap: 22px;
    margin-bottom: 40px;
  }
  .scenario {
    display: flex; align-items: center; gap: 24px;
    padding: 22px 30px;
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 16px;
  }
  .scenario-icon { font-size: 44px; width: 64px; text-align: center; }
  .scenario-line { width: 4px; height: 50px; border-radius: 2px; }
  .scenario-title { font-size: 34px; font-weight: 800; margin-bottom: 4px; }
  .scenario-desc { font-size: 24px; color: #7a8ba3; }
  /* Benefits */
  .benefits-title {
    text-align: center; font-size: 26px; color: #10b981;
    letter-spacing: 0.3em; font-weight: 600; margin-bottom: 8px;
  }
  .benefits-heading {
    text-align: center; font-size: 44px; font-weight: 900; margin-bottom: 20px;
  }
  .benefits-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
    margin-bottom: 40px;
  }
  .benefit {
    padding: 24px 22px;
    background: rgba(59, 130, 246, 0.06);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 14px;
  }
  .benefit-head { display: flex; align-items: center; gap: 14px; margin-bottom: 10px; }
  .benefit-icon { font-size: 36px; }
  .benefit-name { font-size: 28px; font-weight: 800; }
  .benefit-desc { font-size: 20px; color: #7a8ba3; line-height: 1.5; }
  /* Bottom */
  .bottom {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: auto;
  }
  .bottom-left { display: flex; align-items: center; gap: 24px; }
  .author-photo {
    width: 90px; height: 90px; border-radius: 50%; overflow: hidden;
    border: 3px solid rgba(59, 130, 246, 0.4);
    background: #1a2a4a;
    display: flex; align-items: center; justify-content: center;
  }
  .author-photo img { width: 100%; height: 100%; object-fit: cover; }
  .author-name { font-size: 28px; font-weight: 700; }
  .author-org { font-size: 20px; color: #7a8ba3; }
  .author-award { font-size: 16px; color: #f59e0b; margin-top: 4px; }
  .bottom-center { text-align: center; }
  .date-big { font-size: 52px; font-weight: 900; color: #60a5fa; }
  .date-time { font-size: 24px; color: #7a8ba3; }
  .qr-block { text-align: center; }
  .qr-img {
    width: 160px; height: 160px; border-radius: 14px;
    background: #fff; padding: 8px;
    border: 2px solid rgba(59, 130, 246, 0.3);
    overflow: hidden;
  }
  .qr-img img { width: 100%; height: 100%; object-fit: contain; }
  .qr-label { font-size: 20px; color: #7a8ba3; margin-top: 8px; }
</style>
</head>
<body>
<div class="circle1"></div>
<div class="circle2"></div>
<div class="circle3"></div>
<div class="content">
  <!-- Badge -->
  <div class="badge">清华大学出版社 · 重磅新书</div>

  <!-- Title -->
  <div class="title">智能体赋能高校教学新范式</div>
  <div class="subtitle">小龙虾 + Manus 一站式解决方案</div>
  <div class="divider"></div>

  <!-- Five Scenarios -->
  <div class="scenarios">
    <div class="scenario">
      <div class="scenario-icon">📄</div>
      <div class="scenario-line" style="background:#3b82f6"></div>
      <div><div class="scenario-title">课件智能生成</div><div class="scenario-desc">"小龙虾三部曲"精品课件</div></div>
    </div>
    <div class="scenario">
      <div class="scenario-icon">🌿</div>
      <div class="scenario-line" style="background:#10b981"></div>
      <div><div class="scenario-title">教学案例开发</div><div class="scenario-desc">烟草数据挖掘、网络课程动画、微信小程序等</div></div>
    </div>
    <div class="scenario">
      <div class="scenario-icon">✍️</div>
      <div class="scenario-line" style="background:#a78bfa"></div>
      <div><div class="scenario-title">论文协作写作</div><div class="scenario-desc">从选题到IEEE成稿全流程</div></div>
    </div>
    <div class="scenario">
      <div class="scenario-icon">🎬</div>
      <div class="scenario-line" style="background:#f59e0b"></div>
      <div><div class="scenario-title">教学视频制作</div><div class="scenario-desc">PPT自动转教学视频</div></div>
    </div>
    <div class="scenario">
      <div class="scenario-icon">📊</div>
      <div class="scenario-line" style="background:#ef4444"></div>
      <div><div class="scenario-title">数据可视化</div><div class="scenario-desc">一键生成可发表图表</div></div>
    </div>
  </div>

  <!-- Benefits -->
  <div class="benefits-title">入 群 福 利</div>
  <div class="benefits-heading">扫码加入读者服务群</div>
  <div class="benefits-grid">
    <div class="benefit">
      <div class="benefit-head"><span class="benefit-icon">🦞</span><span class="benefit-name">小龙虾AI体验</span></div>
      <div class="benefit-desc">群内部署OpenClaw智能体，实时体验课件生成、教案制作等AI能力</div>
    </div>
    <div class="benefit">
      <div class="benefit-head"><span class="benefit-icon">📚</span><span class="benefit-name">教学资料包</span></div>
      <div class="benefit-desc">小龙虾三部曲课件、数据挖掘案例、16章教学动画、微信小程序等全套Manus实战案例</div>
    </div>
    <div class="benefit">
      <div class="benefit-head"><span class="benefit-icon">🎁</span><span class="benefit-name">免费样书赠送</span></div>
      <div class="benefit-desc">直播间专享10本《Manus智能体全攻略》免费样书（名额有限，抽奖获得）</div>
    </div>
    <div class="benefit">
      <div class="benefit-head"><span class="benefit-icon">💬</span><span class="benefit-name">教学交流社区</span></div>
      <div class="benefit-desc">高校教师AI教学实践交流、问题解答、经验分享</div>
    </div>
  </div>

  <!-- Bottom -->
  <div class="bottom">
    <div class="bottom-left">
      <div class="author-photo">
        <img src="author_photo.png" alt="诸葛斌" />
      </div>
      <div>
        <div class="author-name">诸葛斌 教授</div>
        <div class="author-org">浙江工商大学 · 萨塞克斯人工智能学院</div>
        <div class="author-award">2025全国高校人工智能教育大会优秀案例一等奖</div>
      </div>
    </div>
    <div class="bottom-center">
      <div class="date-big">6月24日</div>
      <div class="date-time">下午 3:00-4:00</div>
    </div>
    <div class="qr-block">
      <div class="qr-img">
        <img src="qr_code.png" alt="扫码加群" />
      </div>
      <div class="qr-label">扫码加群</div>
    </div>
  </div>
</div>
</body>
</html>
'''

with open('/home/admin/.openclaw/workspace/digital-employee-report/poster.html', 'w') as f:
    f.write(html)

print('✅ Poster HTML generated')

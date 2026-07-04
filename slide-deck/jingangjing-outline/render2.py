#!/usr/bin/env python3
"""Render HTML slides to PNG images using Playwright - one slide per page."""
import asyncio
import os
from playwright.async_api import async_playwright

SLIDE_DIR = "/home/admin/.openclaw/workspace/slide-deck/jingangjing-outline"
OUTPUT_DIR = SLIDE_DIR

SLIDES = [
    ("01-slide-cover", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.ink-bg{position:absolute;bottom:0;left:0;right:0;height:180px;background:linear-gradient(to top,rgba(45,45,45,0.05),transparent);border-radius:50% 50% 0 0/100% 100% 0 0}
.wash{position:absolute;border-radius:50%;filter:blur(40px);opacity:0.25}
svg.lotus{position:absolute;bottom:15%;right:10%;width:90px;height:90px;opacity:0.3}
.title{position:absolute;top:32%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:72px;color:#2D2D2D;letter-spacing:8px;text-align:center}
.sub{position:absolute;top:54%;left:50%;transform:translateX(-50%);font-size:28px;color:#5D5D5D;letter-spacing:6px;font-weight:300}
.bottom{position:absolute;bottom:8%;left:50%;transform:translateX(-50%);font-size:16px;color:#9D9D9D;letter-spacing:4px}
</style></head><body>
<div class="ink-bg"></div>
<div class="wash" style="width:300px;height:300px;background:#87A96B;bottom:5%;right:5%"></div>
<div class="title">金刚般若波罗蜜经</div>
<div class="sub">三十二品整体脉络</div>
<div class="bottom">水墨禅风讲义</div>
<svg class="lotus" viewBox="0 0 90 90"><ellipse cx="45" cy="55" rx="14" ry="28" fill="rgba(232,160,160,0.3)" transform="rotate(-20 45 55)"/><ellipse cx="45" cy="55" rx="14" ry="28" fill="rgba(232,160,160,0.25)" transform="rotate(20 45 55)"/><ellipse cx="45" cy="55" rx="12" ry="24" fill="rgba(232,160,160,0.35)"/><ellipse cx="45" cy="55" rx="12" ry="22" fill="rgba(232,160,160,0.2)" transform="rotate(-40 45 55)"/><ellipse cx="45" cy="55" rx="12" ry="22" fill="rgba(232,160,160,0.2)" transform="rotate(40 45 55)"/></svg>
</body></html>"""),
    ("02-slide-yuanqi", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.wash{position:absolute;border-radius:50%;filter:blur(40px);opacity:0.2}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:16%;left:8%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.stroke{position:absolute;top:28%;left:8%;width:55%;height:2px;background:linear-gradient(to right,transparent,#2D2D2D,transparent);opacity:0.12}
.quote{position:absolute;top:32%;left:8%;right:40%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:32px;color:#2D2D2D;letter-spacing:2px;padding:18px 28px;border-left:3px solid #D4A84B;background:linear-gradient(to right,rgba(212,168,75,0.08),transparent);line-height:1.8}
.body{position:absolute;top:56%;left:8%;right:40%;font-size:22px;color:#4D4D4D;line-height:2.2;letter-spacing:1px}
svg.bowl{position:absolute;bottom:12%;right:8%;width:200px;height:200px;opacity:0.2}
</style></head><body>
<div class="wash" style="width:250px;height:250px;background:#87A96B;top:8%;left:50%"></div>
<div class="tag">第一品 · 法会因由分</div>
<div class="head">讲经缘起：日常生活中的般若</div>
<div class="stroke"></div>
<div class="quote">佛陀日常乞食、洗足、敷座而坐<br/>行住坐卧皆是般若道场</div>
<div class="body">以平常心示现，于日常中见佛法</div>
<svg class="bowl" viewBox="0 0 200 200"><circle cx="100" cy="100" r="75" fill="none" stroke="#2D2D2D" stroke-width="1.5" opacity="0.3"/><ellipse cx="100" cy="110" rx="60" ry="38" fill="none" stroke="#2D2D2D" stroke-width="1.5"/><ellipse cx="100" cy="105" rx="55" ry="33" fill="rgba(212,168,75,0.08)"/><path d="M45,105 Q100,60 155,105" fill="none" stroke="#2D2D2D" stroke-width="1"/></svg>
</body></html>"""),
    ("03-slide-fawen", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.wash{position:absolute;border-radius:50%;filter:blur(50px);opacity:0.12}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:16%;left:8%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.qbox{position:absolute;top:30%;left:8%;right:8%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:38px;color:#2D2D2D;letter-spacing:4px;padding:30px 40px;border-left:4px solid #D4A84B;background:linear-gradient(to right,rgba(212,168,75,0.1),transparent);line-height:1.9}
.note{position:absolute;top:72%;left:8%;font-size:20px;color:#7D7D7D;letter-spacing:2px}
svg.qq{position:absolute;bottom:8%;right:8%;width:130px;height:130px;opacity:0.1}
</style></head><body>
<div class="wash" style="width:500px;height:350px;background:#D4A84B;top:15%;left:30%"></div>
<div class="tag">第二品 · 善现启请分</div>
<div class="head">须菩提发问</div>
<div class="qbox">善男子善女人，发菩提心者<br/>应云何住？云何降伏其心？</div>
<div class="note">全经问答，由此一问展开</div>
<svg class="qq" viewBox="0 0 130 130"><text x="10" y="95" font-family="'KaiTi','STXingkai','楷体',cursive" font-size="110" fill="#2D2D2D">？？</text></svg>
</body></html>"""),
    ("04-slide-zonggang", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.wash{position:absolute;border-radius:50%;filter:blur(60px);opacity:0.03}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.central{position:absolute;top:20%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:56px;color:#2D2D2D;letter-spacing:6px;text-align:center}
.stroke{position:absolute;top:44%;left:20%;width:60%;height:3px;background:linear-gradient(to right,transparent,#D4A84B,transparent);opacity:0.3}
.body{position:absolute;top:52%;left:15%;right:15%;font-size:24px;color:#4D4D4D;text-align:center;line-height:2.2}
svg.sweep{position:absolute;top:18%;left:3%;width:1270px;height:200px;opacity:0.03}
</style></head><body>
<div class="wash" style="width:600px;height:500px;background:#2D2D2D;top:10%;left:20%"></div>
<svg class="sweep" viewBox="0 0 1270 200"><path d="M0,100 Q200,20 400,80 Q600,140 800,60 Q1000,20 1270,100" fill="none" stroke="#2D2D2D" stroke-width="30"/></svg>
<div class="tag">第三品 · 大乘正宗分</div>
<div class="central">应无所住而生其心</div>
<div class="stroke"></div>
<div class="body"><p>度一切众生，而实无众生可度</p><p style="margin-top:15px">破除我相、人相、众生相、寿者相</p></div>
</body></html>"""),
    ("05-slide-poxiang", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:16%;left:5%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.quote{position:absolute;top:30%;left:5%;width:55%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:32px;color:#2D2D2D;letter-spacing:2px;padding:18px 28px;border-left:3px solid #D4A84B;background:linear-gradient(to right,rgba(212,168,75,0.08),transparent);line-height:1.9}
.body{position:absolute;top:58%;left:5%;width:55%;font-size:22px;color:#4D4D4D;line-height:2.2}
svg.dissolve{position:absolute;top:20%;right:3%;width:48%;height:65%;opacity:0.2}
</style></head><body>
<div class="tag">第五品 · 如理实见分 / 第六品 · 正信希有分</div>
<div class="head">破相：凡所有相，皆是虚妄</div>
<div class="quote">凡所有相，皆是虚妄。<br/>若见诸相非相，即见如来。</div>
<div class="body"><p>一切外在形相，都非真实本体</p><p>不执着四相：我相、人相、众生相、寿者相</p><p>般若空义难信稀有，受持此经消无量业障</p></div>
<svg class="dissolve" viewBox="0 0 500 450"><circle cx="200" cy="200" r="80" fill="rgba(45,45,45,0.12)"/><circle cx="200" cy="200" r="100" fill="rgba(45,45,45,0.06)"/><circle cx="200" cy="200" r="120" fill="rgba(45,45,45,0.03)"/><circle cx="300" cy="150" r="5" fill="rgba(45,45,45,0.08)"/><circle cx="330" cy="180" r="3" fill="rgba(45,45,45,0.06)"/><circle cx="350" cy="210" r="4" fill="rgba(45,45,45,0.05)"/><circle cx="370" cy="250" r="2" fill="rgba(45,45,45,0.04)"/><circle cx="390" cy="280" r="3" fill="rgba(45,45,45,0.02)"/><circle cx="410" cy="300" r="2" fill="rgba(45,45,45,0.015)"/></svg>
</body></html>"""),
    ("06-slide-wude", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:14%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.stroke{position:absolute;top:28%;left:8%;width:84%;height:1px;background:linear-gradient(to right,transparent,#2D2D2D,transparent);opacity:0.12}
.card{position:absolute;top:34%;width:42%;height:54%;border-radius:8px;padding:24px;background:rgba(255,255,255,0.6)}
.card-left{left:5%;background:linear-gradient(135deg,rgba(244,162,97,0.1),rgba(255,255,255,0.6))}
.card-right{right:5%;background:linear-gradient(135deg,rgba(212,168,75,0.1),rgba(255,255,255,0.6))}
.ctitle{font-family:'KaiTi','STXingkai','楷体',cursive;font-size:30px;margin-bottom:16px}
.cbody{font-size:20px;color:#5D5D5D;line-height:2}
svg.zen{position:absolute;top:48%;left:50%;transform:translate(-50%,-50%);width:60px;height:60px;opacity:0.12}
</style></head><body>
<div class="tag">第七品 · 无得无说分 / 第八品 · 依法出生分</div>
<div class="head">无得无说 · 依法出生</div>
<div class="stroke"></div>
<div class="card card-left"><div class="ctitle" style="color:#F4A261">无得无说</div><div class="cbody">没有固定不变的"无上菩提法"<br/>如来也无固定法可说<br/>一切圣贤依无为法修行，深浅有别</div></div>
<div class="card card-right"><div class="ctitle" style="color:#D4A84B">依法出生</div><div class="cbody">一切诸佛、一切菩提法<br/>皆从般若生出<br/>持诵四句偈，福德远超七宝布施</div></div>
<svg class="zen" viewBox="0 0 60 60"><circle cx="30" cy="30" r="25" fill="none" stroke="#2D2D2D" stroke-width="2"/></svg>
</body></html>"""),
    ("07-slide-guowei", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:14%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.card{position:absolute;width:42%;height:28%;border-radius:8px;padding:20px;background:rgba(255,255,255,0.6)}
.card-t{font-family:'KaiTi','STXingkai','楷体',cursive;font-size:24px;margin-bottom:10px}
.card-b{font-size:19px;color:#5D5D5D;line-height:1.8}
.c1{top:28%;left:5%;background:linear-gradient(135deg,rgba(244,162,97,0.12),rgba(255,255,255,0.6))}
.c2{top:28%;right:5%;background:linear-gradient(135deg,rgba(135,169,107,0.12),rgba(255,255,255,0.6))}
.c3{top:63%;left:5%;background:linear-gradient(135deg,rgba(212,168,75,0.12),rgba(255,255,255,0.6))}
.c4{top:63%;right:5%;background:linear-gradient(135deg,rgba(126,200,227,0.12),rgba(255,255,255,0.6))}
</style></head><body>
<div class="tag">第九品 · 一相无相分 / 第十品 · 庄严净土分</div>
<div class="head">果位无相 · 庄严净土</div>
<div class="card c1"><div class="card-t" style="color:#F4A261">四果假名</div><div class="card-b">须陀洹至阿罗汉，皆无实有可得</div></div>
<div class="card c2"><div class="card-t" style="color:#87A96B">果位只是假名</div><div class="card-b">不可执着修行果位之相</div></div>
<div class="card c3"><div class="card-t" style="color:#D4A84B">庄严佛土</div><div class="card-b">心净则国土净，非外求可得</div></div>
<div class="card c4"><div class="card-t" style="color:#7EC8E3">即非庄严</div><div class="card-b">庄严佛土者，即非庄严，是名庄严</div></div>
</body></html>"""),
    ("08-slide-fude", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:14%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.stroke{position:absolute;top:28%;left:8%;width:84%;height:1px;background:linear-gradient(to right,transparent,#2D2D2D,transparent);opacity:0.12}
.col{position:absolute;top:33%;width:40%;text-align:center}
.col-l{left:5%}
.col-r{right:5%}
.ct{font-family:'KaiTi','STXingkai','楷体',cursive;font-size:32px;margin-bottom:15px}
.cb{font-size:20px;color:#5D5D5D;line-height:1.9}
.bottom{position:absolute;bottom:10%;left:10%;right:10%;text-align:center;font-size:18px;color:#9D9D9D;letter-spacing:2px}
svg.arrow-down{opacity:0.25}
svg.arrow-up{opacity:0.25}
</style></head><body>
<div class="tag">第十一品 · 无为福胜分 / 第十二品 · 尊重正教分</div>
<div class="head">无为福胜 · 尊重正教</div>
<div class="stroke"></div>
<div class="col col-l"><div class="ct" style="color:#F4A261">有为福报</div><div class="cb">七宝布施<br/>短暂有漏，终有尽时</div><svg class="arrow-down" width="40" height="60" viewBox="0 0 40 60"><line x1="20" y1="0" x2="20" y2="45" stroke="#F4A261" stroke-width="2" stroke-dasharray="4,4"/><polygon points="10,40 20,55 30,40" fill="#F4A261" opacity="0.4"/></svg></div>
<div class="col col-r"><div class="ct" style="color:#87A96B">无为福报</div><div class="cb">受持般若、悟无住无相<br/>无漏大福，无量倍胜</div><svg class="arrow-up" width="40" height="60" viewBox="0 0 40 60"><line x1="20" y1="60" x2="20" y2="15" stroke="#87A96B" stroke-width="2" stroke-dasharray="4,4"/><polygon points="10,20 20,5 30,20" fill="#87A96B" opacity="0.4"/></svg></div>
<div class="bottom">无论在家出家，受持此经，一切天人皆应供养</div>
</body></html>"""),
    ("09-slide-lixing", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:14%;left:5%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.quote{position:absolute;top:28%;left:5%;width:55%;font-family:'KaiTi','STXingkai','楷体',cursive;font-size:28px;color:#2D2D2D;letter-spacing:2px;padding:16px 24px;border-left:3px solid #D4A84B;background:linear-gradient(to right,rgba(212,168,75,0.08),transparent);line-height:1.8}
.body{position:absolute;top:48%;left:5%;width:55%;font-size:22px;color:#4D4D4D;line-height:2.2}
svg.water{position:absolute;top:22%;right:3%;width:42%;height:65%;opacity:0.18}
</style></head><body>
<div class="tag">第十四品 · 离相寂灭分 / 第十五品 · 持经功德分</div>
<div class="head">离相寂灭 · 持经功德</div>
<div class="quote">离一切诸相，即名诸佛</div>
<div class="body"><p>发菩提心须远离四相：我、人、众生、寿者</p><p>诸法无实亦无虚</p><p>恒河沙数身命布施，不及受持四句偈之功德</p></div>
<svg class="water" viewBox="0 0 500 450"><path d="M50,200 Q150,80 250,150 Q350,50 450,120 L450,300 Q350,250 250,280 Q150,250 50,300 Z" fill="rgba(45,45,45,0.06)"/><rect x="0" y="300" width="500" height="150" fill="rgba(126,200,227,0.04)"/><line x1="50" y1="320" x2="200" y2="320" stroke="rgba(45,45,45,0.04)" stroke-width="1"/><line x1="100" y1="340" x2="250" y2="340" stroke="rgba(45,45,45,0.03)" stroke-width="1"/><line x1="80" y1="360" x2="220" y2="360" stroke="rgba(45,45,45,0.03)" stroke-width="1"/><line x1="120" y1="380" x2="280" y2="380" stroke="rgba(45,45,45,0.02)" stroke-width="1"/><path d="M0,430 Q125,420 250,435 Q375,450 500,430" fill="none" stroke="rgba(45,45,45,0.05)" stroke-width="1.5"/></svg>
</body></html>"""),
    ("10-slide-wuwo", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.tag{position:absolute;top:8%;left:8%;font-size:18px;color:#9D9D9D;letter-spacing:3px;font-weight:300}
.head{position:absolute;top:14%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:42px;color:#2D2D2D;letter-spacing:4px}
.stroke{position:absolute;top:28%;left:8%;width:84%;height:1px;background:linear-gradient(to right,transparent,#2D2D2D,transparent);opacity:0.12}
.col-l{position:absolute;top:33%;left:5%;width:35%}
.col-c{position:absolute;top:33%;left:42%;width:25%;text-align:center}
.col-r{position:absolute;top:33%;right:5%;width:30%}
.stitle{font-family:'KaiTi','STXingkai','楷体',cursive;font-size:28px;margin-bottom:12px}
.sbody{font-size:19px;color:#5D5D5D;line-height:1.9}
.eye{border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;margin:8px auto}
svg.zen{opacity:0.1;margin-top:10px}
</style></head><body>
<div class="tag">第十七品 · 究竟无我分 / 第十八品 · 一体同观分</div>
<div class="head">究竟无我 · 一体同观</div>
<div class="stroke"></div>
<div class="col-l"><div class="stitle">通达无我法</div><div class="sbody">菩萨度生、成佛<br/>皆不可执"我能度<br/>众生可度"</div><svg class="zen" width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="35" fill="none" stroke="#2D2D2D" stroke-width="2.5"/></svg></div>
<div class="col-c"><div class="stitle" style="color:#87A96B">如来五眼</div><div class="eye" style="width:50px;height:50px;background:rgba(135,169,107,0.12);color:#87A96B">肉眼</div><div class="eye" style="width:60px;height:60px;background:rgba(126,200,227,0.12);color:#7EC8E3">天眼</div><div class="eye" style="width:70px;height:70px;background:rgba(212,168,75,0.12);color:#D4A84B">慧眼</div><div class="eye" style="width:80px;height:80px;background:rgba(197,180,227,0.12);color:#C5B4E3">法眼</div><div class="eye" style="width:90px;height:90px;background:rgba(244,162,97,0.12);color:#F4A261">佛眼</div></div>
<div class="col-r"><div class="stitle" style="color:#D4A84B">三心皆空</div><div class="sbody" style="line-height:2.2">过去心不可得<br/>现在心不可得<br/>未来心不可得</div><svg style="opacity:0.12;margin-top:10px" width="80" height="40" viewBox="0 0 80 40"><circle cx="15" cy="20" r="12" fill="rgba(232,160,160,0.5)"/><circle cx="40" cy="20" r="8" fill="rgba(232,160,160,0.3)"/><circle cx="65" cy="20" r="4" fill="rgba(232,160,160,0.15)"/></svg></div>
</body></html>"""),
    ("11-slide-jieyu", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
svg.mountain{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0.04}
.wash{position:absolute;border-radius:50%;filter:blur(60px);opacity:0.06}
.tag{position:absolute;top:8%;left:50%;transform:translateX(-50%);font-size:18px;color:#BDBDBD;letter-spacing:4px}
.verse{position:absolute;top:22%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:52px;color:#2D2D2D;text-align:center;line-height:1.9;letter-spacing:6px}
svg.bubbles{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0.15}
.note{position:absolute;bottom:8%;left:50%;transform:translateX(-50%);font-size:16px;color:#9D9D9D;letter-spacing:3px}
</style></head><body>
<svg class="mountain" viewBox="0 0 1280 720"><path d="M0,500 Q100,350 300,420 Q500,250 700,380 Q900,200 1100,350 Q1200,300 1280,380 L1280,720 L0,720 Z" fill="#2D2D2D"/><path d="M0,550 Q200,450 400,500 Q600,380 800,480 Q1000,350 1280,450 L1280,720 L0,720 Z" fill="#2D2D2D" opacity="0.5"/></svg>
<div class="wash" style="width:600px;height:500px;background:#87A96B;top:10%;left:20%"></div>
<div class="wash" style="width:400px;height:400px;background:#D4A84B;top:20%;right:10%"></div>
<div class="tag">第三十二品 · 应化非真分</div>
<div class="verse">一切有为法<br/>如梦幻泡影<br/>如露亦如电<br/>应作如是观</div>
<svg class="bubbles" viewBox="0 0 1280 720"><circle cx="100" cy="100" r="15" fill="none" stroke="#7EC8E3" stroke-width="1"/><circle cx="200" cy="150" r="8" fill="none" stroke="#D4A84B" stroke-width="1"/><circle cx="1100" cy="200" r="12" fill="none" stroke="#87A96B" stroke-width="1"/><circle cx="1050" cy="600" r="10" fill="none" stroke="#E8A0A0" stroke-width="1"/><circle cx="150" cy="650" r="6" fill="none" stroke="#D4A84B" stroke-width="1"/><circle cx="1150" cy="100" r="18" fill="none" stroke="#7EC8E3" stroke-width="1"/></svg>
<div class="note">说法不取诸相，如如不动</div>
</body></html>"""),
    ("12-slide-back-cover", """<html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;background:#FAF8F0;font-family:'Noto Serif SC','Source Han Serif SC','STSong','SimSun',serif;color:#2D2D2D;position:relative;overflow:hidden}
.ink-bg{position:absolute;bottom:0;left:0;right:0;height:100px;background:linear-gradient(to top,rgba(45,45,45,0.04),transparent);border-radius:50% 50% 0 0/100% 100% 0 0}
.main{position:absolute;top:32%;left:50%;transform:translateX(-50%);font-family:'KaiTi','STXingkai','楷体',cursive;font-size:80px;color:#2D2D2D;letter-spacing:12px;text-align:center}
.hstroke{position:absolute;top:48%;left:50%;transform:translateX(-50%);width:200px;height:2px;background:linear-gradient(to right,transparent,rgba(45,45,45,0.15),transparent)}
.sub{position:absolute;top:53%;left:50%;transform:translateX(-50%);font-size:22px;color:#7D7D7D;letter-spacing:4px}
.bot{position:absolute;bottom:8%;left:50%;transform:translateX(-50%);font-size:14px;color:#BDBDBD;letter-spacing:3px}
svg.petal{position:absolute;bottom:12%;left:8%;width:60px;height:60px;opacity:0.12}
svg.mtn{position:absolute;bottom:0;left:0;width:100%;height:80px;opacity:0.025}
</style></head><body>
<div class="ink-bg"></div>
<div class="main">信受奉行</div>
<div class="hstroke"></div>
<div class="sub">大众闻法开悟，信受奉行</div>
<div class="bot">金刚般若波罗蜜经 · 三十二品脉络讲义</div>
<svg class="petal" viewBox="0 0 60 60"><ellipse cx="30" cy="35" rx="8" ry="20" fill="rgba(232,160,160,0.5)" transform="rotate(-10 30 35)"/></svg>
<svg class="mtn" viewBox="0 0 1280 80"><path d="M0,80 Q200,30 400,50 Q600,20 800,45 Q1000,15 1280,40 L1280,80 Z" fill="#2D2D2D"/></svg>
</body></html>"""),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )

        for fname, html in SLIDES:
            context = await browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
            page = await context.new_page()
            await page.set_content(html, wait_until="load")
            await page.wait_for_timeout(2000)
            output_path = os.path.join(OUTPUT_DIR, f"{fname}.png")
            await page.screenshot(path=output_path, type="png", full_page=False)
            print(f"✓ Generated: {fname}.png")
            await page.close()
            await context.close()

        await browser.close()
        print("\nAll 12 slides generated!")

if __name__ == "__main__":
    asyncio.run(main())

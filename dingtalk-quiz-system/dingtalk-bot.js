/**
 * 钉钉机器人推送考试通知
 * 
 * 使用方法：
 * 1. 在钉钉群创建自定义机器人，获取 Webhook URL
 * 2. 修改下面的 WEBHOOK_URL
 * 3. 运行：node dingtalk-bot.js
 */

const https = require('https');

// 配置你的钉钉机器人 Webhook URL
const WEBHOOK_URL = 'https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN_HERE';

// 考试系统地址
const QUIZ_URL = 'http://172.24.56.3:3000';

// 发送钉钉消息
function sendDingTalkMessage(title, content) {
  const data = JSON.stringify({
    msgtype: 'markdown',
    markdown: {
      title: title,
      text: content
    }
  });

  const url = new URL(WEBHOOK_URL);
  const options = {
    hostname: url.hostname,
    path: url.pathname + url.search,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  const req = https.request(options, (res) => {
    let body = '';
    res.on('data', (chunk) => body += chunk);
    res.on('end', () => {
      console.log('钉钉消息发送结果：', body);
    });
  });

  req.on('error', (e) => {
    console.error('发送失败：', e.message);
  });

  req.write(data);
  req.end();
}

// 发送考试通知
function sendExamNotification(category, count, deadline) {
  const text = `## 📚 考试通知\n\n**分类：** ${category || '全部'}\n**题量：** ${count} 题\n**截止时间：** ${deadline || '不限'}\n\n👇 点击下方链接开始考试：\n[📝 立即考试](${QUIZ_URL})\n\n---\n💡 提示：考试完成后自动评分，可查看答题详情`;

  sendDingTalkMessage('📚 考试通知', text);
}

// 发送考试结果统计
function sendExamResults(examData) {
  const text = `## 📊 考试结果统计\n\n**考生：** ${examData.user_name}\n**得分：** ${examData.score} 分\n**题量：** ${examData.total_questions} 题\n**时间：** ${new Date(examData.created_at).toLocaleString('zh-CN')}\n\n${examData.score >= 60 ? '✅ 考试通过！' : '❌ 未通过，请继续努力！'}`;

  sendDingTalkMessage('📊 考试结果', text);
}

// 示例：发送考试通知
if (require.main === module) {
  console.log('📤 发送考试通知...');
  sendExamNotification('道教理论', 10, '2026-05-26 18:00');
  console.log('✅ 发送完成');
}

module.exports = { sendExamNotification, sendExamResults };

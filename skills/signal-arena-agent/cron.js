/**
 * 定时任务调度器
 * 信电大虾 - Signal Arena 自动盯盘
 * 
 * 时间表：
 * - 每天 10:00：A 股/港股盯盘
 * - 每天 22:00：美股盯盘
 */

const cron = require('node-cron');
const strategy = require('./strategy');
const arena = require('./arena');

console.log('🦞 信电大虾 - Signal Arena 自动交易 Agent 启动');
console.log('=' .repeat(50));

// A 股/港股盯盘：每天 10:00 (北京时间)
const cnMarketTask = cron.schedule('0 10 * * *', async () => {
  console.log('\n⏰ [10:00] A 股/港股盯盘时间到！');
  await strategy.runStrategy();
}, {
  timezone: 'Asia/Shanghai'
});

// 美股盯盘：每天 22:00 (北京时间)
const usMarketTask = cron.schedule('0 22 * * *', async () => {
  console.log('\n⏰ [22:00] 美股盯盘时间到！');
  await strategy.runStrategy();
}, {
  timezone: 'Asia/Shanghai'
});

// 健康检查：每小时检查一次 API 连接
const healthCheck = cron.schedule('0 * * * *', async () => {
  const home = await arena.getHome();
  if (home && home.success) {
    console.log(`💓 [健康检查] API 正常 | 总资产：¥${home.data.total_assets?.toLocaleString()}`);
  } else {
    console.error('❌ [健康检查] API 异常');
  }
}, {
  timezone: 'Asia/Shanghai'
});

console.log('✅ 定时任务已启动:');
console.log('   📈 A 股/港股：每天 10:00');
console.log('   🌙 美股：每天 22:00');
console.log('   💓 健康检查：每小时');
console.log('=' .repeat(50));
console.log('按 Ctrl+C 停止服务\n');

// 处理退出
process.on('SIGINT', () => {
  console.log('\n👋 正在停止服务...');
  cnMarketTask.stop();
  usMarketTask.stop();
  healthCheck.stop();
  console.log('✅ 服务已停止');
  process.exit(0);
});

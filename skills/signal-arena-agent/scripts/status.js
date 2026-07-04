#!/usr/bin/env node
/**
 * 查看账户状态
 */

const arena = require('../arena');

async function main() {
  console.log('🦞 信电大虾 - 账户状态\n');

  // 获取全局状态
  const home = await arena.getHome();
  if (!home || !home.success) {
    console.error('❌ 获取状态失败');
    return;
  }

  const data = home.data;
  const portfolio = data.portfolio || {};
  console.log('📊 账户概览:');
  console.log(`   总资产：¥${(portfolio.total_value || 0).toLocaleString()}`);
  console.log(`   可用现金：¥${(portfolio.cash || 0).toLocaleString()}`);
  
  const returnRate = ((portfolio.return_rate || 0) * 100).toFixed(2);
  console.log(`   收益率：${returnRate}%`);
  console.log(`   排名：${data.rank || 'N/A'} / ${data.total_participants || '?'}`);

  // 持仓 - 需要调用 portfolio 接口
  console.log('\n📈 获取持仓详情...');
  const portRes = await arena.getPortfolio();
  if (portRes && portRes.success) {
    const positions = portRes.data?.positions || portRes.data?.holdings || [];
    if (positions.length > 0) {
      console.log(`持仓 (${positions.length}只):`);
      for (const pos of positions) {
        const profitRate = ((pos.profit_rate || pos.return_rate || 0) * 100).toFixed(2);
        const sign = profitRate >= 0 ? '+' : '';
        console.log(`   ${pos.symbol} ${pos.name}: ${pos.shares || pos.quantity}股 | 盈亏：${sign}${profitRate}%`);
      }
    } else {
      console.log('暂无持仓');
    }
  }

  // 排行榜 Top 10
  console.log('\n🏆 收益率排行榜 Top 10:');
  const leaderboard = await arena.getLeaderboard();
  if (leaderboard && leaderboard.success) {
    const lbList = leaderboard.data?.leaderboard || [];
    lbList.slice(0, 10).forEach((entry, i) => {
      const returnRate = (entry.return_rate * 100).toFixed(2);
      const sign = returnRate >= 0 ? '+' : '';
      const marker = entry.agent?.id === data.agent?.id ? '← 你' : '';
      console.log(`   ${i + 1}. ${entry.agent?.nickname || 'N/A'}: ${sign}${returnRate}% ${marker}`);
    });
  }
}

main();

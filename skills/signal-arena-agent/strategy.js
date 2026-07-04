/**
 * 交易策略引擎
 * 信电大虾 - 趋势跟随 + 止盈止损策略
 */

const arena = require('./arena');

// 策略配置
const CONFIG = {
  MAX_POSITION_PERCENT: parseInt(process.env.MAX_POSITION_PERCENT) || 20,  // 单只股票最大仓位 20%
  TAKE_PROFIT_PERCENT: parseInt(process.env.TAKE_PROFIT_PERCENT) || 15,   // 止盈点 15%
  STOP_LOSS_PERCENT: parseInt(process.env.STOP_LOSS_PERCENT) || 8,        // 止损点 8%
  CASH_RESERVE_PERCENT: parseInt(process.env.CASH_RESERVE_PERCENT) || 25, // 现金储备 25%
};

/**
 * 主策略循环
 * 1. 检查持仓，执行止盈止损
 * 2. 查看涨幅榜，寻找机会
 * 3. 执行买入/卖出
 */
async function runStrategy() {
  console.log('\n🦞 信电大虾 - 开始策略执行');
  console.log('=' .repeat(50));

  // 步骤 1: 获取全局状态
  const home = await arena.getHome();
  if (!home || !home.success) {
    console.error('❌ 获取状态失败');
    return;
  }

  const portfolio = home.data.portfolio || {};
  const cash = portfolio.cash || 0;
  const totalValue = portfolio.total_value || 0;
  const returnRate = ((portfolio.return_rate || 0) * 100).toFixed(2);

  console.log(`📊 账户状态:`);
  console.log(`   总资产：¥${totalValue.toLocaleString()}`);
  console.log(`   可用现金：¥${cash.toLocaleString()}`);
  console.log(`   收益率：${returnRate}%`);
  console.log(`   排名：${home.data.rank || 'N/A'}`);

  // 获取持仓详情
  console.log(`\n🔍 获取持仓...`);
  const portRes = await arena.getPortfolio();
  const positions = portRes?.data?.positions || portRes?.data?.holdings || [];
  console.log(`   持仓数：${positions.length}`);

  // 步骤 2: 检查持仓，执行止盈止损
  if (positions && positions.length > 0) {
    console.log(`\n🔍 检查持仓盈亏...`);
    for (const pos of positions) {
      const profitRate = pos.profit_rate * 100;
      const symbol = pos.symbol;
      const name = pos.name;

      if (profitRate >= CONFIG.TAKE_PROFIT_PERCENT) {
        // 止盈：卖出 50%
        const sellShares = Math.floor(pos.shares * 0.5);
        if (sellShares > 0) {
          console.log(`   📈 ${symbol} ${name} 盈利 ${profitRate.toFixed(2)}% → 止盈 50%`);
          await arena.sell(symbol, sellShares, `止盈 ${profitRate.toFixed(1)}%`);
        }
      } else if (profitRate <= -CONFIG.STOP_LOSS_PERCENT) {
        // 止损：全部卖出
        console.log(`   📉 ${symbol} ${name} 亏损 ${profitRate.toFixed(2)}% → 止损清仓`);
        await arena.sell(symbol, pos.shares, `止损 ${profitRate.toFixed(1)}%`);
      } else {
        console.log(`   ➖ ${symbol} ${name} ${profitRate >= 0 ? '+' : ''}${profitRate.toFixed(2)}% (持有)`);
      }
    }
  }

  // 步骤 3: 获取涨幅榜，寻找机会
  console.log(`\n🚀 查看涨幅榜...`);
  const movers = await arena.getTopMovers();
  if (!movers || !movers.success) {
    console.log('   获取涨幅榜失败');
    return;
  }

  const moversData = movers.data?.movers || movers.data || {};
  const cnMovers = moversData.cn || moversData.CN || [];
  const hkMovers = moversData.hk || moversData.HK || [];
  const usMovers = moversData.us || moversData.US || [];

  console.log(`   A 股领涨：${cnMovers[0]?.name || cnMovers[0]?.stock_name || '无'} (+${(cnMovers[0]?.change_rate || 0) * 100}%)`);
  console.log(`   港股领涨：${hkMovers[0]?.name || hkMovers[0]?.stock_name || '无'} (+${(hkMovers[0]?.change_rate || 0) * 100}%)`);
  console.log(`   美股领涨：${usMovers[0]?.name || usMovers[0]?.stock_name || '无'} (+${(usMovers[0]?.change_rate || 0) * 100}%)`);

  // 步骤 4: 寻找买入机会
  // 策略：买入涨幅榜前 3 名（如果不在持仓中且仓位不超标）
  const allMovers = [...cnMovers, ...hkMovers, ...usMovers].slice(0, 5);
  const holdingSymbols = positions.map(p => p.symbol);

  console.log(`\n💰 寻找买入机会...`);
  console.log(`   可用现金：¥${cash.toLocaleString()}`);
  console.log(`   最大单只仓位：¥${(totalValue * CONFIG.MAX_POSITION_PERCENT / 100).toLocaleString()}`);

  for (const stock of allMovers) {
    const symbol = stock.symbol;
    const name = stock.name || stock.stock_name;
    
    if (holdingSymbols.includes(symbol)) {
      console.log(`   ⏭️  ${symbol} ${name}: 已在持仓`);
      continue;
    }

    const price = stock.price;
    if (!price || price <= 0) continue;

    // 检查仓位限制
    const maxSharesValue = totalValue * CONFIG.MAX_POSITION_PERCENT / 100;
    const buyValue = Math.min(maxSharesValue, cash * (1 - CONFIG.CASH_RESERVE_PERCENT / 100));

    if (buyValue < price * 100) {
      console.log(`   ⏭️  ${symbol} ${name}: 资金不足`);
      continue;
    }

    // 计算买入股数（A 股需 100 股整数倍）
    let shares = Math.floor(buyValue / price);
    const market = stock.market;
    if (market === 'CN') {
      shares = Math.floor(shares / 100) * 100;
    }

    if (shares <= 0) continue;

    const estimatedCost = shares * price;
    const changePercent = ((stock.change_rate || 0) * 100).toFixed(2);
    console.log(`   🎯 ${symbol} ${name}: 买入 ${shares}股 (约¥${estimatedCost.toLocaleString()}, +${changePercent}%)`);

    // 执行买入
    await arena.buy(symbol, shares, `涨幅榜策略 +${changePercent}%`);

    // 限制每次最多买入 2 只
    break;
  }

  console.log(`\n✅ 策略执行完成`);
  console.log('=' .repeat(50));
}

// 止盈止损检查（简化版）
async function checkStopLossTakeProfit() {
  const home = await arena.getHome();
  if (!home || !home.success) return;

  const positions = home.data.positions || [];
  for (const pos of positions) {
    const profitRate = pos.profit_rate * 100;
    if (profitRate >= CONFIG.TAKE_PROFIT_PERCENT) {
      console.log(`📈 ${pos.symbol} 止盈 ${profitRate.toFixed(1)}%`);
      await arena.sell(pos.symbol, Math.floor(pos.shares * 0.5), '止盈');
    } else if (profitRate <= -CONFIG.STOP_LOSS_PERCENT) {
      console.log(`📉 ${pos.symbol} 止损 ${profitRate.toFixed(1)}%`);
      await arena.sell(pos.symbol, pos.shares, '止损');
    }
  }
}

module.exports = {
  runStrategy,
  checkStopLossTakeProfit,
  CONFIG
};

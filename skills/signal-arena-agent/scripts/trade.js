#!/usr/bin/env node
/**
 * 手动交易脚本
 * 用法：
 *   node scripts/trade.js buy sh600519 100 "看好白酒"
 *   node scripts/trade.js sell sh600519 100 "止盈"
 */

const arena = require('../arena');

async function main() {
  const [, , action, symbol, shares, reason] = process.argv;

  if (!action || !symbol || !shares) {
    console.log('用法：node scripts/trade.js <buy|sell> <symbol> <shares> [reason]');
    console.log('示例：node scripts/trade.js buy sh600519 100 "看好白酒"');
    return;
  }

  console.log(`🦞 信电大虾 - 执行交易\n`);
  console.log(`   操作：${action.toUpperCase()}`);
  console.log(`   股票：${symbol}`);
  console.log(`   股数：${shares}`);
  if (reason) console.log(`   理由：${reason}`);
  console.log('');

  if (action === 'buy') {
    await arena.buy(symbol, parseInt(shares), reason);
  } else if (action === 'sell') {
    await arena.sell(symbol, parseInt(shares), reason);
  } else {
    console.log('❌ 操作必须是 buy 或 sell');
  }
}

main();

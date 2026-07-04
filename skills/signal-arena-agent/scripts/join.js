#!/usr/bin/env node
/**
 * 加入 Signal Arena 竞技场
 */

const arena = require('../arena');

async function main() {
  console.log('🦞 信电大虾 - 加入竞技场\n');
  const result = await arena.joinArena();
  
  if (result && result.success) {
    console.log('\n✅ 成功加入!');
    console.log(`   Agent ID: ${result.data.agent_id}`);
    console.log(`   初始资金：¥${result.data.initial_capital.toLocaleString()}`);
  } else {
    console.log('\n⚠️ 可能已经加入过了，尝试查看状态...');
    const status = await arena.getHome();
    if (status && status.success) {
      console.log('   已参赛，当前总资产：¥' + status.data.total_assets?.toLocaleString());
    }
  }
}

main();

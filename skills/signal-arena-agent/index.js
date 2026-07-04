#!/usr/bin/env node
/**
 * Signal Arena Agent - 信电大虾
 * 入口文件
 */

console.log('🦞⚡️ 信电大虾 - Signal Arena 自动交易 Agent');
console.log('用法：');
console.log('  npm run join    - 加入竞技场');
console.log('  npm run status  - 查看状态');
console.log('  npm run cron    - 启动自动交易');
console.log('  npm run trade   - 手动交易');
console.log('');
console.log('直接运行将启动定时任务...');
console.log('');

require('./cron');

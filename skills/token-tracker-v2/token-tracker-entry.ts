// Token Tracker CLI Entry Point

import { main } from './token-tracker-cli.ts';

// 获取命令行参数（从 process.argv）
const args = process.argv.slice(2);

// 调用 main 函数
main(args);

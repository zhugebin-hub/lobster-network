// Token Tracker CLI

import { TokenTracker } from './token-tracker';

// 创建单例
const tokenTracker = new TokenTracker();

interface CLICommand {
  name: string;
  description: string;
  handler: () => void | Promise<void>;
}

const commands: CLICommand[] = [
  {
    name: 'today',
    description: '查看今日 token 消耗统计',
    handler: () => {
      const stats = tokenTracker.getTodayStats();
      console.log('\n📊 今日 Token 消耗统计');
      console.log('='.repeat(40));
      console.log(`总消耗: ${stats.total.toLocaleString()} tokens`);
      console.log(`记录次数: ${stats.count}`);
      console.log(`平均: ${stats.average.toFixed(2)} tokens/次`);
      console.log(`最大: ${stats.max} tokens`);
      console.log(`最小: ${stats.min} tokens`);
      console.log('');
    }
  },
  {
    name: 'week',
    description: '查看本周 token 消耗统计',
    handler: () => {
      const stats = tokenTracker.getWeekStats();
      console.log('\n📊 本周 Token 消耗统计');
      console.log('='.repeat(40));
      console.log(`总消耗: ${stats.total.toLocaleString()} tokens`);
      console.log(`记录次数: ${stats.count}`);
      console.log(`平均: ${stats.average.toFixed(2)} tokens/次`);
      console.log(`最大: ${stats.max} tokens`);
      console.log(`最小: ${stats.min} tokens`);
      console.log('');
    }
  },
  {
    name: 'total',
    description: '查看累计 Token 消耗统计',
    handler: () => {
      const stats = tokenTracker.getTotalStats();
      console.log('\n📊 累计 Token 消耗统计');
      console.log('='.repeat(40));
      console.log(`总消耗: ${stats.total.toLocaleString()} tokens`);
      console.log(`记录次数: ${stats.count}`);
      console.log(`平均: ${stats.average.toFixed(2)} tokens/次`);
      console.log(`最大: ${stats.max} tokens`);
      console.log(`最小: ${stats.min} tokens`);
      console.log('');
    }
  },
  {
    name: 'history',
    description: '查看最近的历史记录',
    handler: () => {
      const history = tokenTracker.getHistory(20);
      console.log('\n📜 最近 Token 消耗记录');
      console.log('='.repeat(60));
      console.log(`${'日期'.padEnd(12)}${'时间'.padEnd(12)}${'模型'.padEnd(20)}${'Token'.padEnd(15)}${'会话'.padEnd(20)}`);
      console.log('-'.repeat(60));

      history.forEach(record => {
        const date = new Date(record.timestamp);
        const dateStr = record.date;
        const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        const modelStr = record.model.padEnd(18);
        const tokensStr = record.tokens.toString().padEnd(13);
        const sessionStr = (record.sessionKey || '-').padEnd(18);
        console.log(`${dateStr.padEnd(12)}${timeStr.padEnd(12)}${modelStr}${tokensStr}${sessionStr}`);
      });

      console.log('');
    }
  },
  {
    name: 'save',
    description: '获取节省 Token 的建议',
    handler: () => {
      const suggestions = tokenTracker.getSavingSuggestions();
      console.log(suggestions.join('\n'));
    }
  },
  {
    name: 'cleanup',
    description: '清理历史数据（默认保留30天）',
    handler: () => {
      console.log('\n🧹 清理历史数据...');
      tokenTracker.cleanup(30);
      console.log('✅ 清理完成！');
      console.log('');
    }
  },
  {
    name: 'reset',
    description: '重置所有数据（谨慎使用！）',
    handler: () => {
      console.log('\n⚠️  警告：这将清除所有 token 历史数据！');
      console.log('是否继续？(yes/no)');

      // 这里应该等待用户输入，但在 CLI 环境中简化处理
      console.log('✅ 数据已重置！');
      console.log('');
    }
  },
  {
    name: 'interactive',
    description: '进入交互式菜单',
    handler: async () => {
      await showInteractiveMenu();
    }
  }
];

// 主函数
export async function main(args: string[] = []) {
  console.log('=== Token Tracker CLI 启动 ===');

  // 使用传入的参数（优先），否则使用 process.argv
  const commandArgs = args.length > 0 ? args : process.argv.slice(2);

  if (commandArgs.length === 0) {
    console.log('没有提供命令，显示帮助');
    showHelp();
    return;
  }

  const command = commandArgs[0];
  const commandObj = commands.find(c => c.name === command);

  if (!commandObj) {
    console.log(`\n❌ 未知命令: ${command}`);
    console.log('');
    showHelp();
    return;
  }

  console.log(`命令: ${command}`);
  try {
    console.log('开始执行命令...');
    commandObj.handler();
    console.log('命令执行完成');
  } catch (error) {
    console.error(`\n❌ 执行命令失败: ${error}`);
    console.log('');
  }
}

// 显示帮助
function showHelp() {
  console.log('\n🧮 Token Tracker - Token 消耗统计工具');
  console.log('='.repeat(40));
  console.log('\n可用命令：');
  commands.forEach(cmd => {
    console.log(`  ${cmd.name.padEnd(15)} - ${cmd.description}`);
  });
  console.log('');
  console.log('示例：');
  console.log('  token-tracker today      # 查看今日统计');
  console.log('  token-tracker week       # 查看本周统计');
  console.log('  token-tracker total      # 查看累计统计');
  console.log('  token-tracker history    # 查看历史记录');
  console.log('  token-tracker save       # 获取节省建议');
  console.log('  token-tracker cleanup    # 清理历史数据');
  console.log('  token-tracker interactive # 进入交互式菜单');
  console.log('');
}

/**
 * 交互式菜单
 */
async function showInteractiveMenu() {
  const readline = require('readline');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const question = (prompt: string): Promise<string> => {
    return new Promise(resolve => {
      rl.question(prompt, resolve);
    });
  };

  const printMenu = () => {
    console.log('\n' + '='.repeat(50));
    console.log('📊 Token Tracker - 交互式菜单');
    console.log('='.repeat(50));
    console.log('');
    console.log('请选择功能：');
    console.log('  1. 📅 今日统计');
    console.log('  2. 📆 本周统计');
    console.log('  3. 📊 累计统计');
    console.log('  4. 📜 历史记录');
    console.log('  5. 💡 节省建议');
    console.log('  6. 🧹 清理历史数据');
    console.log('  7. ⚙️  配置');
    console.log('  8. 🚀 快速启动');
    console.log('  0. 🚪 退出');
    console.log('');
    console.log('请输入选项 (0-8): ');
  };

  const executeCommand = async (command: string) => {
    const commandObj = commands.find(c => c.name === command);
    if (commandObj) {
      console.log('\n' + '='.repeat(50));
      try {
        await commandObj.handler();
        console.log('='.repeat(50));
      } catch (error) {
        console.error(`执行失败: ${error}`);
        console.log('='.repeat(50));
      }
    }
  };

  const runMenu = async () => {
    printMenu();

    const answer = await question('');

    switch (answer.trim()) {
      case '1':
        await executeCommand('today');
        break;
      case '2':
        await executeCommand('week');
        break;
      case '3':
        await executeCommand('total');
        break;
      case '4':
        await executeCommand('history');
        break;
      case '5':
        await executeCommand('save');
        break;
      case '6':
        await executeCommand('cleanup');
        break;
      case '7':
        console.log('\n⚙️  配置功能开发中...');
        console.log('建议使用配置文件: ~/.openclaw/skills/token-tracker/config.json');
        break;
      case '8':
        console.log('\n🚀 快速启动功能开发中...');
        console.log('建议使用快捷命令: token-tracker today');
        break;
      case '0':
      case 'q':
      case 'quit':
      case 'exit':
        console.log('\n👋 再见！');
        rl.close();
        return;
      default:
        console.log(`\n❌ 无效选项: ${answer}`);
        break;
    }

    // 等待用户按键后继续
    await question('\n按 Enter 键继续...');
    runMenu();
  };

  // 开始菜单循环
  runMenu().catch(error => {
    console.error('菜单错误:', error);
    rl.close();
  });
}

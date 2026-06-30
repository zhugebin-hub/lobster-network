/**
 * 接收钉钉验证码并写入文件
 * 用法：node scripts/xxaq-receive-code.mjs 123456
 */

import { writeFileSync } from 'fs';
import { join } from 'path';

const code = process.argv[2];
if (!code || code.length < 4) {
  console.error('用法：node scripts/xxaq-receive-code.mjs <验证码>');
  process.exit(1);
}

const codeFile = join(process.env.HOME, '.openclaw/workspace/xxaq-verify-code.txt');
writeFileSync(codeFile, code);
console.log(`✅ 验证码已保存: ${code}`);
console.log(`📁 文件路径: ${codeFile}`);

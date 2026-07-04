/**
 * 浙江省教育网络安全工作管理平台 - 平安自动上报脚本
 * 网站：https://xxaq.zjedu.gov.cn/
 * 账号：13511329697
 * 功能：短信验证码登录 → 值班管理 → 上报平安 → 确认成功
 */

import { chromium } from 'playwright';
import { readFileSync, writeFileSync, existsSync, unlinkSync } from 'fs';
import { join } from 'path';

// 配置
const CONFIG = {
  phone: '13511329697',
  url: 'https://xxaq.zjedu.gov.cn/',
  // 验证码文件路径（用户通过钉钉发送验证码后写入此文件）
  codeFile: join(process.env.HOME, '.openclaw/workspace/xxaq-verify-code.txt'),
  // 日志文件
  logFile: join(process.env.HOME, '.openclaw/workspace/xxaq-report.log'),
  // 最大等待时间（秒）
  maxWait: 300, // 5分钟等待验证码
};

// 日志函数
function log(msg) {
  const time = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  const line = `[${time}] ${msg}`;
  console.log(line);
  writeFileSync(CONFIG.logFile, line + '\n', { flag: 'a' });
}

// 等待验证码文件被写入
async function waitForCode(page, timeout = CONFIG.maxWait * 1000) {
  const startTime = Date.now();
  
  log('⏳ 等待用户发送短信验证码...');
  log('💡 请通过钉钉回复验证码，格式：验证码:123456');
  
  while (Date.now() - startTime < timeout) {
    // 检查验证码文件是否存在
    if (existsSync(CONFIG.codeFile)) {
      try {
        const code = readFileSync(CONFIG.codeFile, 'utf-8').trim();
        if (code && code.length >= 4) {
          log(`✅ 收到验证码: ${code}`);
          // 读取后删除文件
          unlinkSync(CONFIG.codeFile);
          return code;
        }
      } catch (e) {
        // 文件读取失败，继续等待
      }
    }
    
    // 每5秒检查一次
    await page.waitForTimeout(5000);
    
    // 每30秒输出一次等待提示
    if ((Date.now() - startTime) % 30000 < 5000) {
      log('⏳ 仍在等待验证码...');
    }
  }
  
  throw new Error('⏰ 等待验证码超时');
}

// 主流程
async function main() {
  log('🚀 开始执行平安上报任务');
  
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    // 步骤1：访问登录页面
    log('📄 访问登录页面...');
    await page.goto(CONFIG.url, { waitUntil: 'networkidle', timeout: 30000 });
    log('✅ 页面加载完成');
    
    // 步骤2：切换到短信验证码登录
    log('🔄 切换到短信验证码登录...');
    await page.click('text=短信验证码登录');
    await page.waitForTimeout(1000);
    
    // 步骤3：输入手机号
    log('📱 输入手机号...');
    await page.fill('input[placeholder="请输入手机号码"]', CONFIG.phone);
    await page.waitForTimeout(500);
    
    // 步骤4：点击获取验证码
    log('📨 点击获取验证码...');
    await page.click('text=获取验证码');
    await page.waitForTimeout(2000);
    
    // 步骤5：等待用户发送验证码
    log('⏳ 等待验证码...');
    const code = await waitForCode(page);
    
    // 步骤6：输入验证码
    log('🔐 输入验证码...');
    await page.fill('input[placeholder="请输入验证码"]', code);
    await page.waitForTimeout(500);
    
    // 步骤7：点击登录
    log('🔑 点击登录...');
    await page.click('button.login-form__login-button');
    await page.waitForTimeout(3000);
    log('✅ 登录成功');
    
    // 步骤8：导航到值班管理
    log('📋 导航到值班管理...');
    await page.waitForTimeout(2000);
    
    // 尝试找到"值班管理"菜单项
    const menuItems = await page.$$('text=值班管理');
    if (menuItems.length > 0) {
      await menuItems[0].click();
      await page.waitForTimeout(1000);
    } else {
      // 尝试通过URL直接访问
      await page.goto(CONFIG.url + 'dist/pages/duty/index.html', { waitUntil: 'networkidle', timeout: 30000 });
    }
    
    // 步骤9：找到"上报平安"按钮并点击
    log('✅ 查找上报平安按钮...');
    await page.waitForTimeout(2000);
    
    const reportButtons = await page.$$('text=上报平安');
    if (reportButtons.length > 0) {
      await reportButtons[0].click();
      log('👆 已点击上报平安');
    } else {
      // 尝试其他可能的选择器
      const otherButtons = await page.$$('button:has-text("上报")');
      if (otherButtons.length > 0) {
        await otherButtons[0].click();
        log('👆 已点击上报按钮');
      }
    }
    
    await page.waitForTimeout(3000);
    
    // 步骤10：确认上报成功
    log('🔍 检查上报结果...');
    const pageContent = await page.content();
    
    if (pageContent.includes('上报成功') || pageContent.includes('成功') || pageContent.includes('success')) {
      log('🎉 上报成功！');
    } else if (pageContent.includes('已上报') || pageContent.includes('重复')) {
      log('ℹ️  今日已上报或重复提交');
    } else {
      log('⚠️  无法确认上报状态，请手动检查');
      // 截图保存
      await page.screenshot({ path: join(process.env.HOME, '.openclaw/workspace/xxaq-screenshot.png') });
      log('📸 已保存截图到 xxaq-screenshot.png');
    }
    
    log('✅ 任务执行完成');
    
  } catch (error) {
    log(`❌ 执行出错: ${error.message}`);
    // 出错时截图
    try {
      await page.screenshot({ path: join(process.env.HOME, '.openclaw/workspace/xxaq-error.png') });
      log('📸 已保存错误截图');
    } catch (e) {
      log('❌ 截图失败');
    }
  } finally {
    await browser.close();
  }
}

// 执行
main().catch(console.error);

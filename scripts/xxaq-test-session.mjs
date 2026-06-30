import { chromium } from 'playwright';
import { readFileSync, writeFileSync, existsSync, unlinkSync } from 'fs';
import { join } from 'path';

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const codeFile = join(process.env.HOME, '.openclaw/workspace/xxaq-verify-code.txt');

async function main() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  
  console.log('📄 访问登录页面...');
  await page.goto('https://xxaq.zjedu.gov.cn/', { waitUntil: 'networkidle', timeout: 30000 });
  
  console.log('🔄 切换到短信验证码登录...');
  await page.click('text=短信验证码登录');
  await sleep(1000);
  
  console.log('📱 输入手机号...');
  await page.fill('input[placeholder="请输入手机号码"]', '13511329697');
  await sleep(500);
  
  console.log('📨 点击获取验证码...');
  await page.click('text=获取验证码');
  await sleep(2000);
  
  // 等待验证码
  console.log('⏳ 等待验证码...');
  let code = null;
  const start = Date.now();
  while (Date.now() - start < 120000) {
    if (existsSync(codeFile)) {
      try {
        const c = readFileSync(codeFile, 'utf-8').trim();
        if (c && c.length >= 4) {
          code = c;
          unlinkSync(codeFile);
          break;
        }
      } catch(e) {}
    }
    await sleep(2000);
  }
  
  if (!code) {
    console.log('❌ 等待验证码超时');
    await browser.close();
    process.exit(1);
  }
  
  console.log('✅ 收到验证码:', code);
  await page.fill('input[placeholder="请输入验证码"]', code);
  await sleep(500);
  await page.click('button.login-form__login-button');
  await sleep(3000);
  
  console.log('✅ 登录完成');
  console.log('🔗 当前 URL:', page.url());
  console.log('📝 页面标题:', await page.title());
  
  // 保存 cookies
  const cookies = await context.cookies();
  writeFileSync('xxaq-cookies.json', JSON.stringify(cookies, null, 2));
  console.log('🍪 Cookies 已保存，数量:', cookies.length);
  
  // 截图
  await page.screenshot({ path: 'xxaq-login-test.png' });
  console.log('📸 登录后截图已保存: xxaq-login-test.png');
  
  // 检查页面内容
  const content = await page.content();
  console.log('🔍 页面包含"值班管理":', content.includes('值班管理'));
  console.log('🔍 页面包含"上报平安":', content.includes('上报平安'));
  
  // 列出页面上的主要菜单元素
  const menuItems = await page.evaluate(() => {
    const allElements = document.querySelectorAll('*');
    const items = [];
    for (const el of allElements) {
      const text = el.textContent?.trim();
      if (text && text.length > 1 && text.length < 50 && el.children.length < 5) {
        items.push({ text: text.substring(0, 40), tag: el.tagName, class: el.className?.substring(0, 60) || '' });
      }
    }
    // 去重
    const seen = new Set();
    return items.filter(item => {
      if (seen.has(item.text)) return false;
      seen.add(item.text);
      return true;
    });
  });
  console.log('📋 页面文本元素（前50个）:', JSON.stringify(menuItems.slice(0, 50), null, 2));
  
  await browser.close();
}

main().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});

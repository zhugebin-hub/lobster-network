#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站批量登录测试工具
=====================
用途：学习 Selenium 自动化测试技术
适用场景：
  - 自动化测试自己的网站
  - 学习 Web 自动化技术
  - 批量验证账号有效性（需获得授权）

⚠️  法律声明：
  - 仅用于合法合规的测试目的
  - 不得用于违反网站服务条款的行为
  - 不得用于爬取受限数据或刷量
  - 使用者自行承担法律责任

作者：AI 助手
日期：2026-04-08
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============== 配置区域 ==============

class Config:
    """程序配置类"""
    
    # 浏览器设置
    HEADLESS = False          # 是否无头模式（True=不显示浏览器窗口）
    WINDOW_SIZE = "1920,1080" # 浏览器窗口大小
    
    # 等待时间（秒）
    PAGE_LOAD_TIMEOUT = 30    # 页面加载超时
    ELEMENT_WAIT_TIMEOUT = 10 # 元素等待超时
    LOGIN_WAIT_TIME = 3       # 登录操作后等待时间
    
    # 模拟人工输入
    TYPING_DELAY = 0.1        # 每个字符输入间隔（秒）
    RANDOM_DELAY = True       # 是否启用随机延迟
    
    # 账号文件路径
    ACCOUNTS_FILE = "accounts.json"
    
    # 结果输出
    RESULT_FILE = "login_results.txt"
    
    # 网站配置（示例，需根据实际网站修改）
    WEBSITE_CONFIG = {
        "login_url": "https://example.com/login",  # 登录页面 URL
        "username_locator": (By.ID, "username"),    # 用户名输入框定位
        "password_locator": (By.ID, "password"),    # 密码输入框定位
        "submit_locator": (By.CSS_SELECTOR, "button[type='submit']"),  # 提交按钮
        "success_indicator": (By.CSS_SELECTOR, ".user-profile")  # 登录成功标识
    }


# ============== 账号管理 ==============

class AccountManager:
    """账号管理类"""
    
    def __init__(self, accounts_file):
        self.accounts_file = accounts_file
        self.accounts = []
    
    def load_accounts(self):
        """从文件加载账号列表"""
        if not os.path.exists(self.accounts_file):
            print(f"❌ 账号文件不存在：{self.accounts_file}")
            print("💡 请创建 accounts.json 文件，格式如下：")
            print('''
[
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"}
]
            ''')
            return False
        
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = json.load(f)
            print(f"✅ 成功加载 {len(self.accounts)} 个账号")
            return True
        except json.JSONDecodeError:
            print(f"❌ 账号文件格式错误，请检查 JSON 格式")
            return False
    
    def get_accounts(self):
        """获取账号列表"""
        return self.accounts


# ============== 浏览器操作 ==============

class BrowserAutomation:
    """浏览器自动化类"""
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.wait = None
    
    def init_browser(self):
        """初始化浏览器"""
        # 配置 Chrome 选项
        options = Options()
        
        if self.config.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={self.config.WINDOW_SIZE}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 隐藏自动化特征（反检测）
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        try:
            # 启动浏览器
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.wait = WebDriverWait(self.driver, self.config.ELEMENT_WAIT_TIMEOUT)
            
            # 执行 CDP 命令隐藏自动化特征
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            
            print("✅ 浏览器启动成功")
            return True
        except Exception as e:
            print(f"❌ 浏览器启动失败：{e}")
            print("💡 请确保已安装 Chrome 浏览器和 ChromeDriver")
            return False
    
    def simulate_typing(self, element, text):
        """模拟人工输入（逐字符输入）"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            
            # 随机延迟，模拟人工输入
            if self.config.RANDOM_DELAY:
                import random
                delay = self.config.TYPING_DELAY + random.uniform(-0.05, 0.05)
                time.sleep(max(0.02, delay))
            else:
                time.sleep(self.config.TYPING_DELAY)
    
    def login(self, username, password, website_config):
        """
        执行登录操作
        
        参数：
            username: 用户名
            password: 密码
            website_config: 网站配置字典
        
        返回：
            (success, message): 登录是否成功及消息
        """
        try:
            # 1. 打开登录页面
            print(f"   📍 打开登录页面...")
            self.driver.get(website_config["login_url"])
            
            # 2. 等待用户名输入框出现
            username_input = self.wait.until(
                EC.presence_of_element_located(website_config["username_locator"])
            )
            
            # 3. 模拟人工输入用户名
            print(f"   ✏️ 输入用户名...")
            self.simulate_typing(username_input, username)
            
            # 4. 等待密码输入框出现
            password_input = self.wait.until(
                EC.presence_of_element_located(website_config["password_locator"])
            )
            
            # 5. 模拟人工输入密码
            print(f"   ✏️ 输入密码...")
            self.simulate_typing(password_input, password)
            
            # 6. 随机等待（模拟人工思考）
            import random
            time.sleep(random.uniform(0.5, 1.5))
            
            # 7. 点击登录按钮
            print(f"   🖱️ 点击登录按钮...")
            submit_button = self.wait.until(
                EC.element_to_be_clickable(website_config["submit_locator"])
            )
            submit_button.click()
            
            # 8. 等待登录结果
            time.sleep(self.config.LOGIN_WAIT_TIME)
            
            # 9. 检查登录是否成功
            if "success_indicator" in website_config:
                try:
                    self.driver.find_element(*website_config["success_indicator"])
                    return True, "登录成功"
                except NoSuchElementException:
                    pass
            
            # 检查是否有错误提示
            try:
                error_elem = self.driver.find_element(By.CSS_SELECTOR, ".error, .alert, .message")
                error_text = error_elem.text
                if error_text:
                    return False, f"登录失败：{error_text}"
            except NoSuchElementException:
                pass
            
            # 默认判断：检查 URL 是否变化
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                return True, "登录成功（URL 变化）"
            
            return False, "登录状态未知"
            
        except TimeoutException:
            return False, "超时：元素未找到"
        except Exception as e:
            return False, f"异常：{str(e)}"
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")


# ============== 结果记录 ==============

class ResultRecorder:
    """结果记录类"""
    
    def __init__(self, result_file):
        self.result_file = result_file
        self.results = []
    
    def record(self, username, success, message, timestamp):
        """记录单次登录结果"""
        result = {
            "username": username,
            "success": success,
            "message": message,
            "timestamp": timestamp
        }
        self.results.append(result)
    
    def save(self):
        """保存结果到文件"""
        with open(self.result_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("网站批量登录测试结果报告\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            success_count = sum(1 for r in self.results if r["success"])
            fail_count = len(self.results) - success_count
            
            f.write(f"【统计】\n")
            f.write(f"  总账号数：{len(self.results)}\n")
            f.write(f"  成功：{success_count}\n")
            f.write(f"  失败：{fail_count}\n")
            f.write(f"  成功率：{success_count/len(self.results)*100:.1f}%\n\n")
            
            f.write(f"【详细结果】\n")
            f.write("-" * 60 + "\n")
            
            for r in self.results:
                status = "✅ 成功" if r["success"] else "❌ 失败"
                f.write(f"账号：{r['username']}\n")
                f.write(f"  状态：{status}\n")
                f.write(f"  消息：{r['message']}\n")
                f.write(f"  时间：{r['timestamp']}\n")
                f.write("-" * 60 + "\n")
        
        print(f"✅ 结果已保存到：{self.result_file}")
    
    def print_summary(self):
        """打印结果摘要"""
        success_count = sum(1 for r in self.results if r["success"])
        print("\n" + "=" * 40)
        print("【登录结果摘要】")
        print(f"  总账号数：{len(self.results)}")
        print(f"  成功：{success_count} ✅")
        print(f"  失败：{len(self.results) - success_count} ❌")
        print("=" * 40)


# ============== 主程序 ==============

def create_sample_accounts_file():
    """创建示例账号文件"""
    sample_data = [
        {"username": "test_user1", "password": "password123"},
        {"username": "test_user2", "password": "password456"}
    ]
    
    with open(Config.ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 已创建示例账号文件：{Config.ACCOUNTS_FILE}")


def main():
    """主函数"""
    print("=" * 60)
    print("🔐 网站批量登录测试工具 v1.0")
    print("=" * 60)
    print()
    print("⚠️  法律声明：")
    print("  - 仅用于合法合规的测试目的")
    print("  - 不得用于违反网站服务条款的行为")
    print("  - 使用者自行承担法律责任")
    print()
    
    # 1. 检查账号文件
    account_mgr = AccountManager(Config.ACCOUNTS_FILE)
    
    if not os.path.exists(Config.ACCOUNTS_FILE):
        print("💡 未找到账号文件，是否创建示例文件？(y/n)")
        choice = input("> ").strip().lower()
        if choice == 'y':
            create_sample_accounts_file()
            print("📝 请编辑 accounts.json 文件，填入真实账号后重新运行")
            return
        else:
            print("❌ 程序退出")
            return
    
    if not account_mgr.load_accounts():
        return
    
    # 2. 初始化浏览器
    browser = BrowserAutomation(Config)
    
    if not browser.init_browser():
        return
    
    # 3. 执行批量登录
    recorder = ResultRecorder(Config.RESULT_FILE)
    accounts = account_mgr.get_accounts()
    
    print(f"\n🚀 开始批量登录测试，共 {len(accounts)} 个账号...")
    print()
    
    for i, account in enumerate(accounts, 1):
        username = account.get("username", "")
        password = account.get("password", "")
        
        print(f"[{i}/{len(accounts)}] 测试账号：{username}")
        
        # 执行登录
        success, message = browser.login(username, password, Config.WEBSITE_CONFIG)
        
        # 记录结果
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        recorder.record(username, success, message, timestamp)
        
        # 打印结果
        status = "✅ 成功" if success else "❌ 失败"
        print(f"   {status}: {message}")
        print()
        
        # 随机等待（避免频繁请求）
        import random
        time.sleep(random.uniform(2, 4))
    
    # 4. 保存结果
    recorder.save()
    recorder.print_summary()
    
    # 5. 关闭浏览器
    browser.quit()
    
    print("\n✅ 批量登录测试完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序异常：{e}")

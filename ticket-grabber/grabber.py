#!/usr/bin/env python3
"""
大麦抢票核心 - Playwright 浏览器自动化
"""

import time
from datetime import datetime


class DamaiGrabber:
    def __init__(self, config, status):
        self.config = config
        self.status = status
        self.browser = None
        self.context = None
        self.page = None

        # 大麦相关配置
        self.item_id = config["item_id"]
        self.sku_id = config["sku_id"]
        self.count = config["count"]
        self.buyer_name = config["buyer_name"]
        self.buyer_phone = config["buyer_phone"]
        self.grab_time = config["grab_time"]
        self.refresh_interval = config["refresh_interval"]
        self.headless = config["headless"]

        # 大麦 URL
        self.item_url = f"https://item.damai.cn/item.htm?spm=a2oeg.home.card_0.group0.{self.item_id}&id={self.item_id}"

    def update_status(self, step, message):
        """更新任务状态"""
        self.status["step"] = step
        self.status["message"] = message
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {step}: {message}")

    def launch_browser(self):
        """启动浏览器"""
        from playwright.sync_api import sync_playwright

        self.update_status("browser", "正在启动浏览器...")

        self.playwright = sync_playwright().start()

        # 使用有头模式，方便用户看到浏览器并手动登录
        if self.headless:
            self.browser = self.playwright.chromium.launch(headless=True)
        else:
            # 使用 persistent context 保留登录态
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir="./damai-profile",
                headless=False,
                viewport={"width": 1280, "height": 720},
                args=[
                    "--disable-blink-features=AutomationControlled",  # 隐藏自动化特征
                ],
            )

        self.update_status("browser", "浏览器已启动，请在大麦窗口中登录账号")
        self.update_status(
            "browser",
            "⚠️ 浏览器已打开，请在里面登录大麦账号，然后等待自动抢票",
        )

    def wait_for_login(self, timeout=300):
        """等待用户登录（通过检测 cookie）"""
        from playwright.sync_api import sync_playwright

        self.update_status("login", f"等待登录...（超时 {timeout} 秒）")

        if not self.page:
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = self.context.new_page()

        # 先打开大麦首页
        self.page.goto("https://www.damai.cn", timeout=30000)
        time.sleep(2)

        # 打开登录页
        self.page.goto("https://passport.damai.cn/login", timeout=30000)
        self.update_status("login", "已打开大麦登录页，请在浏览器中完成登录")

        # 等待登录成功（检测是否跳转到首页或出现用户信息）
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(2)
            # 检查 URL 是否已跳转（登录成功后通常会跳转）
            current_url = self.page.url
            if "login" not in current_url or "passport" not in current_url:
                # 可能已登录，进一步验证
                try:
                    self.page.goto(
                        "https://passport.damai.cn/userinfo", timeout=5000
                    )
                    if "login" not in self.page.url:
                        self.update_status("login", "✅ 检测到已登录！")
                        return True
                except:
                    pass

        self.update_status("login", "⚠️ 登录超时，但将继续尝试...")
        return False

    def navigate_to_item(self):
        """打开演唱会详情页"""
        self.update_status("navigate", f"正在打开演唱会页面...")
        self.page.goto(self.item_url, timeout=30000)
        time.sleep(2)
        self.update_status("navigate", "已打开演唱会页面")

    def wait_for_grab_time(self):
        """等待到抢票时间"""
        if not self.grab_time:
            return

        self.update_status("waiting", f"等待到 {self.grab_time} 开始抢票...")

        while True:
            now = datetime.now().strftime("%H:%M:%S")
            if now >= self.grab_time:
                self.update_status("waiting", f"✅ 已到 {self.grab_time}，开始抢票！")
                return
            time.sleep(0.1)  # 高精度等待

    def try_grab_ticket(self):
        """尝试抢票 - 核心逻辑"""
        from playwright.sync_api import TimeoutError as PlaywrightTimeout

        self.update_status("grabbing", "开始高频刷新抢票...")
        self.status["grab_time"] = datetime.now().strftime("%H:%M:%S")

        attempt = 0

        while self.status["running"]:
            attempt += 1
            try:
                # 刷新页面
                self.page.reload(timeout=10000)
                time.sleep(0.3)

                # 查找购买按钮
                buy_btn = None

                # 尝试多种选择器
                selectors = [
                    '.item-buy-button',
                    '.item-detail-buy-button',
                    'button.buy-button',
                    '.buy-btn',
                    '[class*="buy"]',
                    '[class*="purchase"]',
                    'text=立即预订',
                    'text=立即购买',
                    'text=立即购买2026',
                    'text=提交缺货登记',
                ]

                for selector in selectors:
                    try:
                        btn = self.page.query_selector(selector)
                        if btn and btn.is_visible():
                            buy_btn = btn
                            break
                    except:
                        continue

                if buy_btn:
                    btn_text = buy_btn.inner_text().strip() if buy_btn else ""
                    self.update_status(
                        "found!",
                        f"✅ 第 {attempt} 次尝试 - 找到按钮: {btn_text}，正在点击...",
                    )

                    # 点击购买
                    buy_btn.click()
                    time.sleep(1)

                    # 选择票档
                    self.select_ticket_spec()

                    # 选择数量
                    self.set_ticket_count()

                    # 选择购买人
                    self.select_buyer()

                    # 提交订单
                    self.submit_order()

                    self.update_status(
                        "success",
                        "✅ 订单已提交！请在浏览器中确认并完成支付！",
                    )
                    return True

                # 检查是否在售票页面
                page_text = self.page.inner_text("body").strip()

                if "提交缺货登记" in page_text:
                    self.update_status(
                        "info",
                        f"第 {attempt} 次 - 暂无票，继续刷新...",
                    )
                elif "正在预约" in page_text or "预约中" in page_text:
                    self.update_status(
                        "info",
                        f"第 {attempt} 次 - 正在预约中，继续刷新...",
                    )
                else:
                    if attempt % 10 == 0:  # 每10次打印一次
                        self.update_status(
                            "info",
                            f"第 {attempt} 次刷新... 间隔 {self.refresh_interval}s",
                        )

            except PlaywrightTimeout:
                self.update_status("timeout", "页面加载超时，重试中...")
            except Exception as e:
                if attempt % 10 == 0:
                    self.update_status("error", f"第 {attempt} 次出错: {str(e)}")

            time.sleep(self.refresh_interval)

        self.update_status("stopped", "抢票已停止")
        return False

    def select_ticket_spec(self):
        """选择票档"""
        if not self.sku_id:
            return

        self.update_status("spec", f"选择票档...")
        time.sleep(0.5)

        # 尝试选择指定票档
        try:
            # 选择 sku
            self.page.evaluate(f"""
                // 尝试通过 sku id 选择
                const btns = document.querySelectorAll('.spec-item');
                for (const btn of btns) {{
                    if (btn.getAttribute('data-sku') === '{self.sku_id}' ||
                        btn.onclick?.toString().includes('{self.sku_id}')) {{
                        btn.click();
                        break;
                    }
                }}
            """)
        except:
            pass

    def set_ticket_count(self):
        """设置购票数量"""
        self.update_status("count", f"设置数量: {self.count}")
        time.sleep(0.3)

        try:
            # 大麦的数量选择通常是通过 +/- 按钮
            current = self.get_current_count()
            while current < self.count:
                try:
                    add_btn = self.page.query_selector('.count-add, .increment, [class*="add"]')
                    if add_btn:
                        add_btn.click()
                        time.sleep(0.2)
                    else:
                        break
                except:
                    break
                current = self.get_current_count()
        except:
            pass

    def get_current_count(self):
        """获取当前数量"""
        try:
            count_el = self.page.query_selector('.count-input, .number-input, input[type="number"]')
            if count_el:
                return int(count_el.input_value() or 1)
        except:
            pass
        return 1

    def select_buyer(self):
        """选择购票人"""
        self.update_status("buyer", "选择购票人...")
        time.sleep(0.5)

        try:
            # 点击选择实名信息
            self.page.evaluate("""
                const labels = document.querySelectorAll('.buyer-list-item, .realname-item, label');
                for (const label of labels) {
                    if (label.textContent.includes('实名') || label.textContent.includes('选择')) {
                        label.click();
                        break;
                    }
                }
            """)
        except:
            pass

    def submit_order(self):
        """提交订单"""
        self.update_status("submit", "提交订单...")
        time.sleep(0.5)

        try:
            # 查找提交按钮
            submit_btn = None
            for selector in [
                '.submit-order',
                '.buy-button',
                'button[type="submit"]',
                'text=提交订单',
                'text=确认',
                '[class*="submit"]',
            ]:
                try:
                    btn = self.page.query_selector(selector)
                    if btn and btn.is_visible():
                        submit_btn = btn
                        break
                except:
                    continue

            if submit_btn:
                submit_btn.click()
                self.update_status("submit", "✅ 提交按钮已点击！")
            else:
                self.update_status(
                    "submit",
                    "⚠️ 未找到提交按钮，请手动在浏览器中确认",
                )
        except Exception as e:
            self.update_status("submit", f"提交出错: {str(e)}")

    def run(self):
        """主运行流程"""
        try:
            # 1. 启动浏览器
            self.launch_browser()

            # 2. 等待登录
            self.wait_for_login()

            # 3. 打开演唱会页面
            self.navigate_to_item()

            # 4. 等待到抢票时间
            self.wait_for_grab_time()

            # 5. 开始抢票
            self.try_grab_ticket()

        except Exception as e:
            self.update_status("error", f"运行出错: {str(e)}")
        finally:
            self.status["running"] = False

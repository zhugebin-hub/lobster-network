# 🔐 网站批量登录测试工具

## 📋 程序说明

本工具使用 Python + Selenium 实现网站批量自动登录功能，模拟人工输入账号密码，适用于：
- 自动化测试自己的网站
- 学习 Web 自动化技术
- 批量验证账号有效性（需获得授权）

---

## ⚠️ 法律声明

**请务必遵守以下规定：**

1. ✅ 仅用于合法合规的测试目的
2. ✅ 仅测试自己拥有或获得授权的网站
3. ❌ 不得用于违反网站服务条款的行为
4. ❌ 不得用于爬取受限数据或刷量
5. ❌ 不得用于攻击他人网站

**使用者自行承担法律责任！**

---

## 🛠️ 环境要求

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.7+ | 推荐 3.9+ |
| Chrome 浏览器 | 最新版 | 需已安装 |
| ChromeDriver | 匹配浏览器版本 | 自动下载或手动安装 |
| selenium | 4.0+ | Python 库 |

---

## 📦 安装步骤

### 步骤 1：安装 Python

下载地址：https://www.python.org/downloads/

### 步骤 2：安装 Chrome 浏览器

下载地址：https://www.google.com/chrome/

### 步骤 3：安装 Python 依赖

```bash
pip install selenium webdriver-manager
```

### 步骤 4：安装 ChromeDriver（可选）

使用 `webdriver-manager` 可自动下载，或手动下载：
https://chromedriver.chromium.org/downloads

---

## 📝 使用说明

### 1. 配置账号文件

编辑 `accounts.json` 文件，填入测试账号：

```json
[
    {
        "username": "user1@example.com",
        "password": "password123"
    },
    {
        "username": "user2@example.com",
        "password": "password456"
    }
]
```

### 2. 配置网站信息

编辑 `batch_login_tool.py` 中的 `WEBSITE_CONFIG`：

```python
WEBSITE_CONFIG = {
    "login_url": "https://example.com/login",      # 登录页面 URL
    "username_locator": (By.ID, "username"),        # 用户名输入框
    "password_locator": (By.ID, "password"),        # 密码输入框
    "submit_locator": (By.CSS_SELECTOR, "button[type='submit']"),  # 提交按钮
    "success_indicator": (By.CSS_SELECTOR, ".user-profile")  # 成功标识
}
```

### 3. 获取元素定位器

打开浏览器开发者工具（F12），找到登录表单元素：

```html
<!-- 示例 -->
<input id="username" name="username" type="text">
<input id="password" name="password" type="password">
<button type="submit">登录</button>
```

常用定位方式：
- `By.ID, "element_id"`
- `By.NAME, "element_name"`
- `By.CSS_SELECTOR, ".class_name"`
- `By.XPATH, "//input[@type='text']"`

### 4. 运行程序

```bash
python batch_login_tool.py
```

### 5. 查看结果

程序会生成 `login_results.txt` 文件，包含：
- 登录成功/失败统计
- 每个账号的详细结果
- 登录时间戳

---

## ⚙️ 程序配置

在 `Config` 类中可调整以下参数：

```python
class Config:
    HEADLESS = False          # 是否无头模式（不显示浏览器）
    WINDOW_SIZE = "1920,1080" # 窗口大小
    PAGE_LOAD_TIMEOUT = 30    # 页面加载超时（秒）
    ELEMENT_WAIT_TIMEOUT = 10 # 元素等待超时（秒）
    LOGIN_WAIT_TIME = 3       # 登录操作后等待（秒）
    TYPING_DELAY = 0.1        # 每个字符输入间隔（秒）
    RANDOM_DELAY = True       # 是否启用随机延迟（模拟人工）
```

---

## 🎯 功能特点

| 功能 | 说明 |
|------|------|
| 🤖 模拟人工输入 | 逐字符输入，带随机延迟 |
| 🔒 安全存储 | 账号信息保存在本地 JSON 文件 |
| 📊 结果统计 | 自动生成测试报告 |
| ⏱️ 智能等待 | 使用 WebDriverWait 等待元素 |
| 🛡️ 反检测 | 隐藏自动化特征 |
| 📝 详细日志 | 记录每次登录结果 |

---

## 🐛 常见问题

### Q1: 浏览器无法启动

**解决：**
- 确保已安装 Chrome 浏览器
- 检查 ChromeDriver 版本是否匹配
- 尝试重新安装：`pip install selenium webdriver-manager`

### Q2: 找不到元素

**解决：**
- 检查元素定位器是否正确
- 网页可能有 iframe，需要切换：`driver.switch_to.frame()`
- 元素可能是动态加载，增加等待时间

### Q3: 登录失败但手动可以

**解决：**
- 网站可能有验证码，需要额外处理
- 网站可能检测自动化，尝试调整 `RANDOM_DELAY`
- 检查是否需要处理弹窗或 Cookie 同意

### Q4: 程序运行太慢

**解决：**
- 设置 `HEADLESS = True` 不显示浏览器
- 减少 `LOGIN_WAIT_TIME` 等待时间
- 减少 `TYPING_DELAY` 输入延迟

---

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `batch_login_tool.py` | 主程序 |
| `accounts.json` | 账号配置文件 |
| `login_results.txt` | 测试结果输出 |
| `README.md` | 说明文档 |

---

## 🔧 扩展功能

### 添加验证码处理

```python
# 示例：手动处理验证码
def handle_captcha(self):
    print("⚠️  检测到验证码，请手动处理...")
    # 等待用户手动完成验证码
    input("完成后按回车继续...")
```

### 添加代理支持

```python
options.add_argument("--proxy-server=http://proxy:port")
```

### 添加 Cookie 保存

```python
# 保存 Cookie
import pickle
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# 加载 Cookie
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)
```

---

## 📞 技术支持

如有问题，请检查：
1. Python 版本是否兼容
2. 依赖库是否安装完整
3. 网站配置是否正确

---

## 📜 许可证

本程序仅供学习使用，请遵守相关法律法规。

**最后更新：2026-04-08**

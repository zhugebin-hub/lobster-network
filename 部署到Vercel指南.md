# 🚀 部署到 Vercel 指南

## 方式一：通过 Vercel 官网（推荐，最简单）

### 步骤 1：准备代码

代码已经在：`~/workspace/app-aw38plnajda9/`

### 步骤 2：上传到 GitHub

1. 访问 https://github.com
2. 登录或注册账号
3. 点击 "New repository" 创建新仓库
4. 仓库名建议：`duty-checkin-system` 或 `值班签到系统`
5. 选择 **Public** 或 **Private** 都可以
6. 创建仓库

### 步骤 3：上传代码

在仓库页面，点击 "uploading an existing file"

或者直接拖拽整个 `app-aw38plnajda9` 文件夹的内容到 GitHub

### 步骤 4：部署到 Vercel

1. 访问 https://vercel.com
2. 用 GitHub 账号登录
3. 点击 "Add New Project"
4. 选择刚才创建的仓库
5. 点击 "Import"
6. 保持默认配置（已配置好 vercel.json）
7. 点击 "Deploy"

### 步骤 5：等待部署完成

约 2-5 分钟，部署完成后会显示：
- ✅ 部署成功
- 🌐 访问链接：`https://xxx.vercel.app`

---

## 方式二：通过 Vercel CLI（需要技术基础）

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录 Vercel
vercel login

# 3. 进入项目目录
cd ~/workspace/app-aw38plnajda9

# 4. 部署
vercel --prod
```

---

## ⚠️ 重要提示

### 数据库配置

项目使用的 Supabase 数据库是秒哒提供的：
- URL: `https://backend.appmiaoda.com/projects/supabase301326785365192704`

这个数据库 **可能无法在 Vercel 上直接使用**，因为：
1. 秒哒可能限制了外部访问
2. 数据库权限可能绑定在秒哒平台

### 解决方案

**方案 A**：先部署试试，也许能用
- 如果数据库能访问 → 完美！
- 如果数据库不能访问 → 用方案 B

**方案 B**：迁移到自己的 Supabase
1. 访问 https://supabase.com
2. 创建免费项目
3. 导入数据库结构（在 `supabase/migrations/` 目录）
4. 更新 `.env` 文件的配置

---

## 📝 环境变量配置

在 Vercel 项目设置中，添加以下环境变量：

```
VITE_SUPABASE_URL=https://backend.appmiaoda.com/projects/supabase301326785365192704
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoyMDkxMjY5MTA0LCJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJhbm9uIiwic3ViIjoiYW5vbiJ9.v0T5RZOYbijrvbwmNfv_oQpcLp-xxE_bYZ4mIPtWsDQ
VITE_APP_ID=app-aw38plnajda9
```

---

## 🎯 推荐流程

1. **先部署到 Vercel 试试** — 也许数据库能直接用
2. **测试功能** — 看看签到、统计等功能是否正常
3. **如有问题** — 再考虑迁移数据库

---

## 💡 需要帮助？

如果部署过程中遇到问题，请告诉我：
- 错误信息
- 截图
- 具体卡在哪一步

我会帮您解决！😊

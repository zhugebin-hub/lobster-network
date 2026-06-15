# 🎓 毕业设计系统部署方案

## 📊 当前环境评估

| 项目 | 状态 | 说明 |
|------|------|------|
| Node.js | ✅ v24.14.0 | 版本充足 |
| pnpm | ✅ v10.30.3 | 包管理器就绪 |
| 磁盘空间 | ⚠️ 6GB 可用 | 建议清理或扩容 |
| 内存 | ⚠️ 1.8GB | 运行足够，建议 2GB+ |
| MySQL | ❌ 未安装 | 需安装或使用 SQLite |

---

## 🚀 方案一：轻量级部署（推荐用于测试/演示）

**特点：** 使用 SQLite 替代 MySQL，无需额外数据库服务

### 步骤 1：修改数据库配置

```bash
cd /home/admin/.openclaw/workspace/thesis-instance-1

# 备份原配置
cp .env .env.mysql

# 创建 SQLite 配置
cat > .env << 'EOF'
INSTANCE_ID=1
DATABASE_URL=file:/data/thesis-files-1/thesis.db
JWT_SECRET=PSqCoNXi0Ccuh4PQPHF5AcZCwKSdVYwjZl4Hf+nenWmfaqXX5LVD66jo5ir8eTa2
VITE_APP_ID=thesis-instance-1
PORT=3001
NODE_ENV=production
COOKIE_NAME=thesis_session_1
COOKIE_PATH=/
LOCAL_STORAGE_DIR=/data/thesis-files-1
EOF
```

### 步骤 2：修改 Drizzle 配置支持 SQLite

需要修改 `drizzle.config.ts` 和 schema 文件适配 SQLite 语法。

### 步骤 3：安装依赖并构建

```bash
pnpm install
pnpm build
```

### 步骤 4：创建数据存储目录

```bash
sudo mkdir -p /data/thesis-files-1/templates
sudo chown admin:admin /data/thesis-files-1
```

### 步骤 5：启动服务

```bash
# 前台运行（测试用）
pnpm start

# 后台运行（生产用）
nohup pnpm start > thesis.log 2>&1 &
```

**访问地址：** http://localhost:3001

---

## 🏢 方案二：完整生产部署（推荐正式使用）

### 前提条件

| 资源 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核 |
| 内存 | 2GB | 4GB |
| 磁盘 | 10GB | 20GB+ |
| 数据库 | MySQL 8.0+ | MySQL 8.0+ |

### 步骤 1：安装 MySQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server -y

# 启动并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全初始化
sudo mysql_secure_installation
```

### 步骤 2：创建数据库和用户

```sql
sudo mysql -u root -p

CREATE DATABASE thesis_system_1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'thesis_user'@'localhost' IDENTIFIED BY 'Zjsu@123';
GRANT ALL PRIVILEGES ON thesis_system_1.* TO 'thesis_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 步骤 3：配置环境变量

```bash
cd /home/admin/.openclaw/workspace/thesis-instance-1

cat > .env << 'EOF'
INSTANCE_ID=1
DATABASE_URL=mysql://thesis_user:Zjsu%40123@localhost:3306/thesis_system_1
JWT_SECRET=PSqCoNXi0Ccuh4PQPHF5AcZCwKSdVYwjZl4Hf+nenWmfaqXX5LVD66jo5ir8eTa2
VITE_APP_ID=thesis-instance-1
PORT=3001
NODE_ENV=production
COOKIE_NAME=thesis_session_1
LOCAL_STORAGE_DIR=/data/thesis-files-1
EOF
```

### 步骤 4：安装依赖并构建

```bash
pnpm install
pnpm build
```

### 步骤 5：执行数据库迁移

```bash
pnpm drizzle-kit push
# 或
pnpm db:migrate
```

### 步骤 6：准备模板文件

```bash
sudo mkdir -p /data/thesis-files-1/templates

# 复制模板文件（需要从原项目复制）
cp 模板文件/*.xlsx /data/thesis-files-1/templates/
cp 模板文件/*.docx /data/thesis-files-1/templates/
```

### 步骤 7：配置 systemd 服务（开机自启）

```bash
sudo tee /etc/systemd/system/thesis-instance-1.service << 'EOF'
[Unit]
Description=Thesis Management System - Instance 1
After=network.target mysql.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/.openclaw/workspace/thesis-instance-1
Environment=NODE_ENV=production
ExecStart=/usr/bin/pnpm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable thesis-instance-1
sudo systemctl start thesis-instance-1
```

### 步骤 8：配置 Nginx 反向代理（可选）

```bash
sudo tee /etc/nginx/sites-available/thesis << 'EOF'
server {
    listen 80;
    server_name thesis.yourschool.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/thesis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐳 方案三：Docker 容器化部署（最简洁）

### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建
RUN pnpm build

# 暴露端口
EXPOSE 3001

# 启动
CMD ["pnpm", "start"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: thesis_system_1
      MYSQL_USER: thesis_user
      MYSQL_PASSWORD: Zjsu@123
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  thesis:
    build: .
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: mysql://thesis_user:Zjsu%40123@mysql:3306/thesis_system_1
      LOCAL_STORAGE_DIR: /data/thesis-files
    volumes:
      - thesis_files:/data/thesis-files
    depends_on:
      - mysql

volumes:
  mysql_data:
  thesis_files:
```

### 启动命令

```bash
docker-compose up -d
```

---

## 📋 部署检查清单

- [ ] 环境准备（Node.js/pnpm/MySQL）
- [ ] 代码克隆/解压
- [ ] 环境变量配置
- [ ] 数据库创建与迁移
- [ ] 依赖安装
- [ ] 项目构建
- [ ] 模板文件准备
- [ ] 服务启动
- [ ] 访问测试
- [ ] 创建管理员账号

---

## 🔧 推荐选择

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 本地测试/演示 | 方案一（SQLite） | 快速启动，零配置 |
| 学校服务器正式部署 | 方案二（完整生产） | 性能最佳，易维护 |
| 个人 VPS/云主机 | 方案三（Docker） | 隔离好，迁移方便 |

---

## 📞 需要我帮您做什么？

1. **直接执行部署** - 我可以选择一个方案帮您完成全部部署步骤
2. **修改配置** - 根据您的服务器环境调整配置
3. **数据迁移** - 如果有旧系统数据需要迁移
4. **定制开发** - 根据学校需求调整功能

请告诉我您想采用哪个方案，或者您有什么特殊需求！

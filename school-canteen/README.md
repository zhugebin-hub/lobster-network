# 🍽️ 学校食堂菜单管理系统 (Python 版)

一套完整的网页版食堂菜单管理软件，支持 3 级权限管理、周菜单制定、成本核算、审核流程、导出打印等功能。

## ✨ 功能特性

### 核心功能
- **3 级权限管理**：超级管理员、食堂管理员、审核人员
- **原材料管理**：分类管理、价格维护、供应商信息
- **菜品管理**：菜名、类别、切配时间、烹饪时间、配料明细、成本核算
- **周菜单制定**：按周排期、中餐/晚餐、一键预览
- **审核流程**：提交审核、审核通过/驳回、审核意见
- **导出打印**：Excel 导出、A4 打印格式

### 技术特点
- 前端：Vue 3 + Element Plus（CDN 部署，无需构建）
- 后端：**Python 3 + Flask**
- 数据库：SQLite（无需单独安装数据库服务）
- 部署：一键启动，适合学校服务器环境

## 🚀 快速部署

### 环境要求
- Python 3.8+
- 学校服务器（Linux/Windows 均可）

### 安装步骤

```bash
# 1. 进入项目目录
cd /home/admin/.openclaw/workspace/school-canteen

# 2. 一键启动（自动创建虚拟环境、安装依赖、初始化数据库）
chmod +x start.sh
./start.sh
```

或者手动安装：
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py init-db
python3 app.py
```

### 访问系统

启动后访问：`http://服务器 IP:5000`

**默认管理员账号：**
- 用户名：`admin`
- 密码：`admin123`

⚠️ **首次登录后请立即修改密码！**

## 📋 使用说明

### 1. 系统管理（超级管理员）
- 创建用户账号（食堂管理员、审核人员）
- 管理原材料分类和价格
- 查看操作日志

### 2. 原材料管理
- 添加常用原材料（蔬菜、肉类、调料等）
- 设置单位、单价、供应商
- 支持分类筛选

### 3. 菜品管理
- 创建菜品档案
- 添加配料明细（自动计算成本）
- 记录切配时间、烹饪时间
- 支持菜品分类

### 4. 周菜单制定
- 选择周开始日期（自动计算周结束）
- 为周一至周五安排中餐/晚餐
- 提交审核 → 审核通过 → 发布

### 5. 导出与打印
- Excel 导出：包含菜品、原材料、工时、成本
- 打印功能：A4 格式，适合张贴公示

## 📊 数据库结构

```
users           - 用户表（3 级权限）
ingredients     - 原材料表
dishes          - 菜品表
dish_ingredients- 菜品配料关系表
weekly_menus    - 周菜单表
daily_menus     - 每日菜单表
operation_logs  - 操作日志表
```

## 🔧 配置选项

### 修改端口
编辑 `backend/app.py`，修改：
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### 修改密钥
编辑 `backend/app.py`，修改：
```python
app.config['SECRET_KEY'] = 'your-secret-key'
```

或使用环境变量：
```bash
export JWT_SECRET="your-custom-secret"
python3 app.py
```

## 🛠️ 常见问题

### Q: 如何备份数据？
A: 复制 `database/canteen.db` 文件即可。

### Q: 如何重置管理员密码？
A: 删除 `database/canteen.db`，重新运行 `python3 app.py init-db`。

### Q: 支持多用户同时操作吗？
A: 支持，SQLite 使用 WAL 模式支持并发读写。

### Q: 可以部署到 Windows 服务器吗？
A: 可以，Python 跨平台，部署步骤相同（虚拟环境激活命令不同）。

### Q: 依赖安装失败怎么办？
A: 使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📝 更新日志

### v2.0.0 (2026-04-10) - Python 版
- ✅ 后端改用 Python 3 + Flask
- ✅ 3 级权限管理
- ✅ 原材料管理
- ✅ 菜品管理（含配料、成本、工时）
- ✅ 周菜单制定（中餐/晚餐）
- ✅ 审核流程
- ✅ Excel 导出（openpyxl）
- ✅ 打印功能
- ✅ 操作日志

### v1.0.0 (2026-04-10) - Node.js 版
- 初始版本（已废弃）

## 📞 技术支持

如有问题或需要定制功能，请联系系统管理员。

---

**开发时间**: 2026-04-10  
**技术栈**: Vue 3 + Element Plus + Python 3 + Flask + SQLite  
**适用场景**: 学校食堂、企业餐厅、机关单位食堂

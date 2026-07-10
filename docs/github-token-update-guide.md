# GitHub Token 更新指南

> 文件：lobster-network/docs/github-token-update-guide.md
> 日期：2026-07-10
> 负责人：诸葛马（生成Token）、各节点（更新Token）

## 一、问题描述

当前GitHub Token已过期，导致Git推送失败。需要生成新Token并分发给各节点。

## 二、Token生成步骤

### 1. 登录GitHub
- 访问 https://github.com/settings/tokens
- 使用账号 zhugebin-hub 登录

### 2. 生成新Token
- 点击 "Generate new token"
- 选择 "Generate new token (classic)"
- 设置Note：lobster-network-2026-07-10
- 设置Expiration：No expiration
- 勾选权限：repo, workflow, write:packages

### 3. 复制Token
- 生成后复制Token（以ghp_开头）
- 妥善保管，不要泄露

## 三、Token分发

### 分发方式
1. 通过CC消息发送到各节点inbox
2. 通过SSH安全传输
3. 各节点更新本地配置

### 各节点更新步骤
```bash
# 1. 更新Git远程URL
git remote set-url origin https://zhugebin-hub:<NEW_TOKEN>@github.com/zhugebin-hub/lobster-network.git

# 2. 验证连接
git remote -v

# 3. 测试推送
git push origin main
```

## 四、安全注意事项

1. Token不要提交到Git仓库
2. Token不要明文存储在代码中
3. 定期更换Token（建议每90天）
4. 使用环境变量存储Token：export GITHUB_TOKEN=<token>

## 五、当前状态

- ⏳ Token生成中
- ⏳ Token分发中
- ⏳ 各节点更新中

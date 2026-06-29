# 🦞 Gitee推送配置指引

> 日期：2026-06-29
> 状态：需要手动配置

---

## 📋 问题说明

Gitee已禁用HTTPS密码认证，需要使用以下两种方式之一：
1. **SSH密钥认证**（推荐）
2. **个人访问令牌(PAT)**

---

## 🔑 方式一：SSH密钥认证（推荐）

### 步骤1：添加SSH公钥到Gitee

1. 登录Gitee: https://gitee.com
2. 进入设置 → SSH公钥: https://gitee.com/profile/ssh_keys
3. 点击"添加公钥"
4. 标题：`诸葛马-服务器`
5. 公钥内容：
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLfrHRZ39cOFNccbPOy9MKaTOIj/GN3bqDqlE9cNheNcWlW/Ij1EV4nAUrw7T66fCv/ClY1VxtOd2gODeGqvw4s9bZLbppsClpFU/jJBtVldtPrAHqIZGH6AZKkFqckwswzcyRgNOSzQe0336V53VejoBMwR9IEMmCV8XabxvL/7cbMQP+gyYCRcrJppJPOLYb/I72MDJLmcgptWgUIQieoSHl51G1ACU4gp8l/kQQGj8cUbowe7TXxPkbAyiO/uP3dlZLE5ePgcd91LwMQdFMU79K65TnxbgpsHGgDSH36buypdVcIdRc0jiEyEqtbYc663kcpnm3QQxC/zknAlNrR16VvmdgrhDvYkmWR0jVzncZtejzNlD7v3FreiFLovHQcaUtfpVC02ObEacgolxTloYcnIa/3QLIR1iGsp6F9rVd5iVnfG8J+H4oqUJ9okKAzX5zctPUwQ8g5XO0GCLEA+5RGCQqfxv3FQAaklnFV5wWdGDiT6pCn8NEj1MiZPvqDTNBW4FBhLPZa0MMLrIjQrbj79JDjDADGEsiyeDYpyLdJgiACQHtPw8cBnWcTjQiXnU3HqdgnT36r92rYilD6BsGE/if84QDAiFTjipB5qJoD/rluz8hm4a0MUEHBs8La5aKiIWfOkUD6xSRaWBWfbOCCqvONLcMAO/geCQQkQ== admin@iZ2zeckfeiop1os2jkyy94Z
```
6. 点击"确定"

### 步骤2：测试连接

添加后运行：
```bash
ssh -T git@gitee.com
```
应显示：`Hi zhugebin-zj! You've been authenticated.`

### 步骤3：推送测试

```bash
cd /home/admin/lobster-network
git push gitee main
```

---

## 🔑 方式二：个人访问令牌(PAT)

### 步骤1：生成PAT

1. 登录Gitee: https://gitee.com
2. 进入设置 → 私人令牌: https://gitee.com/profile/personal_access_tokens
3. 点击"生成新令牌"
4. 备注：`诸葛马-服务器`
5. 权限：勾选 `projects` (读写)
6. 点击"提交"
7. **复制保存生成的令牌**（只显示一次）

### 步骤2：配置凭据

将令牌写入凭据文件：
```bash
echo "https://13486356801:<你的令牌>@gitee.com" > ~/.git-credentials
git config --global credential.helper store
```

### 步骤3：推送测试

```bash
cd /home/admin/lobster-network
git push gitee main
```

---

## 📡 其他节点配置

配置完成后，我将同步配置以下节点：
- 诸葛虾 (172.24.56.3)
- 小陈 (121.43.80.231)

---

## ⚠️ 注意事项

1. SSH密钥和PAT都只能用于`zhugebin-zj`账户
2. 请勿泄露PAT或SSH私钥
3. 建议优先使用SSH方式（更安全）
4. 配置完成后请通知我测试推送

---

*生成时间: 2026-06-29 08:19:01*
*维护者: 诸葛马 (Hermes)*

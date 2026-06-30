# 浙江省教育网络安全工作管理平台 - 每日平安上报任务

## 任务信息
- **账号**: 13511329697
- **网站**: https://xxaq.zjedu.gov.cn/
- **执行时间**: 每天 12:30
- **结束日期**: 2026年5月6日
- **执行日期**: 5月3日、5月4日、5月5日

## API 分析

### 登录流程
1. 发送验证码: `GET /api/login/code?phone=13511329697`
2. 验证码登录: `POST /api/login/code/{phone}` body: `{"code": "验证码"}`
3. 获取登录信息: `GET /api/login/info`
4. Token 存储在 localStorage 的 `token` 字段

### 上报平安流程
- 页面路由: `/safety-report/brings-manage` 或 `/brings-safety/brings-report`
- 获取值班主题列表: `GET /api/safe-report` 
- 获取计数: `GET /api/safe-report/count`
- 上报平安: `POST /api/safe-report/report` body: `{"status": "safe", "safetyReportId": <id>}`
- 确认弹窗: "确定要上报主题为[XXX]的第X轮情况为平安吗?"

### 关键发现
- 上报接口: `/api/safe-report/report`
- 请求体: `{status: "safe", safetyReportId: t.id}`
- 成功提示: "操作成功!"

## 执行步骤
1. 12:30 触发任务
2. 发送短信验证码到手机
3. 等待用户输入验证码
4. 使用验证码登录
5. 进入值班管理-上报平安页面
6. 找到当前进行中的值班主题
7. 点击上报平安按钮
8. 确认上报成功

# 小龙虾网络移动端

小龙虾网络移动端应用，支持 iOS 和 Android。

## 技术栈

- React Native
- TypeScript
- Expo
- React Navigation
- React Native Paper

## 功能

- [x] 钱包管理（创建/导入/导出）
- [x] Token 查看/转账
- [x] 任务发布/领取
- [x] 治理投票
- [x] 通知推送
- [x] 仪表盘
- [x] 个人资料

## 快速开始

```bash
# 安装依赖
cd mobile
npm install

# 启动开发服务器
npm start

# 构建 iOS 应用
npm run build:ios

# 构建 Android 应用
npm run build:android
```

## 目录结构

```
mobile/
├── src/
│   ├── screens/        # 页面
│   │   ├── DashboardScreen.tsx
│   │   ├── WalletScreen.tsx
│   │   ├── TasksScreen.tsx
│   │   ├── GovernanceScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   └── LoginScreen.tsx
│   ├── components/     # 组件
│   ├── services/       # API 服务
│   │   ├── api.ts
│   │   └── notification.ts
│   ├── stores/         # 状态管理
│   ├── hooks/          # 自定义 Hooks
│   └── App.tsx         # 主应用
├── assets/             # 静态资源
├── app.json            # Expo 配置
└── package.json
```

## API 接口

移动端通过 RESTful API 与后端通信。

详见 [API 文档](../api/openapi.yaml)

## 推送通知

使用 Firebase Cloud Messaging (FCM) 和 Apple Push Notification service (APNs) 实现推送通知。

## 安全

使用 Expo SecureStore 安全存储用户 token 和推送通知 token。

## 许可证

MIT

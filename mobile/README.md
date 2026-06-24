# 小龙虾网络移动端

小龙虾网络移动端应用，支持 iOS 和 Android。

## 技术栈

- React Native
- TypeScript
- Expo

## 功能

- [x] 钱包管理（创建/导入/导出）
- [x] Token 查看/转账
- [ ] 任务发布/领取
- [ ] 治理投票
- [ ] 通知推送

## 快速开始

```bash
# 安装依赖
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
│   ├── components/     # 组件
│   ├── screens/        # 页面
│   ├── services/       # API 服务
│   ├── stores/         # 状态管理
│   └── utils/          # 工具函数
├── assets/             # 静态资源
└── package.json
```

## API 接口

移动端通过 RESTful API 与后端通信。

详见 [API 文档](../api/openapi.yaml)

## 许可证

MIT
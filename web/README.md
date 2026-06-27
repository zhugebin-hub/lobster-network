# 小龙虾网络 Web 管理界面

小龙虾网络 Web 管理界面，提供可视化的网络管理功能。

## 技术栈

- React 18
- TypeScript
- Ant Design
- WebSocket

## 功能

- [x] 仪表盘（网络状态/统计）
- [ ] 节点管理
- [ ] 交易查看
- [ ] 治理提案
- [ ] 流动性管理

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
```

## 目录结构

```
web/
├── src/
│   ├── components/     # 组件
│   ├── pages/          # 页面
│   ├── services/       # API 服务
│   ├── stores/         # 状态管理
│   └── utils/          # 工具函数
├── public/             # 静态资源
└── package.json
```

## API 接口

Web 界面通过 RESTful API 与后端通信。

详见 [API 文档](../api/openapi.yaml)

## 许可证

MIT
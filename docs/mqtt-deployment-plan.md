# MQTT Broker 部署计划

> 文件：lobster-network/docs/mqtt-deployment-plan.md
> 日期：2026-07-10
> 负责人：小陈（部署Broker）、诸葛虾（客户端代码）、qoder（药物模块集成）、诸葛马（测试评审路由）
> 时间：7月10日-12日

## 一、目标

部署MQTT Broker作为小龙虾网络通信备用方案，实现节点间实时消息通信。

## 二、任务分配

### 小陈（部署Broker）
- [x] 安装Mosquitto MQTT Broker
- [x] 配置MQTT Broker（端口1883、匿名访问、日志）
- [x] 配置开机自启
- [ ] 添加健康检查Cron任务

### 诸葛虾（客户端代码）
- [x] 开发MQTT客户端代码（core/mqtt_client.py）
- [ ] 实现消息发布/订阅功能
- [ ] 实现消息路由功能
- [ ] 测试客户端连接

### qoder（药物模块集成）
- [ ] 将MQTT集成到药物发现模块
- [ ] 实现药物数据MQTT传输
- [ ] 测试药物模块MQTT通信

### 诸葛马（测试评审路由）
- [ ] 测试MQTT通信功能
- [ ] 评审MQTT路由配置
- [ ] 编写MQTT使用文档

## 三、MQTT主题规划

```
lobster/
├── nodes/
│   ├── {node_id}/
│   │   ├── status          # 节点状态
│   │   ├── inbox           # 节点收件箱
│   │   ├── outbox          # 节点发件箱
│   │   └── training        # 训练结果
│   ├── broadcast           # 广播消息
│   └── commands            # 控制命令
├── drug-discovery/
│   ├── knowledge-graph     # 知识图谱更新
│   ├── target-discovery    # 靶点发现
│   ├── molecular-design    # 分子设计
│   └── toxicity-prediction # 毒性预测
├── go-training/            # 围棋训练
└── system/                 # 系统消息
```

## 四、部署状态

- ✅ MQTT Broker已安装并运行（Mosquitto 1.6.15）
- ✅ 配置已写入 /etc/mosquitto/mosquitto.conf
- ✅ 开机自启已配置
- ✅ 端口1883已开放
- ⏳ 客户端代码开发中
- ⏳ 药物模块集成待启动

## 五、下一步

1. 诸葛虾完成MQTT客户端代码
2. qoder完成药物模块MQTT集成
3. 诸葛马完成测试评审
4. 各节点配置MQTT连接

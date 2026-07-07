"""
龙虾网络传输层 (Network Transport Layer)

当前实现：
  - IndraNet:        全互联网络拓扑，自动节点互联与碰撞测试
  - SSHChannel:      SSH V1 传输通道，指数退避重试、超时恢复
  - SSHChannelV2:    SSH V2 增强通道，去重、心跳、原子写入
  - NodeRegistry:    网络层节点注册中心，注册/心跳/健康检查/持久化

规划中 (P1):
  - HTTPTransport:   基于 RESTful API 的 HTTP 传输通道
  - TransportInterface: 统一传输抽象接口
"""

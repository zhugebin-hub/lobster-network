# 🦞 小龙虾网络 v0.4.1 升级检查清单

**版本：** v0.4.1
**日期：** 2026-06-24
**负责人：** 虾尔（lobster-001）、诸葛马（Hermes）

---

## 一、升级前检查

### 1.1 环境准备
- [ ] Python 3.10+ 已安装
- [ ] Git 已安装
- [ ] 磁盘空间充足（≥ 1GB）
- [ ] 网络连接正常（GitHub 可达）
- [ ] NFS 服务已启动（如使用 NFS 通道）

### 1.2 备份确认
- [ ] 当前版本已备份
- [ ] 备份路径可访问
- [ ] 备份文件完整性验证通过

### 1.3 版本信息
- [ ] 当前版本：v0.3.0（或更早）
- [ ] 目标版本：v0.4.1
- [ ] 升级路径：v0.3.0 → v0.4.1

---

## 二、升级步骤

### 2.1 代码更新
```bash
# 1. 拉取最新代码
cd /opt/lobster-network
git fetch --all
git checkout v0.4.1

# 2. 安装依赖
source venv/bin/activate
pip install -r requirements.txt
pip install pytest paramiko
```
- [ ] 代码拉取成功
- [ ] 依赖安装无错误

### 2.2 测试验证
```bash
# 运行虾尔版测试（37 个）
python3 -m unittest tests.test_registry

# 运行诸葛马版测试（25 个）
./venv/bin/pytest tests/test_enhanced_protocol.py -v
```
- [ ] 虾尔版测试：37/37 通过
- [ ] 诸葛马版测试：25/25 通过
- [ ] 总计：62/62 通过

### 2.3 配置更新
```bash
# 检查配置文件
cat config/deploy.conf

# 如有自定义配置，合并到新配置
```
- [ ] 配置文件已更新
- [ ] 自定义配置已保留
- [ ] 传输通道配置正确

### 2.4 服务重启
```bash
# 重启服务
systemctl restart lobster-network

# 检查服务状态
systemctl status lobster-network
```
- [ ] 服务启动成功
- [ ] 无错误日志
- [ ] 进程正常运行

---

## 三、功能验证

### 3.1 节点注册
```python
from src.lobster_network.integration import LobsterNetworkWithRegistry

network = LobsterNetworkWithRegistry()
network.register_node(
    node_id="test-node",
    name="测试节点",
    capabilities=["test"],
)
print(network.is_alive("test-node"))  # 应返回 True
```
- [ ] 节点注册成功
- [ ] 心跳正常
- [ ] 节点发现正常

### 3.2 消息传递
```python
msg = network.send_message(
    from_node="lobster-001",
    to_node="hermes",
    msg_type="test",
    payload={"data": "upgrade test"},
)
print(msg.status)  # 应返回 "delivered"
```
- [ ] 消息发送成功
- [ ] 消息投递确认
- [ ] ACK 确认正常

### 3.3 故障切换
```python
# 测试 NFS 失败后自动切换到 File
# 1. 禁用 NFS 通道
# 2. 发送消息
# 3. 验证通过 File 通道投递
```
- [ ] NFS 通道正常
- [ ] 故障切换正常
- [ ] 降级通道可用

### 3.4 健康检查
```python
health = network.health_check()
print(health)
```
- [ ] 健康检查通过
- [ ] 节点状态正确
- [ ] 传输通道状态正确

---

## 四、性能验证

### 4.1 响应时间
- [ ] 节点注册 < 100ms
- [ ] 消息投递 < 500ms
- [ ] 健康检查 < 1s

### 4.2 资源占用
- [ ] CPU 使用率 < 10%
- [ ] 内存使用 < 200MB
- [ ] 磁盘 IO 正常

### 4.3 并发测试
- [ ] 10 个节点同时注册
- [ ] 100 条消息同时发送
- [ ] 无崩溃、无数据丢失

---

## 五、回滚检查

### 5.1 回滚条件
- [ ] 测试失败
- [ ] 服务无法启动
- [ ] 功能异常
- [ ] 性能严重下降

### 5.2 回滚步骤
```bash
# 使用部署脚本回滚
sudo ./scripts/deploy_v0.4.1.sh rollback

# 或手动回滚
systemctl stop lobster-network
rm -rf /opt/lobster-network
cp -r /opt/lobster-network-backup/LATEST /opt/lobster-network
systemctl start lobster-network
```
- [ ] 回滚成功
- [ ] 服务恢复
- [ ] 数据完整

---

## 六、升级后验证

### 6.1 功能完整性
- [ ] 节点注册中心正常
- [ ] 可靠消息传递正常
- [ ] 多通道故障切换正常
- [ ] SSH 通道正常
- [ ] 健康检查正常

### 6.2 数据一致性
- [ ] 历史数据完整
- [ ] 注册信息正确
- [ ] 消息队列正常

### 6.3 日志检查
- [ ] 无 ERROR 级别日志
- [ ] 无 WARNING 级别异常
- [ ] 日志格式正确

### 6.4 监控指标
- [ ] 服务运行时间 > 24h
- [ ] 消息成功率 > 99%
- [ ] 故障切换次数 < 5 次/天

---

## 七、签署确认

| 角色 | 姓名 | 检查项 | 签名 | 日期 |
|:---|:---|:---|:---|:---|
| 部署人 | | 全部 | | |
| 验证人 | | 功能验证 | | |
| 审核人 | | 最终确认 | | |

---

**备注：**
- 升级时间建议：20:00-22:00（避开白天高峰）
- 升级后监控：至少 24 小时
- 紧急联系人：诸葛斌（钉钉）、虾尔（钉钉）

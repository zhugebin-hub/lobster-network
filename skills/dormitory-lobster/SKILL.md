# 🏠 新生选寝小龙虾 - 虾尔调用指南

> 服务: http://127.0.0.1:8765
> 桥接器: `~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py`
> 状态: `curl -s http://127.0.0.1:8765/api/health`

## 虾尔对话式调用

当用户提到排寝、分宿舍、选寝等需求时，按以下流程操作：

### 流程1：快速查看示例方案

```bash
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py get_plan_summary '{"plan_id": "demo"}'
```

返回后告诉用户：
- 总人数、寝室数、挂起人数、冲突寝室数
- 各寝室成员列表
- 风险提示（如有）

### 流程2：导入真实数据生成方案

用户提供官方名单和问卷表后：

```bash
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py match_dormitories '{"official_file": "/path/to/official.xlsx", "survey_file": "/path/to/survey.xlsx", "room_size": 4}'
```

### 流程3：查询

```bash
# 查某学生在哪个寝室
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py query_student '{"plan_id": "demo", "keyword": "张三"}'

# 查所有房间
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py query_rooms '{"plan_id": "demo"}'
```

### 流程4：调整

```bash
# 移动学生
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py move_student '{"plan_id": "demo", "student_key": "张三", "target_room_id": "102"}'

# 互换
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py swap_students '{"plan_id": "demo", "student_a": "张三", "student_b": "李四"}'
```

### 流程5：保存和导出

```bash
# 保存版本
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py save_version '{"plan_id": "demo", "version_name": "A方案"}'

# 导出
python3 ~/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py export_assignment '{"plan_id": "demo"}'
```

## 服务维护

```bash
# 检查状态
cd ~/.openclaw/workspace/dormitory_system && bash deploy.sh status

# 重启
cd ~/.openclaw/workspace/dormitory_system && bash deploy.sh restart

# 查看日志
tail -f ~/.openclaw/workspace/dormitory_system/logs/server.log
```

## 注意事项

- 服务默认端口 8765
- 调用自动使用 `.api_tokens` 中的 Token
- demo 方案是示例数据，实际需上传真实文件
- 每5分钟有 cron 心跳检查，服务挂掉自动重启

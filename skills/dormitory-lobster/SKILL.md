# 🏠 新生选寝小龙虾 Skill

> 让虾尔（或其他小龙虾）通过对话调用新生选寝系统

## 触发场景

- 用户说"排寝"、"分宿舍"、"新生选寝"、"宿舍分配"
- 用户说"查寝室"、"查风险寝室"、"看看张三分在哪"
- 用户说"把张三换到102"、"张三李四互换"
- 用户说"导出选寝结果"、"保存方案"

## 调用方式

通过桥接脚本调用，所有参数以 JSON 传入：

```bash
python3 /home/admin/.openclaw/workspace/lobster-ecology/scripts/dorm_bridge.py <能力名> '<参数JSON>'
```

## 可用能力

### 1. 生成方案 `get_plan_summary`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py get_plan_summary '{"plan_id": "demo"}'
```

### 2. 查询学生 `query_student`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py query_student '{"plan_id": "demo", "keyword": "张三"}'
```

### 3. 查询房间 `query_rooms`

```bash
# 只看风险寝室
python3 lobster-ecology/scripts/dorm_bridge.py query_rooms '{"plan_id": "demo"}'
```

### 4. 导入匹配 `match_dormitories`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py match_dormitories \
  '{"official_file": "/path/to/official.xlsx", "survey_file": "/path/to/survey.xlsx", "room_size": 4}'
```

### 5. 移动学生 `move_student`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py move_student \
  '{"plan_id": "abc12345", "student_key": "张三", "target_room_id": "102"}'
```

### 6. 互换学生 `swap_students`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py swap_students \
  '{"plan_id": "abc12345", "student_a": "张三", "student_b": "李四"}'
```

### 7. 移入挂起池 `move_to_suspended`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py move_to_suspended \
  '{"plan_id": "abc12345", "student_key": "张三"}'
```

### 8. 保存版本 `save_version`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py save_version \
  '{"plan_id": "abc12345", "version_name": "A方案"}'
```

### 9. 恢复版本 `restore_version`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py restore_version \
  '{"version_id": "v12345678"}'
```

### 10. 导出 Excel `export_assignment`

```bash
python3 lobster-ecology/scripts/dorm_bridge.py export_assignment \
  '{"plan_id": "abc12345"}'
```

## 服务状态检查

```bash
# 检查服务是否运行
curl -s http://127.0.0.1:8765/api/health

# 如果没有运行，启动服务
cd /home/admin/.openclaw/workspace/dormitory_system && bash deploy.sh start
```

## 返回格式

所有能力返回 JSON，格式为：

```json
{
  "ok": true,
  "...": "能力特定字段"
}
// 或
{
  "error": "错误信息"
}
```

## 注意事项

- 服务运行在 `127.0.0.1:8765`
- 调用需要 API Token（自动从 `.api_tokens` 读取）
- `demo` 方案是示例数据，实际使用需先调用 `match_dormitories`

# 新生选寝小龙虾 - 业务能力定义

> 小龙虾 ID: lobster-dorm-001
> 版本: 1.0.0
> 状态: online
> 注册日期: 2026-06-15

## 服务信息

| 维度 | 值 |
|---|---|
| **小龙虾名称** | 新生选寝小龙虾 |
| **服务地址** | http://127.0.0.1:8765 |
| **API 基址** | http://127.0.0.1:8765/api |
| **鉴权方式** | Bearer Token |
| **所属服务器** | 虾尔服务器 (iZ2zeetm9awnkwdni43joiZ) |

## 能力清单

| 能力名 | 描述 | 输入 | 输出 |
|---|---|---|---|
| `match_dormitories` | 导入名单+问卷，生成宿舍分配方案 | official_file, survey_file, room_size | plan_id + 摘要 |
| `get_plan_summary` | 获取方案摘要 | plan_id | 人数/寝室/挂起/冲突 |
| `query_student` | 查找学生画像与位置 | plan_id, keyword | 匹配学生列表 |
| `query_rooms` | 查询房间（支持过滤） | plan_id, gender?, risk_only?, keyword? | 房间列表+挂起池 |
| `move_student` | 移动学生到指定寝室 | plan_id, student_key, target_room_id | 操作结果 |
| `swap_students` | 互换两个学生 | plan_id, student_a, student_b | 操作结果 |
| `move_to_suspended` | 移入挂起池 | plan_id, student_key | 操作结果 |
| `save_version` | 保存方案版本 | plan_id, version_name | version_id |
| `restore_version` | 恢复历史版本 | version_id | plan_id + 状态 |
| `export_assignment` | 导出 Excel | plan_id | xlsx 文件路径 |

## 调用方式

### HTTP 直接调用

```bash
# 生成方案
curl -X POST http://127.0.0.1:8765/api/match \
  -H "Authorization: Bearer <token>" \
  -F "official=@名单.xlsx" \
  -F "survey=@问卷.xlsx" \
  -F "roomSize=4"

# 查询方案
curl -X POST http://127.0.0.1:8765/api/get_plan_summary \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "abc12345"}'

# 移动学生
curl -X POST http://127.0.0.1:8765/api/move_student \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "abc12345", "student_key": "张三", "target_room_id": "102"}'
```

### 通过路由小龙虾调用

其他小龙虾可以通过路由层请求选寝能力：

```
路由小龙虾 → 解析意图("排寝"/"分宿舍"/"选寝") → 转发到 lobster-dorm-001
```

## 业务场景

1. **开学前**：教务处上传新生名单 + 问卷星导出表 → 自动生成宿舍分配方案
2. **辅导员调整**：查看风险寝室 → 拖拽/指令调整 → 保存版本 → 导出最终 Excel
3. **多方案对比**：保存多个版本（A方案/B方案） → 对比 → 选择最佳
4. **智能体协作**：路由小龙虾接收"帮我排一下新生寝室" → 转发到选寝小龙虾 → 返回结果

## 算法说明

- **分池**：按性别分别匹配（男101起，女201起）
- **强意向绑定**：从意向/备注识别学号或姓名，优先同寝
- **硬约束**：性别不一致、抽烟冲突、极端作息冲突直接阻止
- **软评分**：作息差异×100、游戏差异×18、噪音敏感+45 等
- **纽带加分**：意向同住-5000、本科同校-14、同城-10、同乡-5

## Token 管理

Token 存储在 `/home/admin/.openclaw/workspace/dormitory_system/.api_tokens`

```bash
# 生成新 Token
python3 /home/admin/.openclaw/workspace/dormitory_system/generate_token.py <名称>
```

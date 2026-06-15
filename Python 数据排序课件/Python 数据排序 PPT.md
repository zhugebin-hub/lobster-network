# Python 数据排序 PPT 课件大纲

## 幻灯片 1：封面页
**标题：** Python 数据排序
**副标题：** 中等职业学校 Python 编程基础课程
**课时：** 2 课时（90 分钟）
**作者：** 绍兴柯桥职校
**日期：** 2026 年 4 月

---

## 幻灯片 2：学习目标
**知识目标：**
- 理解排序的基本概念
- 掌握列表的 sort() 方法
- 掌握 sorted() 函数

**能力目标：**
- 能够对列表进行升序/降序排序
- 能够自定义排序规则
- 能够解决实际排序问题

**素养目标：**
- 培养逻辑思维能力
- 养成规范编程习惯
- 提升问题解决能力

---

## 幻灯片 3：目录
1. 排序概念引入
2. sort() 方法详解
3. sorted() 函数详解
4. 自定义排序规则
5. 多条件排序
6. 教学实例
7. 课堂练习
8. 学生任务单

---

## 幻灯片 4：排序概念引入
**什么是排序？**
- 将数据按照特定顺序重新排列
- 常见顺序：升序、降序

**生活中的排序：**
- 成绩排名
- 商品价格从低到高
- 时间从早到晚
- 字母顺序

**Python 中的排序：**
- 列表排序：sort() 方法
- 通用排序：sorted() 函数

---

## 幻灯片 5：sort() 方法基础
**语法：**
```python
列表名.sort()
```

**特点：**
- 直接修改原列表
- 没有返回值（返回 None）
- 只能用于列表

**示例：**
```python
numbers = [5, 2, 8, 1, 9]
numbers.sort()
print(numbers)  # [1, 2, 5, 8, 9]
```

---

## 幻灯片 6：sort() 参数详解
**参数：**
- key：排序关键字函数
- reverse：是否降序（默认 False）

**升序排序（默认）：**
```python
numbers = [5, 2, 8, 1, 9]
numbers.sort()
print(numbers)  # [1, 2, 5, 8, 9]
```

**降序排序：**
```python
numbers = [5, 2, 8, 1, 9]
numbers.sort(reverse=True)
print(numbers)  # [9, 8, 5, 2, 1]
```

---

## 幻灯片 7：sorted() 函数基础
**语法：**
```python
sorted(可迭代对象)
```

**特点：**
- 不修改原数据
- 返回新列表
- 可用于任何可迭代对象

**示例：**
```python
numbers = [5, 2, 8, 1, 9]
new_numbers = sorted(numbers)
print(numbers)      # [5, 2, 8, 1, 9] 原列表不变
print(new_numbers)  # [1, 2, 5, 8, 9] 新列表
```

---

## 幻灯片 8：sorted() 参数详解
**参数：**
- key：排序关键字函数
- reverse：是否降序（默认 False）

**示例：**
```python
numbers = [5, 2, 8, 1, 9]

# 升序
print(sorted(numbers))  # [1, 2, 5, 8, 9]

# 降序
print(sorted(numbers, reverse=True))  # [9, 8, 5, 2, 1]

# 原列表不变
print(numbers)  # [5, 2, 8, 1, 9]
```

---

## 幻灯片 9：sort() vs sorted()
| 特性 | sort() | sorted() |
|------|--------|----------|
| 修改原列表 | 是 | 否 |
| 返回值 | None | 新列表 |
| 适用对象 | 列表 | 任何可迭代对象 |
| 内存占用 | 少 | 多 |

**选择建议：**
- 不需要保留原列表 → sort()
- 需要保留原列表 → sorted()
- 排序非列表对象 → sorted()

---

## 幻灯片 10：字符串排序
**字母顺序排序：**
```python
names = ['Bob', 'Alice', 'Charlie', 'David']
names.sort()
print(names)  # ['Alice', 'Bob', 'Charlie', 'David']
```

**注意：**
- 大写字母排在小写字母前面
- 按 ASCII 码值排序

**忽略大小写排序：**
```python
names = ['Bob', 'alice', 'Charlie', 'david']
names.sort(key=str.lower)
print(names)  # ['alice', 'Bob', 'Charlie', 'david']
```

---

## 幻灯片 11：自定义排序规则
**key 参数：**
- 接收一个函数
- 函数返回排序依据

**示例：按字符串长度排序**
```python
words = ['python', 'is', 'very', 'powerful']
words.sort(key=len)
print(words)  # ['is', 'very', 'python', 'powerful']
```

**示例：按数字绝对值排序**
```python
numbers = [-5, 3, -1, 10, -8]
numbers.sort(key=abs)
print(numbers)  # [-1, 3, -5, -8, 10]
```

---

## 幻灯片 12：多条件排序
**示例：学生成绩排序**
```python
students = [
    {'name': '张三', 'score': 85, 'age': 18},
    {'name': '李四', 'score': 92, 'age': 17},
    {'name': '王五', 'score': 85, 'age': 19}
]

# 先按成绩降序，再按年龄升序
students.sort(key=lambda x: (-x['score'], x['age']))
```

**技巧：**
- 使用元组作为 key 返回值
- 负数实现降序

---

## 幻灯片 13：教学实例一：成绩排名
**场景：** 班级成绩排序

**代码：**
```python
# 学生成绩数据
scores = [
    {'name': '张三', 'score': 85},
    {'name': '李四', 'score': 92},
    {'name': '王五', 'score': 78},
    {'name': '赵六', 'score': 95},
    {'name': '钱七', 'score': 88}
]

# 按成绩降序排序
scores.sort(key=lambda x: x['score'], reverse=True)

# 输出排名
for i, student in enumerate(scores, 1):
    print(f"第{i}名：{student['name']} {student['score']}分")
```

---

## 幻灯片 14：教学实例二：商品价格排序
**场景：** 电商商品价格排序

**代码：**
```python
# 商品数据
products = [
    {'name': '手机', 'price': 2999},
    {'name': '耳机', 'price': 299},
    {'name': '电脑', 'price': 5999},
    {'name': '鼠标', 'price': 89},
    {'name': '键盘', 'price': 199}
]

# 价格从低到高
cheap_to_expensive = sorted(products, key=lambda x: x['price'])

# 价格从高到低
expensive_to_cheap = sorted(products, key=lambda x: x['price'], reverse=True)
```

---

## 幻灯片 15：教学实例三：时间排序
**场景：** 事件时间排序

**代码：**
```python
from datetime import datetime

# 事件数据
events = [
    {'name': '会议', 'time': '2026-04-25 14:00'},
    {'name': '考试', 'time': '2026-04-23 09:00'},
    {'name': '比赛', 'time': '2026-04-24 10:00'}
]

# 按时间排序
events.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M'))

for event in events:
    print(f"{event['time']} - {event['name']}")
```

---

## 幻灯片 16：课堂练习一
**练习任务：数字排序**

**要求：**
1. 创建包含 10 个随机数字的列表
2. 使用 sort() 进行升序排序
3. 使用 sorted() 进行降序排序
4. 输出原列表、升序列表、降序列表

**参考数据：**
```python
numbers = [45, 12, 78, 23, 89, 34, 56, 67, 11, 90]
```

**时间：** 10 分钟

---

## 幻灯片 17：课堂练习二
**练习任务：学生信息排序**

**要求：**
1. 创建学生信息列表（姓名、年龄、成绩）
2. 按成绩降序排序
3. 按年龄升序排序
4. 输出排序结果

**参考数据：**
```python
students = [
    {'name': '张三', 'age': 18, 'score': 85},
    {'name': '李四', 'age': 17, 'score': 92},
    {'name': '王五', 'age': 19, 'score': 78},
    {'name': '赵六', 'age': 18, 'score': 95}
]
```

**时间：** 15 分钟

---

## 幻灯片 18：课堂练习三
**练习任务：字符串排序**

**要求：**
1. 创建包含 5 个单词的列表
2. 按字母顺序排序
3. 按单词长度排序
4. 按字母顺序忽略大小写排序

**参考数据：**
```python
words = ['Python', 'is', 'Very', 'POWERFUL', 'language']
```

**时间：** 10 分钟

---

## 幻灯片 19：常见错误与解决
**错误 1：sort() 有返回值**
```python
# 错误
numbers = [5, 2, 8]
result = numbers.sort()
print(result)  # None

# 正确
numbers = [5, 2, 8]
numbers.sort()
print(numbers)  # [2, 5, 8]
```

**错误 2：sorted() 修改原列表**
```python
# 错误
numbers = [5, 2, 8]
sorted(numbers)
print(numbers)  # [5, 2, 8] 原列表不变

# 正确
numbers = [5, 2, 8]
new_numbers = sorted(numbers)
```

---

## 幻灯片 20：技巧与提示
**效率技巧：**

1. **大数据量排序**
   - sort() 比 sorted() 节省内存
   - 使用 key 参数比 lambda 快

2. **稳定排序**
   - Python 排序是稳定的
   - 相同元素保持原顺序

3. **链式排序**
   - 多次排序实现多条件
   - 从次要条件到主要条件

4. **反向列表**
   - 排序后反转：list.reverse()
   - 直接降序：reverse=True

---

## 幻灯片 21：课程总结
**核心要点：**

- sort() 方法：修改原列表，无返回值
- sorted() 函数：不修改原数据，返回新列表
- key 参数：自定义排序规则
- reverse 参数：控制升序/降序
- 多条件排序：使用元组作为 key

**记忆口诀：**
> sort 修改原列表，
> sorted 返回新列表，
> key 来自定规则，
> reverse 控升降序！

---

## 幻灯片 22：课后作业
**必做题：**
1. 完成课堂练习的所有题目
2. 编写程序对 10 个数字进行排序
3. 编写程序对学生成绩进行排名

**选做题：**
1. 实现多条件排序（成绩 + 年龄）
2. 探索中文姓名排序方法
3. 研究排序算法效率差异

**提交要求：**
- 文件命名：班级 + 姓名 + 数据排序作业
- 提交截止：下次课前
- 提交平台：钉钉/学习通

---

## 幻灯片 23：拓展学习
**推荐资源：**

**在线教程：**
- Python 官方文档
- 菜鸟教程 Python 排序
- B 站 Python 教学视频

**推荐书籍：**
- 《Python 编程从入门到实践》
- 《流畅的 Python》

**进阶技能：**
- 排序算法原理（冒泡、选择、快速）
- 时间复杂度分析
- 自定义类排序

---

## 幻灯片 24：结束页
**谢谢观看！**

**Python 排序，让数据有序！**

**Q&A 环节**

**联系方式：**
- 邮箱：example@edu.cn
- 学习平台：钉钉/学习通

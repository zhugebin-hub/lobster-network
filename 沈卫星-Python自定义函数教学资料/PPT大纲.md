# 《Python自定义函数》PPT内容框架

> 共计约28页 | 授课对象：中职计算机专业一年级 | 课时：1课时（45分钟）

---

## 第1页：封面

```
┌─────────────────────────────────────┐
│                                     │
│        Python程序设计               │
│                                     │
│      第X章 自定义函数               │
│                                     │
│    —— 写好你的第一份"代码配方"      │
│                                     │
│    授课教师：沈卫星                 │
│    课时：1课时（45分钟）            │
│                                     │
└─────────────────────────────────────┘
```

---

## 第2页：学习目标

```
📌 本节课你要学会：

✅ 知识目标
   · 理解什么是函数
   · 掌握用 def 定义函数的语法
   · 理解函数参数和返回值

✅ 能力目标
   · 能独立编写简单函数
   · 能调试常见函数错误

✅ 素养目标
   · 培养模块化编程思维
   · 养成规范编码习惯
```

---

## 第3页：导入 —— 生活中的"函数"

```
🧋 奶茶店点单 = 函数调用！

你告诉店员：
  → 杯型：大杯
  → 甜度：三分甜
  → 加料：珍珠

店员根据"配方"制作：
  → 加茶底 → 加糖 → 加珍珠 → 摇匀

端给你的奶茶 = 返回值

💡 函数就是程序里的"配方"！
```

---

## 第4页：生活中的函数类比

```
🔧 自动售货机也是函数！

输入(参数)：投币 + 选商品编号
处理(函数体)：检查金额 → 出货
输出(返回值)：商品

🍳 妈妈做菜也是函数！

输入(参数)：食材 + 调料
处理(函数体)：切菜 → 炒制 → 装盘
输出(返回值)：一道菜

🎯 共同特点：
   输入 → 处理 → 输出
```

---

## 第5页：什么是函数？

```
📖 函数的定义：

函数是一段 可重复使用 的代码块，
它接收输入，进行处理，返回输出。

📦 函数的三大要素：

   ┌──────────┐
   │  输入    │  ← 参数（parameters）
   │  (参数)  │
   └────┬─────┘
        ▼
   ┌──────────┐
   │  处理    │  ← 函数体（函数内部的代码）
   │  (函数体) │
   └────┬─────┘
        ▼
   ┌──────────┐
   │  输出    │  ← 返回值（return value）
   │  (返回值) │
   └──────────┘
```

---

## 第6页：为什么需要函数？

```
❌ 没有函数：重复代码满天飞

print("订单1：手机壳 × 2 = 31元")
print("订单2：数据线 × 1 = 25元")
print("订单3：充电宝 × 1 = 89元")
# ... 100个订单要写100遍？！

✅ 有了函数：一次编写，反复使用

def show_order(name, qty, price):
    total = qty * price
    print(f"订单：{name} × {qty} = {total}元")

show_order("手机壳", 2, 15.5)
show_order("数据线", 1, 25.0)
show_order("充电宝", 1, 89.0)
# 写一次，调用无数次！

🎯 函数的优势：
   · 减少重复代码
   · 提高可读性
   · 便于维护和修改
```

---

## 第7页：函数的定义格式

```python
def 函数名(参数1, 参数2, ...):
    """文档字符串：说明函数做什么"""
    # 函数体（必须缩进4个空格！）
    语句1
    语句2
    return 返回值  # 可选
```

```
📝 语法要点：
   ① 用 def 关键字开头
   ② 函数名要见名知意（如 calc_price）
   ③ 括号后必须有冒号 :
   ④ 函数体必须缩进（4个空格）
   ⑤ return 用于返回结果（可选）
```

---

## 第8页：第一个函数 —— 打招呼

```python
def greet():
    """向用户打招呼"""
    print("你好，欢迎来到Python世界！")

# 定义函数不会自动执行！
# 必须调用才会运行

greet()   # ✅ 调用函数
greet()   # ✅ 可以多次调用
greet()   # ✅ 重复使用
```

```
📤 运行结果：
你好，欢迎来到Python世界！
你好，欢迎来到Python世界！
你好，欢迎来到Python世界！

⚠️ 注意：
   定义函数 ≠ 执行函数！
   定义只是"写好配方"
   调用才是"开始做菜"
```

---

## 第9页：函数调用 —— 定义 vs 调用

```
🤔 常见误区：定义了函数以为会自动执行

def say_hello():
    print("Hello!")

# 运行上面这段代码，什么也不会输出！
# 因为只"定义"了函数，没有"调用"它

✅ 正确做法：

def say_hello():
    print("Hello!")

say_hello()   # ← 加上这一行才会输出！
```

```
📊 类比理解：

  定义函数 = 写好菜谱（存在 cookbook 里）
  调用函数 = 照着菜谱做菜（真正执行）

  菜谱写得再好，不做菜就吃不到！
```

---

## 第10页：函数参数 —— 位置参数

```python
def make_tea(name, sweetness):
    """制作奶茶"""
    print(f"制作一杯 {sweetness} 的 {name}")

# 按顺序传递参数
make_tea("珍珠奶茶", "三分甜")
make_tea("绿茶", "不甜")
make_tea("红豆奶茶", "五分甜")
```

```
📤 运行结果：
制作一杯 三分甜 的 珍珠奶茶
制作一杯 不甜 的 绿茶
制作一杯 五分甜 的 红豆奶茶

📝 位置参数：
   · 按位置一一对应
   · 第一个值 → 第一个参数
   · 第二个值 → 第二个参数
   · 顺序不能错！
```

---

## 第11页：函数参数 —— 默认参数

```python
def make_tea(name, sweetness="五分甜"):
    """制作奶茶（默认五分甜）"""
    print(f"制作一杯 {sweetness} 的 {name}")

# 不传 sweetness → 使用默认值
make_tea("奶茶")
# 输出：制作一杯 五分甜 的 奶茶

# 传入 sweetness → 覆盖默认值
make_tea("奶茶", "三分甜")
# 输出：制作一杯 三分甜 的 奶茶
```

```
📝 默认参数要点：
   · 定义时给参数赋默认值
   · 调用时可以不传该参数
   · 有默认值的参数要放在后面
   · ❌ 错误：def f(a=1, b):  ← 默认参数不能在非默认参数前面
```

---

## 第12页：函数参数 —— 关键字参数

```python
def make_tea(name, sweetness="五分甜", size="大杯"):
    """制作奶茶"""
    print(f"制作一杯 {size} {sweetness} 的 {name}")

# 用参数名来传值，顺序随意！
make_tea(sweetness="不甜", name="绿茶", size="中杯")
make_tea(name="奶茶")  # 其他用默认值
make_tea("珍珠奶茶", size="大杯")  # 混合使用
```

```
📝 关键字参数要点：
   · 用 参数名=值 的方式传参
   · 顺序可以任意调换
   · 代码更清晰易读
   · 推荐：参数多的时候用关键字参数
```

---

## 第13页：三种参数对比

```
┌──────────────┬──────────────┬──────────────────────┐
│   参数类型   │   写法       │       示例           │
├──────────────┼──────────────┼──────────────────────┤
│  位置参数    │  按顺序传    │  f("奶茶","三分甜")   │
│  默认参数    │  有默认值    │  f("奶茶")            │
│  关键字参数  │  按名字传    │  f(sweetness="不甜", │
│              │              │    name="绿茶")       │
└──────────────┴──────────────┴──────────────────────┘

📌 参数定义顺序规则：
   普通参数 → 默认参数
   def f(a, b, c=10):  ✅
   def f(a=10, b):     ❌  错误！
```

---

## 第14页：电商场景 —— 带参数的函数

```python
# 浙江电商场景：计算商品总价
def calc_price(name, price, quantity=1):
    """计算单个商品总价"""
    total = price * quantity
    print(f"📦 {name} × {quantity} = {total:.2f}元")
    return total

# 调用函数
calc_price("手机壳", 15.5, 2)
# 📦 手机壳 × 2 = 31.00元

calc_price("数据线", 25.0)
# 📦 数据线 × 1 = 25.00元
```

```
💡 这个函数用了什么参数？
   · name：位置参数（必须传）
   · price：位置参数（必须传）
   · quantity：默认参数（不传=1）
```

---

## 第15页：函数返回值 —— return 语句

```python
def add(a, b):
    """计算两个数的和"""
    result = a + b
    return result   # 返回结果

# 接收返回值
total = add(3, 5)
print(total)   # 输出：8
```

```
📝 return 的作用：
   ① 把结果"递出去"
   ② 结束函数的执行
   ③ 返回值可以赋值给变量

🔑 关键理解：
   return ≠ print
   print → 在屏幕上显示（说给你听）
   return → 把结果交给你（装进盒子）
```

---

## 第16页：return vs print

```python
def with_return():
    return 42

def with_print():
    print(42)

# 调用两个函数
a = with_return()
b = with_print()

print(f"a = {a}")   # a = 42
print(f"b = {b}")   # b = None
```

```
📤 运行结果：
42          ← with_print() 打印的
a = 42      ← return 的值赋给了 a
b = None    ← print 没有返回值，b 是 None

⚠️ 记住：
   return 的值可以存起来再用
   print 的值"说完就没了"
```

---

## 第17页：无返回值的函数

```python
def show_message(name):
    """只显示信息，不返回结果"""
    print(f"欢迎 {name} 来到电商直播间！")

result = show_message("小明")
print(f"返回值是：{result}")
```

```
📤 运行结果：
欢迎 小明 来到电商直播间！
返回值是：None

📝 说明：
   · 没有 return 语句的函数
   · 默认返回 None
   · None 表示"什么都没有"
   · 适合只需要执行操作、不需要返回结果的场景
```

---

## 第18页：电商场景 —— 带返回值的函数

```python
# 浙江电商场景：订单金额计算
def calc_order(items):
    """计算订单总金额"""
    total = 0
    for item in items:
        total += item
    return total

# 调用函数
cart = [15.5, 25.0, 89.0]  # 购物车商品单价
total = calc_order(cart)
print(f"订单总额：{total:.2f}元")
# 输出：订单总额：129.50元
```

```
💡 思考：
   如果把 return 改成 print，
   还能用 total 继续计算折扣吗？
   → 不能！因为 print 不返回值！
```

---

## 第19页：折扣计算函数

```python
def apply_discount(price, rate=0.9):
    """应用折扣，返回折后价"""
    final = price * rate
    return final

# 调用
original = 129.50
# 双十一 85 折
final_price = apply_discount(original, 0.85)
print(f"原价：{original:.2f}元")
print(f"折后：{final_price:.2f}元")
print(f"节省：{original - final_price:.2f}元")
```

```
📤 运行结果：
原价：129.50元
折后：110.08元
节省：19.43元
```

---

## 第20页：综合演示 —— 电商促销计算器

```python
# ============================
# 电商促销计算器（完整示例）
# ============================

def calc_item_price(name, price, quantity=1):
    """计算单个商品总价"""
    total = price * quantity
    print(f"📦 {name} × {quantity} = {total:.2f}元")
    return total

def apply_discount(total, rate=0.9):
    """应用折扣"""
    return total * rate

def show_receipt(customer, items_total, final_price):
    """显示结算单"""
    print(f"\n🧾 结算单")
    print(f"👤 顾客：{customer}")
    print(f"💰 商品总额：{items_total:.2f}元")
    print(f"💰 实付金额：{final_price:.2f}元")
    print("=" * 25)

# 主程序
customer = "小明同学"
item1 = calc_item_price("手机壳", 15.5, 2)
item2 = calc_item_price("数据线", 25.0, 1)
items_total = item1 + item2
final = apply_discount(items_total, 0.85)
show_receipt(customer, items_total, final)
```

---

## 第21页：综合演示 —— 运行结果

```
📦 手机壳 × 2 = 31.00元
📦 数据线 × 1 = 25.00元

🧾 结算单
👤 顾客：小明同学
💰 商品总额：56.00元
💰 实付金额：47.60元
=========================
```

```
🎯 这个程序用了几个函数？
   · calc_item_price()  → 计算商品价
   · apply_discount()   → 计算折扣
   · show_receipt()     → 显示结算单

🎯 体现了什么编程思想？
   · 模块化：每个函数做一件事
   · 可复用：函数可以被多次调用
   · 易维护：修改某个功能只需改对应函数
```

---

## 第22页：常见错误（一）—— 语法错误

```python
# ❌ 错误1：忘记冒号
def greet()
    print("Hello!")

# ✅ 正确
def greet():
    print("Hello!")


# ❌ 错误2：缩进不对
def greet():
print("Hello!")    # ← 没有缩进！

# ✅ 正确
def greet():
    print("Hello!")  # ← 缩进4个空格
```

```
🔍 Python 3.12+ 的错误提示更友好了！

旧版本：
  SyntaxError: invalid syntax

Python 3.12+：
  SyntaxError: expected ':'
  def greet()
             ^
  💡 直接告诉你缺了什么！
```

---

## 第23页：常见错误（二）—— 调用错误

```python
# ❌ 错误3：函数名拼写错误
def say_hello():
    print("Hello!")

say_helo()   # ← 拼错了！

# 🔧 解决：仔细检查函数名


# ❌ 错误4：参数数量不匹配
def make_tea(name, sweetness):
    print(f"{sweetness}的{name}")

make_tea("奶茶")   # ← 少传了一个参数！

# 🔧 解决：检查参数数量，或使用默认参数
```

```
🐛 调试技巧：
   ① 看错误信息（Python会告诉你哪一行错了）
   ② 逐行检查（从报错行往上找）
   ③ 用 print 查看中间结果
   ④ 把大问题拆成小步骤测试
```

---

## 第24页：常见错误（三）—— 逻辑错误

```python
# ❌ 错误5：忘记 return
def add(a, b):
    result = a + b
    # ← 忘了写 return！

total = add(3, 5)
print(total)   # 输出：None（不是8！）

# ✅ 正确
def add(a, b):
    result = a + b
    return result


# ❌ 错误6：return 放错位置
def max_num(a, b):
    if a > b:
        return a
    return b   # ← 这个位置才对

# 如果写成：
def max_num(a, b):
    return a   # ← 永远返回a，if白写了！
    if a > b:
        ...
```

---

## 第25页：Python 3.12+ 新特性

```
🆕 Python 3.12+ 函数相关新特性：

1. 更好的错误提示
   · 语法错误会精确指出位置
   · 用 ^ 标记出错的地方
   · 对初学者更友好！

2. 类型提示改进（Type Hints）
   def calc_price(name: str, price: float, qty: int = 1) -> float:
       """类型提示让代码更清晰"""
       return price * qty

3. f-string 中的 = 符号（调试利器）
   x = 42
   print(f"{x=}")   # 输出：x=42
   # 不用写 print("x =", x) 了！

💡 这些特性让写函数更简单、调试更容易！
```

---

## 第26页：实践任务

```
🎯 上机实践任务

📌 基础任务（必做）：
   定义一个 greet(name) 函数，
   接收用户名，打印欢迎信息。

📌 进阶任务（必做）：
   定义一个 calc_discount(price, rate) 函数，
   接收原价和折扣率，返回折后价。

📌 挑战任务（选做）：
   定义一个 generate_receipt(customer, items, rate) 函数，
   接收顾客名、商品列表和折扣率，
   生成完整的结算单。

⏰ 时间：10分钟
🤝 可以同桌讨论，但代码要自己写
```

---

## 第27页：课堂小结

```
📋 今天学了什么？

1️⃣ 函数是什么？
   可重复使用的代码块 = 代码配方

2️⃣ 怎么定义函数？
   def 函数名(参数):
       函数体
       return 返回值

3️⃣ 三种参数
   位置参数 → 按顺序
   默认参数 → 有默认值
   关键字参数 → 按名字

4️⃣ 返回值
   return → 返回结果
   无return → 返回None

5️⃣ 常见错误
   冒号、缩进、参数匹配、return
```

---

## 第28页：课后作业

```
📝 课后作业

🔹 基础题：
   编写一个函数 is_even(n)，
   判断一个数是否为偶数，返回 True/False。

🔹 提高题：
   编写一个函数 calc_shipping(weight, distance)，
   根据重量和距离计算运费：
   · 1kg以内 8元
   · 超过1kg，每kg加3元
   · 超过100km，额外加5元

🔹 拓展题：
   编写一个简易计算器，包含四个函数：
   add(a,b)、subtract(a,b)、multiply(a,b)、divide(a,b)

💡 下节课预告：函数的嵌套调用与作用域
```

---

*PPT大纲编写：沈卫星 | 日期：2026年4月*

---
name: dingtalk-case-export
description: 钉钉聊天记录导出为教学案例技能。支持按主题模块整理对话、自动生成案例文档、打包附件。使用场景：教师与 AI 助手的钉钉对话需要整理成教学案例时自动触发，包括：(1) 对话结束后整理归档，(2) 按主题模块分割对话，(3) 生成 Word 格式案例文档，(4) 打包输入图片和产出文件，(5) 建立可复用的教学案例库。
---

# 钉钉聊天记录导出为教学案例

## 技能概述

本技能用于将教师与 AI 助手的钉钉聊天记录整理成结构化教学案例，包括对话记录、主题分析、产出物归档和附件打包。

## 核心功能

1. **对话记录整理** - 按时间顺序整理完整对话
2. **主题模块分割** - 识别对话中的主题模块（如模块 1：创意激发、模块 2：概念澄清等）
3. **案例文档生成** - 自动生成 Word 格式案例文档（含教学分析、技巧提炼、反思讨论）
4. **附件打包归档** - 整理输入图片和产出文件，统一命名和归档
5. **案例库管理** - 建立可检索的案例库结构

## 工作流程

### 步骤 1：触发条件

当满足以下条件时触发本技能：

- 用户明确要求"整理钉钉聊天记录成教学案例"
- 对话结束且产生多个产出物
- 用户提到"案例"、"导出"、"记录整理"等关键词

### 步骤 2：收集对话内容

从当前会话历史中提取：

1. 完整对话记录（包括时间戳、发送者）
2. 所有输入图片（保存路径）
3. 所有产出文件（文档、PPT、压缩包等）

### 步骤 3：识别主题模块

分析对话内容，识别主题模块：

```
模块识别规则：
- 话题明显转换 → 新模块开始
- 用户提出新任务 → 新模块开始
- AI 生成长内容 → 独立模块
```

示例模块结构：

| 模块 | 主题 | 教学价值 |
|------|------|---------|
| 模块 1 | 樱花照片分享与古诗创作 | AI 创意生成能力展示 |
| 模块 2 | 魔戒魔法学院→小龙虾比喻 | AI 概念澄清与比喻构建 |
| 模块 3 | 小龙虾培养机制设计 | 人机协作理念阐述 |
| 模块 4 | 双向成长模型 | 共生关系深度讨论 |
| 模块 5 | 11 周教学方案设计 | 完整教学设计协作案例 |

### 步骤 4：生成案例文档

使用 `templates/case_template.md` 模板，填充以下内容：

1. **案例基本信息** - 编号、日期、参与方
2. **案例背景** - 课程信息、教学目标
3. **对话记录（按模块）** - 每个模块的完整对话 + 教学分析
4. **关键技巧提炼** - 提问技巧、追问分析、验证方法
5. **产出物展示** - 文件清单、附件列表
6. **反思与讨论** - 使用心得、学生讨论题
7. **附录** - 完整对话记录、附件清单

### 步骤 5：整理附件（关键：相对路径）

执行 `scripts/organize_attachments.py` 脚本：

```bash
python3 scripts/organize_attachments.py \
  --case-number 001 \
  --case-name "人机协作设计数字人文课程" \
  --input-images /path/to/images/ \
  --output-files /path/to/outputs/ \
  --output-dir /home/admin/.openclaw/workspace/teaching_cases/001_案例名称/
```

**核心原则：所有文件路径必须是相对路径！**

脚本功能：

- 清理不相关图片
- 重命名文件（格式：`模块 X_描述_序号。扩展名`）
- 建立标准文件夹结构
- 生成附件清单
- **将绝对路径转换为相对路径**（如 `./02_产出物/file.docx`）
- **确保所有文件在同一目录树内**（避免跨目录链接）

### 步骤 6：转换文档格式

使用 Pandoc 将 Markdown 转换为 Word：

```bash
pandoc -f markdown -t docx -o "01_案例文档.docx" "01_案例文档.md"
pandoc -f markdown -t docx -o "04_对话记录_完整版.docx" "04_对话记录_完整版.md"
```

### 步骤 7：打包案例包

执行打包脚本：

```bash
cd /home/admin/.openclaw/workspace/teaching_cases/
zip -r 001_案例名称.zip 001_案例名称/
```

### 步骤 8：发送给用户

使用 `message` 工具发送案例包：

```python
message(action="send", filePath="/path/to/001_案例名称.zip", target="用户 ID")
```

## 案例库结构

```
teaching_cases/
├── 001_人机协作设计数字人文课程/
│   ├── 01_案例文档.docx              ← 主文档（所有链接使用相对路径）
│   ├── 01_案例文档.md                ← Markdown 源码
│   ├── 02_产出物/                    ← 所有产出文件放在此目录
│   │   ├── digital_humanities_11weeks.docx
│   │   └── week5_package_word.zip
│   ├── 03_输入材料/                  ← 所有输入图片放在此目录
│   │   ├── 模块 1_樱花照片_1.jpg
│   │   ├── 模块 1_樱花照片_2.jpg
│   │   └── 模块 5_案例文档预览截图.png
│   ├── 04_对话记录_完整版.docx
│   └── 04_对话记录_完整版.md
├── 002_案例名称/
└── ...
```

**路径规则：**

| 文档位置 | 引用产出物 | 相对路径写法 |
|----------|-----------|-------------|
| `01_案例文档.md` | 同目录文件 | `./02_产出物/file.docx` |
| `01_案例文档.md` | 输入材料 | `./03_输入材料/模块 1_樱花照片_1.jpg` |
| `04_对话记录_完整版.md` | 产出物 | `./02_产出物/file.docx` |

**❌ 错误示例（绝对路径）：**
```markdown
![截图](/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/03_输入材料/模块 1_樱花照片_1.jpg)
```

**✅ 正确示例（相对路径）：**
```markdown
![截图](./03_输入材料/模块 1_樱花照片_1.jpg)
```

## 文件命名规范

### 输入材料

```
模块 X_描述_序号。扩展名

示例：
- 模块 1_樱花照片_1.jpg
- 模块 1_樱花照片_2.jpg
- 模块 5_案例文档预览截图.png
```

### 输出文档

```
序号_文档类型。扩展名

示例：
- 01_案例文档.docx
- 04_对话记录_完整版.docx
```

### 产出物

```
描述性名称。扩展名

示例：
- digital_humanities_11weeks.docx
- week5_package_word.zip
```

---

## 📁 文件路径处理规范（重要！）

### 核心原则

1. **所有路径必须是相对路径** - 从案例文档所在目录开始计算
2. **所有文件必须在案例目录内** - 不允许引用外部文件
3. **打包后链接必须有效** - ZIP 解压后所有链接仍可访问

### 路径转换规则

| 原始路径（虚拟机绝对路径） | 转换后（相对路径） |
|--------------------------|------------------|
| `/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/02_产出物/file.docx` | `./02_产出物/file.docx` |
| `/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/03_输入材料/模块 1_樱花照片_1.jpg` | `./03_输入材料/模块 1_樱花照片_1.jpg` |
| `/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/01_案例文档.docx` | `./01_案例文档.docx` |

### Markdown 链接处理

在生成 `01_案例文档.md` 时：

```markdown
<!-- ❌ 错误：绝对路径 -->
![樱花照片](/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/03_输入材料/模块 1_樱花照片_1.jpg)

<!-- ✅ 正确：相对路径 -->
![樱花照片](./03_输入材料/模块 1_樱花照片_1.jpg)

<!-- ❌ 错误：引用外部文件 -->
[下载文件](/tmp/outputs/digital_humanities_11weeks.docx)

<!-- ✅ 正确：引用案例目录内文件 -->
[下载文件](./02_产出物/digital_humanities_11weeks.docx)
```

### Word 文档处理

使用 Pandoc 转换时，确保 Markdown 中的相对路径在 Word 中保持有效：

```bash
# 在案例目录内执行转换，确保路径基准正确
cd /home/admin/.openclaw/workspace/teaching_cases/001_案例名称/
pandoc -f markdown -t docx -o "01_案例文档.docx" "01_案例文档.md"
```

### HTML 网页处理（如生成网页版案例）

```html
<!-- ❌ 错误：绝对路径 -->
<img src="/home/admin/.openclaw/workspace/teaching_cases/001_案例名称/03_输入材料/模块 1_樱花照片_1.jpg">

<!-- ✅ 正确：相对路径 -->
<img src="./03_输入材料/模块 1_樱花照片_1.jpg">
```

### 脚本实现要点

在 `organize_attachments.py` 中添加路径转换函数：

```python
def convert_to_relative_path(abs_path, case_dir):
    """将绝对路径转换为相对于案例目录的路径"""
    # 确保文件已复制到案例目录内
    if not abs_path.startswith(case_dir):
        # 复制文件到案例目录
        dest_path = os.path.join(case_dir, '03_输入材料', os.path.basename(abs_path))
        shutil.copy2(abs_path, dest_path)
        abs_path = dest_path
    
    # 转换为相对路径
    rel_path = os.path.relpath(abs_path, case_dir)
    return f"./{rel_path}"
```

---

## 质量检查清单（路径专项）

在发送案例包前，**额外检查以下路径相关项目**：

- [ ] 所有 Markdown 链接使用相对路径（无 `/home/` 等绝对路径）
- [ ] 所有图片引用在案例目录内（无外部引用）
- [ ] 所有产出物已复制到 `02_产出物/` 目录
- [ ] 所有输入图片已复制到 `03_输入材料/` 目录
- [ ] 在案例目录内执行 `grep -r "/home/admin"` 无匹配结果
- [ ] 打包 ZIP 后，解压到新位置，所有链接仍可访问
- [ ] Word 文档中的超链接和图片引用有效

## 案例编号规则

```
DH-LLM-YYYY-NNN

DH: Digital Humanities（数字人文）
LLM: Large Language Model
YYYY: 年份
NNN: 序号（001, 002, ...）
```

示例：`DH-LLM-2026-001`

## 教学分析模板

每个模块的教学分析包含：

```markdown
### 📌 教学分析

| 维度 | 分析 |
|------|------|
| AI 能力展示 | [描述 AI 展示的能力] |
| 提问技巧 | [分析用户提问技巧] |
| 输出质量 | [评估 AI 输出质量] |
| 教学价值 | [说明教学价值] |

### 💡 关键技巧

- [技巧 1]
- [技巧 2]

### ⚠️ 验证点

- [需要验证的知识点]
```

## 学生讨论题模板

```markdown
### 学生讨论题

1. **提问分析**：案例中哪些提问是有效的？为什么？
2. **改进建议**：如果让你重新提问，你会怎么改进？
3. **验证思考**：AI 的回答有哪些需要验证的地方？如何验证？
4. **模式讨论**：这个案例展示了什么样的人机协作模式？你认同吗？
5. **应用迁移**：你能将这种协作模式应用到你的专业学习中吗？
```

## 自动化脚本

### organize_attachments.py

功能：整理和重命名附件（**包含路径转换**）

输入：
- 案例编号
- 案例名称
- 输入图片路径（可能是绝对路径）
- 产出文件路径（可能是绝对路径）

输出：
- 标准化的文件夹结构
- 重命名后的文件
- 附件清单 JSON
- **路径映射表**（绝对路径 → 相对路径）

**关键函数：**

```python
def organize_and_convert_paths(case_dir, input_images, output_files):
    """
    1. 复制所有文件到案例目录内
    2. 重命名文件
    3. 生成相对路径映射
    4. 返回路径映射表供文档生成使用
    """
    path_mapping = {}
    
    # 处理输入图片
    for i, img_path in enumerate(input_images):
        # 复制到案例目录
        dest_dir = os.path.join(case_dir, '03_输入材料')
        dest_path = os.path.join(dest_dir, f'模块{module}_图片_{i+1}.jpg')
        shutil.copy2(img_path, dest_path)
        
        # 记录路径映射
        rel_path = os.path.relpath(dest_path, case_dir)
        path_mapping[img_path] = f"./{rel_path}"
    
    # 处理产出文件
    for file_path in output_files:
        dest_dir = os.path.join(case_dir, '02_产出物')
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        shutil.copy2(file_path, dest_path)
        
        rel_path = os.path.relpath(dest_path, case_dir)
        path_mapping[file_path] = f"./{rel_path}"
    
    return path_mapping
```

### generate_case_doc.py

功能：自动生成案例文档（**使用相对路径**）

输入：
- 对话记录 JSON
- 主题模块分析
- 产出物清单
- **路径映射表**（从 organize_attachments.py 获取）

输出：
- Markdown 格式案例文档（所有链接为相对路径）
- 教学分析建议

**关键处理：**

```python
def replace_paths_in_content(content, path_mapping):
    """将文档中的绝对路径替换为相对路径"""
    for abs_path, rel_path in path_mapping.items():
        # 替换 Markdown 图片链接
        content = content.replace(f']({abs_path})', f']({rel_path})')
        # 替换 Markdown 文件链接
        content = content.replace(f'[{abs_path}]({abs_path})', f'[{os.path.basename(abs_path)}]({rel_path})')
        # 替换 HTML 标签中的路径
        content = content.replace(f'src="{abs_path}"', f'src="{rel_path}"')
        content = content.replace(f'href="{abs_path}"', f'href="{rel_path}"')
    
    return content
```

## 质量检查清单

在发送案例包前，检查以下项目：

- [ ] 案例文档格式正确（Word 可打开）
- [ ] 图片已按模块命名
- [ ] 删除了不相关的图片
- [ ] 产出物完整（所有生成的文件）
- [ ] 压缩包可正常解压
- [ ] 案例编号唯一且连续
- [ ] 对话记录完整无遗漏

## 使用示例

### 示例 1：课后即时整理

**用户输入：**
> 把今天的对话整理成教学案例

**技能响应：**
1. 提取当前会话历史
2. 识别 7 个主题模块
3. 复制所有文件到案例目录（`001_人机协作设计数字人文课程/`）
4. 生成路径映射表（绝对路径 → 相对路径）
5. 生成案例文档（**所有链接使用相对路径**）
6. 整理附件（2 张樱花照片 + 产出文件）
7. 打包发送 `001_人机协作设计数字人文课程.zip`

**验证步骤：**
```bash
# 解压后检查
unzip 001_人机协作设计数字人文课程.zip -d /tmp/test/
cd /tmp/test/001_人机协作设计数字人文课程/

# 检查文档中无绝对路径
grep -r "/home/admin" .  # 应该无输出

# 检查相对路径链接
grep -r "\./02_产出物/" 01_案例文档.md  # 应该有匹配
grep -r "\./03_输入材料/" 01_案例文档.md  # 应该有匹配
```

### 示例 2：批量整理

**用户输入：**
> 把上周的 3 次对话都整理成案例

**技能响应：**
1. 查询上周会话历史
2. 分别生成 3 个案例
3. 编号为 002、003、004
4. 每个案例独立处理文件路径
5. 逐个打包发送

---

## 🧪 路径有效性测试流程

在发送案例包前，执行以下测试：

```bash
#!/bin/bash
# test_case_paths.sh

CASE_DIR="/home/admin/.openclaw/workspace/teaching_cases/001_案例名称"
TEST_DIR="/tmp/case_path_test_$$"

echo "=== 测试案例包路径有效性 ==="

# 1. 打包
cd $(dirname $CASE_DIR)
zip -r $(basename $CASE_DIR).zip $(basename $CASE_DIR)

# 2. 解压到新位置
mkdir -p $TEST_DIR
unzip $(basename $CASE_DIR).zip -d $TEST_DIR

# 3. 检查绝对路径
echo "检查绝对路径..."
if grep -r "/home/admin" $TEST_DIR/$(basename $CASE_DIR)/ 2>/dev/null; then
    echo "❌ 发现绝对路径！需要修复"
    exit 1
else
    echo "✅ 无绝对路径"
fi

# 4. 检查相对路径链接
echo "检查相对路径链接..."
if grep -r "\./02_产出物/" $TEST_DIR/$(basename $CASE_DIR)/01_案例文档.md 2>/dev/null; then
    echo "✅ 相对路径链接存在"
else
    echo "⚠️ 未找到相对路径链接（可能是纯文本案例）"
fi

# 5. 清理
rm -rf $TEST_DIR $(basename $CASE_DIR).zip

echo "=== 测试完成 ==="
```

## 注意事项

1. **隐私保护** - 隐去个人敏感信息（如手机号、账号 ID）
2. **使用授权** - 确保对话双方同意用于教学
3. **内部使用** - 建议仅限课程内部使用
4. **存储管理** - 定期清理过大的图片文件
5. **版本控制** - 案例文档修改后更新版本号

## 相关文件

- `templates/case_template.md` - 案例文档模板
- `scripts/organize_attachments.py` - 附件整理脚本
- `scripts/generate_case_doc.py` - 案例文档生成脚本
- `examples/case_001_sample/` - 案例 001 示例

## 迭代记录

### v1.0 (2026-03-30)
- 初始版本
- 支持单次对话整理
- 基础模板和脚本
- 案例 001 验证通过

### 待开发功能
- [ ] 批量整理支持
- [ ] 自动主题识别优化
- [ ] 案例检索功能
- [ ] 在线案例库展示

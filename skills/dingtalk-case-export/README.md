# 钉钉聊天记录导出技能 - 发布说明

## 技能信息

- **技能名称**: dingtalk-case-export
- **技能版本**: v1.0
- **创建日期**: 2026 年 3 月 30 日
- **技能文件**: `dingtalk-case-export.skill`

## 功能概述

本技能用于将教师与 AI 助手的钉钉聊天记录整理成结构化教学案例，包括：

1. ✅ 对话记录整理（按时间顺序）
2. ✅ 主题模块分割（自动识别话题转换）
3. ✅ 案例文档生成（Word 格式，含教学分析）
4. ✅ 附件打包归档（输入图片 + 产出文件）
5. ✅ 案例库管理（标准化命名和结构）

## 使用场景

当用户提到以下关键词时自动触发：

- "整理钉钉聊天记录成教学案例"
- "把对话导出为案例"
- "生成教学案例文档"
- "打包聊天记录和附件"

## 安装方法

### 方法 1：手动安装

```bash
# 复制技能文件到 OpenClaw 技能目录
cp dingtalk-case-export.skill ~/.openclaw/skills/

# 解压技能包
cd ~/.openclaw/skills/
unzip dingtalk-case-export.skill
```

### 方法 2：使用 clawhub（推荐）

```bash
# 发布到 clawhub
clawhub publish dingtalk-case-export/

# 安装技能
clawhub install dingtalk-case-export
```

## 使用示例

### 示例 1：课后即时整理

**用户输入**:
> 把今天的对话整理成教学案例

**技能响应**:
1. 提取当前会话历史
2. 识别主题模块（如 7 个模块）
3. 生成案例文档（Word 格式）
4. 整理附件（图片重命名 + 归档）
5. 打包发送 `001_人机协作设计数字人文课程.zip`

### 示例 2：指定案例名称

**用户输入**:
> 把这次对话整理成案例，案例名称为"AI 辅助课程设计"

**技能响应**:
- 使用指定名称生成案例包
- 编号自动递增

## 输出结构

生成的案例包结构：

```
001_案例名称.zip
├── 01_案例文档.docx          (主案例文档)
├── 01_案例文档.md            (Markdown 源文件)
├── 04_对话记录_完整版.docx    (完整对话)
├── 04_对话记录_完整版.md      (对话记录源文件)
├── 02_产出物/
│   ├── 产出文件 1.docx
│   └── 产出文件 2.zip
└── 03_输入材料/
    ├── 模块 1_描述_1.jpg
    ├── 模块 1_描述_2.jpg
    └── 模块 X_截图.png
```

## 文件命名规范

### 输入材料
```
模块 X_描述_序号。扩展名

示例：
- 模块 1_樱花照片_1.jpg
- 模块 5_案例文档预览截图.png
```

### 输出文档
```
序号_文档类型。扩展名

示例：
- 01_案例文档.docx
- 04_对话记录_完整版.docx
```

## 案例编号规则

```
DH-LLM-YYYY-NNN

DH: Digital Humanities（数字人文）
LLM: Large Language Model
YYYY: 年份
NNN: 序号（001, 002, ...）
```

## 依赖工具

- Python 3.7+
- Pandoc（用于 Markdown → Word 转换）
- Zip 工具（用于打包）

## 配置说明

### 环境变量（可选）

```bash
# 案例库根目录
export TEACHING_CASES_DIR="/home/admin/.openclaw/workspace/teaching_cases"

# 默认案例前缀
export CASE_PREFIX="DH"
```

### 配置文件

创建 `~/.openclaw/skills/dingtalk-case-export/config.json`:

```json
{
  "default_output_dir": "/home/admin/.openclaw/workspace/teaching_cases",
  "auto_compress": true,
  "include_preview_screenshot": true,
  "max_image_size_mb": 5
}
```

## 质量检查清单

使用技能后，检查以下项目：

- [ ] 案例文档格式正确（Word 可打开）
- [ ] 图片已按模块命名
- [ ] 删除了不相关的图片
- [ ] 产出物完整（所有生成的文件）
- [ ] 压缩包可正常解压
- [ ] 案例编号唯一且连续

## 故障排除

### 问题 1：Pandoc 未安装

**错误信息**:
```
pandoc: command not found
```

**解决方法**:
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# CentOS/RHEL
sudo yum install pandoc
```

### 问题 2：权限不足

**错误信息**:
```
Permission denied: /path/to/output
```

**解决方法**:
```bash
# 确保输出目录可写
chmod -R u+w /home/admin/.openclaw/workspace/teaching_cases
```

### 问题 3：图片文件丢失

**错误信息**:
```
FileNotFoundError: /path/to/image.jpg
```

**解决方法**:
- 检查图片路径是否正确
- 确保图片在钉钉中已下载
- 使用绝对路径

## 版本历史

### v1.0 (2026-03-30)
- ✅ 初始版本发布
- ✅ 支持单次对话整理
- ✅ 基础模板和脚本
- ✅ 案例 001 验证通过

### 待开发功能
- [ ] 批量整理支持
- [ ] 自动主题识别优化（AI 辅助）
- [ ] 案例检索功能
- [ ] 在线案例库展示
- [ ] 支持导出为 PDF

## 贡献者

- **开发者**: AI 助手（小龙虾）
- **测试者**: 诸葛斌
- **案例来源**: 浙江工商大学数字人文课程

## 使用许可

- **许可类型**: 教育用途
- **使用范围**: 仅限课程内部教学使用
- **禁止事项**: 商业用途、二次分发

## 联系方式

如有问题或建议，请通过以下方式联系：

- **钉钉**: 诸葛斌
- **邮箱**: [待填写]
- **GitHub**: [待填写]

---

**最后更新**: 2026 年 3 月 30 日

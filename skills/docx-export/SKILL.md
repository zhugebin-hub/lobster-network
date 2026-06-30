# docx-export Skill

将 Markdown、文本等内容转换为 Word 文档 (.docx) 格式。使用 pandoc 进行高质量格式转换，支持标题、列表、表格、图片等元素。

## 触发场景

用户说"生成 Word"、"导出 docx"、"创建文档"、"转成 Word"、"要 word 版本"等。

## 使用方法

```bash
pandoc input.md -o output.docx
```

## 注意事项

- 确保 pandoc 已安装
- 图片需要是相对路径或绝对路径
- 支持中文编码

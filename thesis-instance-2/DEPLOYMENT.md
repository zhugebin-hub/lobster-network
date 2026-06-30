# 部署指南

## 模板文件部署说明

系统中的模板文件通过本地存储目录 `/files/templates/` 路由提供下载，部署时需要将模板文件复制到生产环境的存储目录中。

### 模板文件清单

| 文件名 | 用途 | 使用位置 |
|--------|------|----------|
| 人工智能本科生耗材申请.docx | 学生毕设采购申请模板 | 学生控制台 > 毕设采购申请 |
| 批量导入.xlsx | 管理员批量导入学生/导师模板 | 管理员控制台 > 批量导入 |
| 导师课题导入.xlsx | 导师批量导入课题模板 | 导师控制台 > 课题管理 > 批量导入 |

### 部署步骤

1. 在生产服务器上创建存储目录（如果使用 `LOCAL_STORAGE_DIR` 环境变量自定义路径）：

```bash
# 默认路径为项目根目录下的 ./local-storage
# 可通过 LOCAL_STORAGE_DIR 环境变量自定义，例如：
export LOCAL_STORAGE_DIR=/data/thesis-files

# 创建 templates 子目录
mkdir -p $LOCAL_STORAGE_DIR/templates
```

2. 将模板文件复制到 templates 目录：

```bash
cp 人工智能本科生耗材申请.docx $LOCAL_STORAGE_DIR/templates/
cp 批量导入.xlsx $LOCAL_STORAGE_DIR/templates/
cp 导师课题导入.xlsx $LOCAL_STORAGE_DIR/templates/
```

3. 确认文件权限正确（Web 服务进程需要读取权限）：

```bash
chmod 644 $LOCAL_STORAGE_DIR/templates/*
```

### 注意事项

- 服务启动时会自动创建 `templates` 目录（通过 `ensureTemplatesDir()` 函数），但不会自动复制模板文件。
- 模板文件通过 Express 静态路由 `/files/` 提供访问，前端通过 `/files/templates/文件名` 路径下载。
- 如果需要更新模板文件，直接替换存储目录中的文件即可，无需重启服务。
- 所有模板文件均不依赖外部 CDN，完全本地化托管。

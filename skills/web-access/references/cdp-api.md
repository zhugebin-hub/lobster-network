# CDP Proxy API Reference

## 健康检查

```bash
curl -s http://localhost:3456/health
# 返回：{"status":"ok","connected":true,"sessions":0,"chromePort":9222}
```

## Tab 管理

### 列出所有 tab
```bash
curl -s http://localhost:3456/targets
```

### 创建新后台 tab
```bash
curl -s "http://localhost:3456/new?url=https://example.com"
# 返回：{"targetId":"ABC123..."}
```

### 关闭 tab
```bash
curl -s "http://localhost:3456/close?target=ABC123..."
```

### 导航到新 URL
```bash
curl -s "http://localhost:3456/navigate?target=ABC123...&url=https://example.com"
```

### 后退
```bash
curl -s "http://localhost:3456/back?target=ABC123..."
```

## 页面信息

### 获取页面信息（标题、URL、状态）
```bash
curl -s "http://localhost:3456/info?target=ABC123..."
# 返回：{"title":"Example","url":"https://example.com","ready":"complete"}
```

## JavaScript 执行

### 执行任意 JS
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d 'document.title'
# 返回：{"value":"Example Domain"}
```

### 提取页面文本
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d 'document.body.innerText'
```

### 提取所有链接
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  Array.from(document.querySelectorAll("a")).map(a => ({
    text: a.textContent.trim(),
    href: a.href
  })).filter(x => x.text && x.href)
'
```

### 查找元素
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  const el = document.querySelector("button.submit");
  el ? { found: true, text: el.textContent } : { found: false }
'
```

## 交互操作

### 点击元素（JS click）
```bash
curl -s -X POST "http://localhost:3456/click?target=ABC123..." -d 'button.submit'
```

### 真实鼠标点击（触发文件对话框等）
```bash
curl -s -X POST "http://localhost:3456/clickAt?target=ABC123..." -d '.upload-btn'
```

### 文件上传
```bash
curl -s -X POST "http://localhost:3456/setFiles?target=ABC123..." \
  -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'
```

### 滚动页面
```bash
# 滚动到底部（触发懒加载）
curl -s "http://localhost:3456/scroll?target=ABC123...&direction=bottom"

# 向下滚动 3000px
curl -s "http://localhost:3456/scroll?target=ABC123...&y=3000"

# 滚动到顶部
curl -s "http://localhost:3456/scroll?target=ABC123...&direction=top"
```

## 截图

### 截图保存
```bash
curl -s "http://localhost:3456/screenshot?target=ABC123...&file=/tmp/shot.png"
```

### 截图返回图片数据
```bash
curl -s "http://localhost:3456/screenshot?target=ABC123..." > shot.png
```

### 视频帧捕获
```bash
# 先 seek 到指定时间点
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  const video = document.querySelector("video");
  video.currentTime = 30; // 30 秒
'

# 然后截图
curl -s "http://localhost:3456/screenshot?target=ABC123...&file=/tmp/frame30s.png"
```

## 高级 JS 模式

### 等待元素出现
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  new Promise(resolve => {
    const el = document.querySelector(".target");
    if (el) return resolve({ found: true });
    const observer = new MutationObserver(() => {
      if (document.querySelector(".target")) {
        observer.disconnect();
        resolve({ found: true });
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => { observer.disconnect(); resolve({ found: false }); }, 5000);
  })
'
```

### 提取图片 URL
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  Array.from(document.querySelectorAll("img")).map(img => ({
    src: img.src,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight
  })).filter(x => x.src && x.width > 100)
'
```

### 提取视频信息
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  const video = document.querySelector("video");
  if (!video) return { found: false };
  return {
    found: true,
    duration: video.duration,
    currentTime: video.currentTime,
    paused: video.paused,
    src: video.src || video.querySelector("source")?.src
  };
'
```

### 填充表单
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  document.querySelector("#email").value = "test@example.com";
  document.querySelector("#password").value = "secret123";
  { filled: true }
'
```

### 提交表单
```bash
curl -s -X POST "http://localhost:3456/eval?target=ABC123..." -d '
  document.querySelector("form").submit();
  { submitted: true }
'
```

## 错误处理

- **WebSocket 未连接**：确保 Chrome 已开启远程调试
- **targetId 无效**：tab 可能已关闭，重新创建
- **元素未找到**：检查选择器，或页面尚未加载完成
- **超时**：页面加载慢，增加等待时间或检查网络

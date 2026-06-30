# 物联网网络层技术 PPT

## 文件说明

- **主文件**: `iot-network-ppt.html`
- **总页数**: 120+ 页
- **内容**: 完整的物联网网络层技术教程

## 三大部分

### 第一部分：互联网发展历史与网络基础 (50 页)
- 互联网发展历程
- OSI 七层模型详解
- TCP/IP 协议栈
- 网络层核心概念（路由、寻址、转发）

### 第二部分：无线局域网技术 (20 页)
- LoRa 技术（广域 IoT）
- WiFi 系列演进（WiFi 4/5/6/7）
- Zigbee 协议（智能家居）

### 第三部分：6G 网络前沿 (50 页)
- 6G 愿景与需求
- 关键使能技术（太赫兹、RIS、AI 原生）
- 空天地海一体化
- 挑战与展望

## 使用方法

### 方式 1：直接打开
双击 `iot-network-ppt.html` 文件，用浏览器打开

### 方式 2：本地服务器（推荐）
```bash
cd /path/to/ppt-output
python3 -m http.server 8000
```
然后访问：http://localhost:8000/iot-network-ppt.html

### 方式 3：VS Code Live Server
1. 在 VS Code 中打开此文件夹
2. 安装 Live Server 插件
3. 右键 HTML 文件 → "Open with Live Server"

## 修复记录

**2026-04-18**: 修复 CSS 样式加载问题
- 恢复 Reveal.js CSS 链接
- 优化页面布局为文档滚动模式
- 禁用幻灯片导航控制

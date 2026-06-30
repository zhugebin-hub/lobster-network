#!/usr/bin/env node

/**
 * 🦞 钉钉文件位置通知脚本
 * 
 * 功能：监听钉钉媒体文件夹，当新文件到达时自动通知用户
 * 使用：作为 OpenClaw 的后台钩子或独立脚本运行
 */

const fs = require('fs');
const path = require('path');

// 配置
const MEDIA_DIR = '/home/admin/.openclaw/media/inbound';
const STATE_FILE = '/home/admin/.openclaw/workspace/memory/file-notify-state.json';
const CHECK_INTERVAL_MS = 2000; // 每 2 秒检查一次

// 加载已通知的文件记录
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('加载状态文件失败:', e.message);
  }
  return { notifiedFiles: [] };
}

// 保存状态
function saveState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) {
    console.error('保存状态文件失败:', e.message);
  }
}

// 格式化文件大小
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 获取文件类型
function getFileType(filename) {
  const ext = path.extname(filename).toLowerCase();
  const typeMap = {
    // 图片
    '.jpg': '图片', '.jpeg': '图片', '.png': '图片', '.gif': '图片', '.bmp': '图片', '.webp': '图片',
    // 文档
    '.pdf': '文档', '.doc': '文档', '.docx': '文档', '.xls': '文档', '.xlsx': '文档', 
    '.ppt': '文档', '.pptx': '文档', '.txt': '文档', '.md': '文档', '.csv': '文档',
    // 压缩包
    '.zip': '压缩包', '.rar': '压缩包', '.7z': '压缩包', '.tar': '压缩包', '.gz': '压缩包',
    // 音频
    '.mp3': '音频', '.wav': '音频', '.aac': '音频', '.m4a': '音频',
    // 视频
    '.mp4': '视频', '.avi': '视频', '.mov': '视频', '.wmv': '视频', '.flv': '视频',
  };
  return typeMap[ext] || '文件';
}

// 生成通知消息
function generateNotifyMessage(filePath, stats) {
  const fileName = path.basename(filePath);
  const fileSize = formatBytes(stats.size);
  const fileType = getFileType(fileName);
  const timestamp = new Date(stats.mtime).toLocaleString('zh-CN');
  
  return `🦞 小龙虾收到啦！你的文件已经乖乖躺好咯~

📁 文件位置：\`${filePath}\`
📊 文件大小：${fileSize}
📂 文件类型：${fileType}
📅 接收时间：${timestamp}

需要我帮你处理这个文件吗？😊`;
}

// 获取媒体文件夹中的所有文件
function getMediaFiles() {
  try {
    return fs.readdirSync(MEDIA_DIR)
      .filter(file => !file.startsWith('.'))
      .map(file => ({
        name: file,
        path: path.join(MEDIA_DIR, file),
        stats: fs.statSync(path.join(MEDIA_DIR, file))
      }));
  } catch (e) {
    console.error('读取媒体文件夹失败:', e.message);
    return [];
  }
}

// 主循环
function watchLoop() {
  const state = loadState();
  const files = getMediaFiles();
  let hasNewFile = false;
  
  files.forEach(file => {
    // 检查是否是新文件（5 分钟内）且未通知过
    const isRecent = Date.now() - file.stats.mtimeMs < 5 * 60 * 1000;
    const isNotified = state.notifiedFiles.includes(file.name);
    
    if (isRecent && !isNotified) {
      hasNewFile = true;
      const message = generateNotifyMessage(file.path, file.stats);
      
      // 输出到控制台（实际使用时可以通过钉钉 API 发送）
      console.log('='.repeat(60));
      console.log('📬 新文件到达！');
      console.log(message);
      console.log('='.repeat(60));
      
      // 记录已通知
      state.notifiedFiles.push(file.name);
      
      // 清理旧记录（保留最近 100 个）
      if (state.notifiedFiles.length > 100) {
        state.notifiedFiles = state.notifiedFiles.slice(-100);
      }
    }
  });
  
  if (hasNewFile) {
    saveState(state);
  }
}

// 启动监听
console.log('🦞 小龙虾文件位置通知服务已启动...');
console.log(`📁 监听目录：${MEDIA_DIR}`);
console.log(`⏱️  检查间隔：${CHECK_INTERVAL_MS / 1000}秒`);
console.log('按 Ctrl+C 停止服务\n');

// 立即执行一次
watchLoop();

// 定时检查
setInterval(watchLoop, CHECK_INTERVAL_MS);

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n👋 小龙虾要休息啦~ 服务已停止');
  process.exit(0);
});

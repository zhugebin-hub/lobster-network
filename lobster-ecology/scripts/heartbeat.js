#!/usr/bin/env node

/**
 * 🦞 小龙虾生态网络 - 心跳服务
 * 
 * 定期向路由小龙虾发送心跳，保持在线状态
 * 
 * 使用:
 *   node heartbeat.js
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

// 加载配置
const CONFIG_FILE = path.join(__dirname, '..', 'lobster-config.json');

let config;
try {
  config = require(CONFIG_FILE);
} catch {
  console.error('❌ 配置文件不存在，请先运行 join-ecology.js');
  console.error(`   路径: ${CONFIG_FILE}`);
  process.exit(1);
}

const HEARTBEAT_INTERVAL = 30000; // 30 秒
const ROUTER_URL = config.router_url || 'http://172.24.56.3:8081/mcp';

function sendHeartbeat() {
  const payload = {
    jsonrpc: '2.0',
    id: Date.now(),
    method: 'tools/call',
    params: {
      name: 'heartbeat',
      arguments: {
        lobster_id: config.lobster_id
      }
    }
  };

  const url = new URL(ROUTER_URL);

  const options = {
    hostname: url.hostname,
    port: url.port || 8081,
    path: url.pathname,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    timeout: 5000
  };

  const req = http.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      try {
        const response = JSON.parse(data);
        if (response.result) {
          console.log(`💓 [${new Date().toISOString()}] 心跳成功`);
        } else {
          console.warn(`⚠️  心跳响应异常: ${data}`);
        }
      } catch {
        console.warn(`⚠️  心跳响应解析失败`);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`❌ [${new Date().toISOString()}] 心跳失败: ${e.message}`);
  });

  req.on('timeout', () => {
    req.destroy();
    console.error(`❌ 心跳超时`);
  });

  req.write(JSON.stringify(payload));
  req.end();
}

// 启动
console.log(`🦞 心跳服务启动`);
console.log(`   小龙虾ID: ${config.lobster_id}`);
console.log(`   路由地址: ${ROUTER_URL}`);
console.log(`   间隔: ${HEARTBEAT_INTERVAL / 1000} 秒`);
console.log('');

// 立即发送一次
sendHeartbeat();

// 定时发送
setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n🦞 心跳服务停止');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🦞 心跳服务停止');
  process.exit(0);
});

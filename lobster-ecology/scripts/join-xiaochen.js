#!/usr/bin/env node

/**
 * 🦞 小龙虾生态网络 - 小陈专属接入脚本
 * 
 * 使用方法:
 *   在小陈的服务器上运行:
 *   node join-xiaochen.js
 * 
 * 功能:
 *   1. 检查环境依赖
 *   2. 生成小陈小龙虾ID
 *   3. 自动注册到路由小龙虾（诸葛马）
 *   4. 验证连接
 *   5. 生成配置文件
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { execSync } = require('child_process');

// ============ 配置 ============

const ECOLOGY_VERSION = '1.0.0';
const SHARED_DIR = '/shared/ecology';
const REGISTRY_FILE = path.join(SHARED_DIR, 'registry.json');

// 小陈专用配置
const LOBSTER_ID = 'lobster-003';  // 小陈专属ID
const LOBSTER_NAME = '小陈小龙虾';
const CAPABILITIES = ['personal_assistant', 'teaching_analysis', 'course_management'];
const PLATFORMS = ['dingtalk'];

// 路由小龙虾地址（诸葛马）
const ROUTER_HOST = '172.24.57.34';
const ROUTER_PORT = 8081;
const ROUTER_MCP_URL = `http://${ROUTER_HOST}:${ROUTER_PORT}/mcp`;

// 配置目录
const CONFIG_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'lobster-ecology');
const CONFIG_FILE = path.join(CONFIG_DIR, 'lobster-config.json');

// ============ 工具函数 ============

function log(msg, type = 'info') {
  const icons = {
    info: 'ℹ️',
    success: '✅',
    error: '❌',
    warn: '⚠️',
    step: '📌'
  };
  const icon = icons[type] || 'ℹ️';
  console.log(`${icon} ${msg}`);
}

function getLocalIp() {
  try {
    const output = execSync("hostname -I | awk '{print $1}'").toString().trim();
    return output || '127.0.0.1';
  } catch {
    return '127.0.0.1';
  }
}

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============ 步骤 ============

async function step1_checkEnvironment() {
  log('步骤 1/5: 检查环境依赖...', 'step');
  
  // 检查 Node.js
  const nodeVersion = process.version;
  log(`Node.js 版本: ${nodeVersion}`);
  
  // 检查 NFS 共享目录
  if (!fs.existsSync(SHARED_DIR)) {
    log('NFS 共享目录不存在，尝试创建...', 'warn');
    try {
      fs.mkdirSync(SHARED_DIR, { recursive: true });
      log('已创建共享目录', 'success');
    } catch (e) {
      log('无法创建共享目录，请检查 NFS 挂载', 'error');
      log('运行: mount -t nfs 172.24.57.34:/shared /shared', 'warn');
      process.exit(1);
    }
  } else {
    log('NFS 共享目录已挂载', 'success');
  }
  
  // 检查配置目录
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
    log('已创建配置目录', 'success');
  }
  
  await sleep(500);
}

async function step2_collectInfo() {
  log('步骤 2/5: 收集小龙虾信息...', 'step');
  
  const localIp = getLocalIp();
  const hostname = require('os').hostname();
  
  const info = {
    lobsterId: LOBSTER_ID,
    lobsterName: LOBSTER_NAME,
    serverIp: localIp,
    hostname,
    capabilities: CAPABILITIES,
    platforms: PLATFORMS
  };
  
  log(`小龙虾ID: ${info.lobsterId}`);
  log(`小龙虾名称: ${info.lobsterName}`);
  log(`服务器IP: ${info.serverIp}`);
  log(`能力标签: ${info.capabilities.join(', ')}`);
  log(`支持平台: ${info.platforms.join(', ')}`);
  
  await sleep(500);
  return info;
}

async function step3_registerToRouter(info) {
  log('步骤 3/5: 注册到路由小龙虾（诸葛马）...', 'step');
  
  const token = generateToken();
  
  const registrationPayload = {
    lobster_id: info.lobsterId,
    lobster_name: info.lobsterName,
    server_ip: info.serverIp,
    hostname: info.hostname,
    mcp_endpoint: `http://${info.serverIp}:8082/mcp`,
    capabilities: info.capabilities,
    platforms: info.platforms,
    token: token,
    ecology_version: ECOLOGY_VERSION,
    registered_at: new Date().toISOString()
  };
  
  // 尝试调用路由小龙虾注册接口
  try {
    const response = await callMCPTool('register_lobster', registrationPayload);
    
    if (response.success) {
      log('成功注册到路由小龙虾（诸葛马）', 'success');
    } else {
      log(`注册失败: ${response.error}`, 'error');
      log('将信息写入共享注册表', 'warn');
      writeToSharedRegistry(registrationPayload);
    }
  } catch (e) {
    log(`无法连接路由小龙虾 (${ROUTER_MCP_URL})`, 'warn');
    log('将注册信息写入共享目录，等待路由小龙虾同步', 'warn');
    writeToSharedRegistry(registrationPayload);
  }
  
  // 保存本地配置
  const localConfig = {
    lobster_id: info.lobsterId,
    lobster_name: info.lobsterName,
    server_ip: info.serverIp,
    hostname: info.hostname,
    mcp_endpoint: `http://${info.serverIp}:8082/mcp`,
    capabilities: info.capabilities,
    platforms: info.platforms,
    lobster_token: token,
    router_url: ROUTER_MCP_URL,
    ecology_version: ECOLOGY_VERSION,
    created_at: new Date().toISOString()
  };
  
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(localConfig, null, 2));
  log(`本地配置已保存: ${CONFIG_FILE}`, 'success');
  
  await sleep(500);
  return localConfig;
}

function writeToSharedRegistry(registrationPayload) {
  const pendingDir = path.join(SHARED_DIR, 'pending-registrations');
  if (!fs.existsSync(pendingDir)) {
    fs.mkdirSync(pendingDir, { recursive: true });
  }
  
  const fileName = `${registrationPayload.lobster_id}-${Date.now()}.json`;
  const filePath = path.join(pendingDir, fileName);
  
  fs.writeFileSync(filePath, JSON.stringify(registrationPayload, null, 2));
  log(`注册信息已写入: ${filePath}`, 'info');
}

async function step4_verifyConnection(config) {
  log('步骤 4/5: 验证连接...', 'step');
  
  // 尝试连接路由小龙虾
  try {
    const response = await callMCPTool('discover_lobsters', {});
    
    if (response.success) {
      const lobsters = response.lobsters || [];
      log(`发现 ${lobsters.length} 只在线小龙虾`, 'success');
      lobsters.forEach(l => {
        log(`  - ${l.name} (${l.id}) [${l.status}]`, 'info');
      });
    }
  } catch (e) {
    log('暂时无法验证连接（路由小龙虾可能尚未启动）', 'warn');
    log('连接将在路由小龙虾启动后自动建立', 'info');
  }
  
  await sleep(500);
}

async function step5_summary(config) {
  log('步骤 5/5: 接入完成！', 'step');
  
  console.log(`
╔══════════════════════════════════════════════════════╗
║         🦞 小龙虾生态网络 - 小陈接入成功!            ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  小龙虾ID:    ${config.lobster_id.padEnd(30)}║
║  小龙虾名称:  ${config.lobster_name.padEnd(30)}║
║  服务器IP:    ${config.server_ip.padEnd(30)}║
║  能力标签:    ${config.capabilities.join(', ').padEnd(30)}║
║  支持平台:    ${config.platforms.join(', ').padEnd(30)}║
║                                                      ║
║  路由小龙虾:  诸葛马 (${ROUTER_HOST.padEnd(16)})║
║  路由地址:    ${ROUTER_MCP_URL.padEnd(30)}║
║                                                      ║
║  配置文件:    ${CONFIG_FILE.padEnd(30)}║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  下一步:                                             ║
║  1. 启动心跳: node heartbeat.js                      ║
║  2. 查看在线小龙虾: node discover.js                 ║
║  3. 发送测试消息给虾尔: node test-message.js         ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
  `);
  
  log('欢迎小陈加入小龙虾生态网络！🦞🦞🦞', 'success');
}

// ============ MCP 调用 ============

async function callMCPTool(toolName, params) {
  const payload = {
    jsonrpc: '2.0',
    id: Date.now(),
    method: 'tools/call',
    params: {
      name: toolName,
      arguments: params
    }
  };
  
  return new Promise((resolve, reject) => {
    const url = new URL(ROUTER_MCP_URL);
    
    const options = {
      hostname: url.hostname,
      port: url.port || 8081,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
      },
      timeout: 5000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve({ success: false, error: 'Invalid response' });
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.write(JSON.stringify(payload));
    req.end();
  });
}

// ============ 主流程 ============

async function main() {
  console.log(`
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   🦞  小龙虾生态网络  -  小陈专属接入脚本             ║
║                                                      ║
║   版本: ${ECOLOGY_VERSION.padEnd(36)}║
║   日期: 2026-06-12                                 ║
║   路由: 诸葛马 (${ROUTER_HOST})                       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
  `);
  
  await step1_checkEnvironment();
  const info = await step2_collectInfo();
  const config = await step3_registerToRouter(info);
  await step4_verifyConnection(config);
  await step5_summary(config);
}

main().catch(e => {
  log(`接入失败: ${e.message}`, 'error');
  process.exit(1);
});

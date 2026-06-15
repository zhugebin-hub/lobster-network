#!/usr/bin/env node

/**
 * 🦞 路由小龙虾 MCP Server
 * 
 * 功能:
 *   - 接收业务小龙虾注册
 *   - 路由消息到目标小龙虾
 *   - 服务发现
 *   - 广播消息
 *   - 心跳检测
 * 
 * 启动:
 *   node router-server.js
 */

const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// ============ 配置 ============

const PORT = process.env.ROUTER_PORT || 8081;
const REGISTRY_FILE = '/shared/ecology/registry.json';
const HEARTBEAT_INTERVAL = 30000; // 30 秒
const HEARTBEAT_TIMEOUT = 90000;  // 90 秒无心跳视为离线

// ============ 注册表管理 ============

function loadRegistry() {
  if (!fs.existsSync(REGISTRY_FILE)) {
    return {
      version: '1.0',
      updated_at: new Date().toISOString(),
      lobsters: []
    };
  }
  try {
    return JSON.parse(fs.readFileSync(REGISTRY_FILE, 'utf8'));
  } catch {
    return { version: '1.0', updated_at: new Date().toISOString(), lobsters: [] };
  }
}

function saveRegistry(registry) {
  registry.updated_at = new Date().toISOString();
  const dir = path.dirname(REGISTRY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(REGISTRY_FILE, JSON.stringify(registry, null, 2));
}

function findLobster(id) {
  const registry = loadRegistry();
  return registry.lobsters.find(l => l.id === id);
}

function updateLobsterStatus(id, status) {
  const registry = loadRegistry();
  const lobster = registry.lobsters.find(l => l.id === id);
  if (lobster) {
    lobster.status = status;
    lobster.last_heartbeat = new Date().toISOString();
    saveRegistry(registry);
  }
  return lobster;
}

// ============ MCP 工具处理 ============

const tools = {
  register_lobster: async (args) => {
    console.log(`📝 注册小龙虾: ${args.lobster_name} (${args.lobster_id})`);
    
    const registry = loadRegistry();
    
    // 检查是否已存在
    const existing = registry.lobsters.find(l => l.id === args.lobster_id);
    if (existing) {
      // 更新现有记录
      Object.assign(existing, {
        server_ip: args.server_ip,
        mcp_endpoint: args.mcp_endpoint,
        capabilities: args.capabilities,
        platforms: args.platforms,
        status: 'online',
        last_heartbeat: new Date().toISOString()
      });
    } else {
      // 新增记录
      registry.lobsters.push({
        id: args.lobster_id,
        name: args.lobster_name,
        type: args.type || 'business',
        server_ip: args.server_ip,
        mcp_endpoint: args.mcp_endpoint,
        capabilities: args.capabilities,
        platforms: args.platforms,
        status: 'online',
        last_heartbeat: new Date().toISOString(),
        joined_at: new Date().toISOString()
      });
    }
    
    saveRegistry(registry);
    
    return {
      success: true,
      message: `小龙虾 ${args.lobster_name} 已成功注册`,
      lobster_id: args.lobster_id,
      total_lobsters: registry.lobsters.length
    };
  },

  discover_lobsters: async (args) => {
    const registry = loadRegistry();
    let lobsters = registry.lobsters;
    
    if (args.capability) {
      lobsters = lobsters.filter(l => l.capabilities.includes(args.capability));
    }
    
    if (args.status && args.status !== 'all') {
      lobsters = lobsters.filter(l => l.status === args.status);
    }
    
    // 检查心跳超时
    const now = Date.now();
    lobsters.forEach(l => {
      if (l.last_heartbeat) {
        const lastBeat = new Date(l.last_heartbeat).getTime();
        if (now - lastBeat > HEARTBEAT_TIMEOUT && l.status === 'online') {
          l.status = 'offline';
        }
      }
    });
    
    return {
      success: true,
      lobsters: lobsters.map(l => ({
        id: l.id,
        name: l.name,
        type: l.type,
        capabilities: l.capabilities,
        platforms: l.platforms,
        status: l.status,
        last_heartbeat: l.last_heartbeat
      })),
      total: lobsters.length
    };
  },

  route_message: async (args) => {
    console.log(`📨 路由消息: ${args.from_lobster_id} -> ${args.target_lobster_id || '智能路由'}`);
    
    let targetId = args.target_lobster_id;
    
    // 智能路由：根据意图匹配
    if (!targetId && args.intent) {
      const registry = loadRegistry();
      const onlineLobsters = registry.lobsters.filter(l => l.status === 'online');
      
      // 匹配能力标签
      const matched = onlineLobsters.find(l => l.capabilities.includes(args.intent));
      if (matched) {
        targetId = matched.id;
        console.log(`🧠 智能路由匹配: ${args.intent} -> ${matched.name} (${matched.id})`);
      }
    }
    
    if (!targetId) {
      return {
        success: false,
        error: '未找到目标小龙虾，且无法智能路由'
      };
    }
    
    const target = findLobster(targetId);
    if (!target) {
      return {
        success: false,
        error: `目标小龙虾不存在: ${targetId}`
      };
    }
    
    if (target.status !== 'online') {
      return {
        success: false,
        error: `目标小龙虾离线: ${target.name} (${targetId})`
      };
    }
    
    // 转发消息到目标小龙虾
    try {
      const response = await forwardMessage(target.mcp_endpoint, {
        protocol: 'lobster-ecology',
        version: '1.0',
        message_id: args.message_id,
        timestamp: new Date().toISOString(),
        from: {
          lobster_id: args.from_lobster_id,
          user_id: args.from_user_id
        },
        to: {
          lobster_id: targetId
        },
        type: args.require_response ? 'request' : 'notification',
        intent: args.intent,
        payload: args.payload,
        metadata: {
          routed_by: 'lobster-router',
          priority: args.priority || 'normal',
          ttl_seconds: args.ttl_seconds || 300
        }
      });
      
      return {
        success: true,
        target: targetId,
        response: response
      };
    } catch (e) {
      return {
        success: false,
        error: `消息转发失败: ${e.message}`
      };
    }
  },

  broadcast_message: async (args) => {
    console.log(`📢 广播消息: from ${args.from_lobster_id}`);
    
    const registry = loadRegistry();
    const onlineLobsters = registry.lobsters.filter(
      l => l.status === 'online' && l.id !== args.from_lobster_id && !(args.exclude || []).includes(l.id)
    );
    
    const results = [];
    for (const lobster of onlineLobsters) {
      try {
        await forwardMessage(lobster.mcp_endpoint, {
          protocol: 'lobster-ecology',
          version: '1.0',
          message_id: `broadcast-${Date.now()}`,
          timestamp: new Date().toISOString(),
          from: { lobster_id: args.from_lobster_id },
          to: { lobster_id: 'broadcast' },
          type: 'broadcast',
          payload: { message: args.message }
        });
        results.push({ lobster_id: lobster.id, status: 'sent' });
      } catch (e) {
        results.push({ lobster_id: lobster.id, status: 'failed', error: e.message });
      }
    }
    
    return {
      success: true,
      sent: results.filter(r => r.status === 'sent').length,
      failed: results.filter(r => r.status === 'failed').length,
      results
    };
  },

  get_lobster_status: async (args) => {
    const lobster = findLobster(args.lobster_id);
    if (!lobster) {
      return { success: false, error: '小龙虾不存在' };
    }
    
    return {
      success: true,
      lobster: {
        id: lobster.id,
        name: lobster.name,
        type: lobster.type,
        status: lobster.status,
        capabilities: lobster.capabilities,
        platforms: lobster.platforms,
        last_heartbeat: lobster.last_heartbeat,
        joined_at: lobster.joined_at
      }
    };
  },

  heartbeat: async (args) => {
    const lobster = updateLobsterStatus(args.lobster_id, 'online');
    if (!lobster) {
      return { success: false, error: '小龙虾未注册' };
    }
    return { success: true, status: 'pong', timestamp: new Date().toISOString() };
  }
};

// ============ 消息转发 ============

async function forwardMessage(endpoint, message) {
  const http = require('http');
  const url = new URL(endpoint);
  
  return new Promise((resolve, reject) => {
    const payload = {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'message/receive',
      params: message
    };
    
    const options = {
      hostname: url.hostname,
      port: url.port || 8082,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve({ raw: data });
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Forward timeout'));
    });
    
    req.write(JSON.stringify(payload));
    req.end();
  });
}

// ============ API 路由 ============

// MCP 标准端点
app.post('/mcp', async (req, res) => {
  const { method, params, id } = req.body;
  
  if (method === 'tools/call') {
    const { name, arguments: args } = params;
    const handler = tools[name];
    
    if (!handler) {
      return res.status(400).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: `Unknown tool: ${name}` }
      });
    }
    
    try {
      const result = await handler(args);
      res.json({
        jsonrpc: '2.0',
        id,
        result: { content: [{ type: 'text', text: JSON.stringify(result) }] }
      });
    } catch (e) {
      res.status(500).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32603, message: e.message }
      });
    }
  } else if (method === 'message/receive') {
    // 接收来自其他小龙虾的直接消息
    console.log('📨 收到直接消息:', JSON.stringify(params).substring(0, 200));
    res.json({ jsonrpc: '2.0', id, result: { status: 'received' } });
  } else {
    res.status(400).json({
      jsonrpc: '2.0',
      id,
      error: { code: -32601, message: `Unknown method: ${method}` }
    });
  }
});

// 健康检查
app.get('/health', (req, res) => {
  const registry = loadRegistry();
  const online = registry.lobsters.filter(l => l.status === 'online').length;
  const total = registry.lobsters.length;
  
  res.json({
    status: 'ok',
    version: '1.0.0',
    lobsters: { online, total },
    uptime: process.uptime()
  });
});

// ============ 启动 ============

app.listen(PORT, () => {
  console.log(`🦞 路由小龙虾 MCP Server 已启动`);
  console.log(`   端口: ${PORT}`);
  console.log(`   端点: http://0.0.0.0:${PORT}/mcp`);
  console.log(`   健康检查: http://0.0.0.0:${PORT}/health`);
  console.log(`   注册表: ${REGISTRY_FILE}`);
  
  // 确保注册表目录存在
  const dir = path.dirname(REGISTRY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  // 注册自己
  const registry = loadRegistry();
  const self = registry.lobsters.find(l => l.id === 'lobster-router');
  if (!self) {
    registry.lobsters.push({
      id: 'lobster-router',
      name: '路由小龙虾',
      type: 'router',
      server_ip: '172.24.56.3',
      mcp_endpoint: `http://172.24.56.3:${PORT}/mcp`,
      capabilities: ['routing', 'discovery', 'broadcast', 'registry'],
      platforms: [],
      status: 'online',
      last_heartbeat: new Date().toISOString(),
      joined_at: new Date().toISOString()
    });
    saveRegistry(registry);
  }
});

// 定期清理离线小龙虾
setInterval(() => {
  const registry = loadRegistry();
  const now = Date.now();
  let changed = false;
  
  registry.lobsters.forEach(l => {
    if (l.last_heartbeat) {
      const lastBeat = new Date(l.last_heartbeat).getTime();
      if (now - lastBeat > HEARTBEAT_TIMEOUT && l.status === 'online') {
        console.log(`⏰ 小龙虾 ${l.name} (${l.id}) 心跳超时，标记为离线`);
        l.status = 'offline';
        changed = true;
      }
    }
  });
  
  if (changed) {
    saveRegistry(registry);
  }
}, HEARTBEAT_INTERVAL);

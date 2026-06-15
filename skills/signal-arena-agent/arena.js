/**
 * Signal Arena API 封装
 * 信电大虾 - 自动交易 Agent 核心模块
 */

const axios = require('axios');
require('dotenv').config();

const BASE_URL = process.env.BASE_URL || 'https://signal.coze.site';
const API_KEY = process.env.AGENT_WORLD_API_KEY;

const arena = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'agent-auth-api-key': API_KEY
  }
});

// 错误处理
function handleError(error) {
  if (error.response) {
    const { status, data } = error.response;
    console.error(`❌ API 错误 [${status}]:`, data.message || data);
    return data;
  }
  console.error('❌ 网络错误:', error.message);
  return null;
}

// 加入竞技场
async function joinArena() {
  try {
    const res = await arena.post('/api/v1/arena/join');
    console.log('✅ 加入竞技场成功');
    console.log('   初始资金:', res.data.data.initial_capital);
    console.log('   可用现金:', res.data.data.cash);
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取全局状态（推荐每次决策前调用）
async function getHome() {
  try {
    const res = await arena.get('/api/v1/arena/home');
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取持仓详情
async function getPortfolio() {
  try {
    const res = await arena.get('/api/v1/arena/portfolio');
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取股票列表
async function getStocks(market = 'CN', limit = 20, search = null) {
  try {
    const params = { market, limit };
    if (search) params.search = search;
    const res = await arena.get('/api/v1/arena/stocks', { params });
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取涨幅榜
async function getTopMovers() {
  try {
    const res = await arena.get('/api/v1/arena/top-movers');
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取股票历史行情
async function getStockHistory(symbol) {
  try {
    const res = await arena.get('/api/v1/arena/stock-history', {
      params: { symbol }
    });
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 执行交易
async function trade(symbol, action, shares, reason = '') {
  try {
    const res = await arena.post('/api/v1/arena/trade', {
      symbol,
      action,
      shares,
      reason
    });
    console.log(`✅ 订单提交：${action.toUpperCase()} ${symbol} ${shares}股`);
    if (reason) console.log('   理由:', reason);
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 快捷买入
async function buy(symbol, shares, reason = '') {
  return trade(symbol, 'buy', shares, reason);
}

// 快捷卖出
async function sell(symbol, shares, reason = '') {
  return trade(symbol, 'sell', shares, reason);
}

// 获取收益率排行榜
async function getLeaderboard() {
  try {
    const res = await arena.get('/api/v1/arena/leaderboard');
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

// 获取交易记录
async function getTrades() {
  try {
    const res = await arena.get('/api/v1/arena/trades');
    return res.data;
  } catch (error) {
    return handleError(error);
  }
}

module.exports = {
  joinArena,
  getHome,
  getPortfolio,
  getStocks,
  getTopMovers,
  getStockHistory,
  trade,
  buy,
  sell,
  getLeaderboard,
  getTrades
};

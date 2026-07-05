/**
 * API 服务
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.lobster-network.ai/v4';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 钱包 API
export const getWallet = (nodeId: string) => {
  return api.get(`/wallet?node_id=${nodeId}`);
};

export const createWallet = (data: { node_id: string }) => {
  return api.post('/wallet', data);
};

export const getBalance = (nodeId: string, currency?: string) => {
  return api.get(`/wallet/${nodeId}/balance`, {
    params: { currency },
  });
};

export const transfer = (nodeId: string, data: { to_node_id: string; amount: number; currency?: string; memo?: string }) => {
  return api.post(`/wallet/${nodeId}/transfer`, data);
};

// 节点 API
export const getNodes = (status?: string) => {
  return api.get('/node', {
    params: { status },
  });
};

export const registerNode = (data: { node_id: string; name: string; type: string; perspective?: string; knowledge_base?: string }) => {
  return api.post('/node', data);
};

// 任务 API
export const getTasks = (status?: string) => {
  return api.get('/task', {
    params: { status },
  });
};

export const createTask = (data: { title: string; description: string; reward_amount?: number; task_type?: string }) => {
  return api.post('/task', data);
};

export const claimTask = (taskId: string, data: { node_id: string }) => {
  return api.post(`/task/${taskId}/claim`, data);
};

// 治理 API
export const getProposals = (status?: string) => {
  return api.get('/proposal', {
    params: { status },
  });
};

export const createProposal = (data: { title: string; description: string; proposal_type?: string }) => {
  return api.post('/proposal', data);
};

export const vote = (proposalId: string, data: { voter_id: string; option: string; reason?: string }) => {
  return api.post(`/proposal/${proposalId}/vote`, data);
};

// 统计 API
export const getStats = () => {
  return api.get('/stats');
};

export default api;
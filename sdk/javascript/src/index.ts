/**
 * 小龙虾网络 JavaScript SDK
 * 
 * @example
 * ```javascript
 * import { LobsterClient } from 'lobster-sdk-js';
 * 
 * const client = new LobsterClient({
 *   apiUrl: 'https://api.lobster-network.ai/v4',
 *   apiKey: 'your-api-key',
 * });
 * 
 * // 创建钱包
 * await client.wallet.create('my-lobster');
 * 
 * // 查看余额
 * const balance = await client.wallet.balance('my-lobster');
 * console.log(`余额: ${balance} 🦞`);
 * ```
 */

import axios, { AxiosInstance } from 'axios';

export interface LobsterClientConfig {
  apiUrl: string;
  apiKey?: string;
}

export class LobsterClient {
  private api: AxiosInstance;
  public wallet: Wallet;
  public node: Node;
  public task: Task;
  public governance: Governance;

  constructor(config: LobsterClientConfig) {
    this.api = axios.create({
      baseURL: config.apiUrl,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {}),
      },
    });

    this.wallet = new Wallet(this.api);
    this.node = new Node(this.api);
    this.task = new Task(this.api);
    this.governance = new Governance(this.api);
  }
}

export class Wallet {
  constructor(private api: AxiosInstance) {}

  async create(nodeId: string) {
    return this.api.post('/wallet', { node_id: nodeId });
  }

  async get(nodeId: string) {
    return this.api.get(`/wallet?node_id=${nodeId}`);
  }

  async balance(nodeId: string, currency?: string) {
    return this.api.get(`/wallet/${nodeId}/balance`, { params: { currency } });
  }

  async transfer(nodeId: string, data: { to_node_id: string; amount: number; currency?: string; memo?: string }) {
    return this.api.post(`/wallet/${nodeId}/transfer`, data);
  }

  async stake(nodeId: string, amount: number) {
    return this.api.post(`/wallet/${nodeId}/stake`, { amount });
  }

  async unstake(nodeId: string, amount: number) {
    return this.api.post(`/wallet/${nodeId}/unstake`, { amount });
  }

  async mine(nodeId: string, emergenceScore: number = 0.5) {
    return this.api.post(`/node/${nodeId}/mine`, { emergence_score: emergenceScore });
  }
}

export class Node {
  constructor(private api: AxiosInstance) {}

  async list(status?: string) {
    return this.api.get('/node', { params: { status } });
  }

  async register(data: { node_id: string; name: string; type: string; perspective?: string; knowledge_base?: string }) {
    return this.api.post('/node', data);
  }
}

export class Task {
  constructor(private api: AxiosInstance) {}

  async list(status?: string) {
    return this.api.get('/task', { params: { status } });
  }

  async create(data: { title: string; description: string; reward_amount?: number; task_type?: string }) {
    return this.api.post('/task', data);
  }

  async claim(taskId: string, nodeId: string) {
    return this.api.post(`/task/${taskId}/claim`, { node_id: nodeId });
  }

  async submit(taskId: string, result: string) {
    return this.api.post(`/task/${taskId}/submit`, { result });
  }

  async review(taskId: string, reviewerId: string, approved: boolean, feedback?: string) {
    return this.api.post(`/task/${taskId}/review`, { reviewer_id: reviewerId, approved, feedback });
  }
}

export class Governance {
  constructor(private api: AxiosInstance) {}

  async list(status?: string) {
    return this.api.get('/proposal', { params: { status } });
  }

  async create(data: { title: string; description: string; proposal_type?: string }) {
    return this.api.post('/proposal', data);
  }

  async vote(proposalId: string, data: { voter_id: string; option: string; reason?: string }) {
    return this.api.post(`/proposal/${proposalId}/vote`, data);
  }

  async checkResult(proposalId: string) {
    return this.api.post(`/proposal/${proposalId}/check`);
  }

  async execute(proposalId: string) {
    return this.api.post(`/proposal/${proposalId}/execute`);
  }
}

export default LobsterClient;
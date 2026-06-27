/**
 * 仪表盘页面
 */

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Space, Button } from 'antd';
import {
  TeamOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  BlockOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';
import { getStats, getNodes, getTasks } from '../services/api';

interface Stats {
  total_nodes: number;
  active_nodes: number;
  total_tasks: number;
  completed_tasks: number;
  total_supply: number;
  circulating_supply: number;
  blockchain_length: number;
}

interface Node {
  node_id: string;
  name: string;
  type: string;
  status: string;
  perspective: string;
}

interface Task {
  task_id: string;
  title: string;
  status: string;
  reward_amount: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, nodesData, tasksData] = await Promise.all([
        getStats(),
        getNodes(),
        getTasks(),
      ]);
      setStats(statsData);
      setNodes(nodesData);
      setTasks(tasksData);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const nodeColumns = [
    {
      title: '节点 ID',
      dataIndex: 'node_id',
      key: 'node_id',
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={type === 'agent' ? 'blue' : type === 'coach' ? 'green' : 'orange'}>
          {type}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'default'}>
          {status === 'active' ? '活跃' : '离线'}
        </Tag>
      ),
    },
    {
      title: '视角',
      dataIndex: 'perspective',
      key: 'perspective',
    },
  ];

  const taskColumns = [
    {
      title: '任务 ID',
      dataIndex: 'task_id',
      key: 'task_id',
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={
          status === 'pending' ? 'default' :
          status === 'assigned' ? 'processing' :
          status === 'completed' ? 'success' : 'error'
        }>
          {status === 'pending' ? '待领取' :
           status === 'assigned' ? '进行中' :
           status === 'completed' ? '已完成' : status}
        </Tag>
      ),
    },
    {
      title: '奖励',
      dataIndex: 'reward_amount',
      key: 'reward_amount',
      render: (amount: number) => `${amount} 🦞`,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>🦞 小龙虾网络仪表盘</h1>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="总节点数"
              value={stats?.total_nodes || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="活跃节点"
              value={stats?.active_nodes || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="总供应量"
              value={stats?.total_supply || 0}
              prefix={<DollarOutlined />}
              precision={2}
              suffix="🦞"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="区块链长度"
              value={stats?.blockchain_length || 0}
              prefix={<BlockOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 节点列表 */}
      <Card
        title="节点列表"
        extra={<Button type="link" href="/nodes">查看全部 →</Button>}
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={nodeColumns}
          dataSource={nodes.slice(0, 5)}
          rowKey="node_id"
          pagination={false}
          loading={loading}
        />
      </Card>

      {/* 任务列表 */}
      <Card
        title="最近任务"
        extra={<Button type="link" href="/tasks">查看全部 →</Button>}
      >
        <Table
          columns={taskColumns}
          dataSource={tasks.slice(0, 5)}
          rowKey="task_id"
          pagination={false}
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
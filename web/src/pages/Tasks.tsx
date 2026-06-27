/**
 * 任务管理页面
 */

import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Modal, Form, Input, InputNumber, Select, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getTasks, createTask, claimTask } from '../services/api';

interface Task {
  task_id: string;
  title: string;
  description: string;
  publisher_id: string;
  assignee_id: string;
  status: string;
  reward_amount: number;
  created_at: string;
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
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
      title: '发布者',
      dataIndex: 'publisher_id',
      key: 'publisher_id',
    },
    {
      title: '领取者',
      dataIndex: 'assignee_id',
      key: 'assignee_id',
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
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Task) => (
        <Button
          type="link"
          disabled={record.status !== 'pending'}
          onClick={() => handleClaim(record.task_id)}
        >
          领取
        </Button>
      ),
    },
  ];

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error) {
      message.error('加载任务失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createTask(values);
      message.success('创建成功');
      setModalVisible(false);
      form.resetFields();
      loadTasks();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleClaim = async (taskId: string) => {
    try {
      const nodeId = localStorage.getItem('node_id') || '';
      await claimTask(taskId, { node_id: nodeId });
      message.success('领取成功');
      loadTasks();
    } catch (error) {
      message.error('领取失败');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>任务管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          发布任务
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="task_id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="发布任务"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="reward_amount" label="奖励" rules={[{ required: true }]} initialValue={10}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="task_type" label="类型" initialValue="labor">
            <Select>
              <Select.Option value="labor">劳务</Select.Option>
              <Select.Option value="flash">快闪</Select.Option>
              <Select.Option value="bounty">悬赏</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Tasks;
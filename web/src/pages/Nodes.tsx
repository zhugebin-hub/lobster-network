/**
 * 节点管理页面
 */

import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getNodes, registerNode } from '../services/api';

interface Node {
  node_id: string;
  name: string;
  type: string;
  status: string;
  perspective: string;
  knowledge_base: string;
  registered_at: string;
}

const Nodes: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
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
    {
      title: '知识',
      dataIndex: 'knowledge_base',
      key: 'knowledge_base',
    },
    {
      title: '注册时间',
      dataIndex: 'registered_at',
      key: 'registered_at',
    },
  ];

  useEffect(() => {
    loadNodes();
  }, []);

  const loadNodes = async () => {
    try {
      const data = await getNodes();
      setNodes(data);
    } catch (error) {
      message.error('加载节点失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    try {
      const values = await form.validateFields();
      await registerNode(values);
      message.success('注册成功');
      setModalVisible(false);
      form.resetFields();
      loadNodes();
    } catch (error) {
      message.error('注册失败');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>节点管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          注册节点
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={nodes}
        rowKey="node_id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="注册节点"
        open={modalVisible}
        onOk={handleRegister}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="node_id" label="节点 ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="agent">Agent</Select.Option>
              <Select.Option value="coach">教练</Select.Option>
              <Select.Option value="student">学生</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="perspective" label="视角">
            <Input />
          </Form.Item>
          <Form.Item name="knowledge_base" label="知识">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Nodes;
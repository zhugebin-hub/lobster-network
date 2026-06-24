/**
 * 治理页面
 */

import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Modal, Form, Input, Select, message, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getProposals, createProposal, vote } from '../services/api';

interface Proposal {
  proposal_id: string;
  title: string;
  description: string;
  creator_id: string;
  status: string;
  for_votes: number;
  against_votes: number;
  created_at: string;
}

const Governance: React.FC = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
    {
      title: '提案 ID',
      dataIndex: 'proposal_id',
      key: 'proposal_id',
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '创建者',
      dataIndex: 'creator_id',
      key: 'creator_id',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={
          status === 'draft' ? 'default' :
          status === 'active' ? 'processing' :
          status === 'passed' ? 'success' :
          status === 'rejected' ? 'error' : 'default'
        }>
          {status === 'draft' ? '草稿' :
           status === 'active' ? '投票中' :
           status === 'passed' ? '已通过' :
           status === 'rejected' ? '已拒绝' : status}
        </Tag>
      ),
    },
    {
      title: '赞成',
      dataIndex: 'for_votes',
      key: 'for_votes',
      render: (votes: number) => `${votes} 🦞`,
    },
    {
      title: '反对',
      dataIndex: 'against_votes',
      key: 'against_votes',
      render: (votes: number) => `${votes} 🦞`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Proposal) => (
        <Space>
          {record.status === 'active' && (
            <>
              <Button
                type="link"
                onClick={() => handleVote(record.proposal_id, 'for')}
              >
                赞成
              </Button>
              <Button
                type="link"
                danger
                onClick={() => handleVote(record.proposal_id, 'against')}
              >
                反对
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    try {
      const data = await getProposals();
      setProposals(data);
    } catch (error) {
      message.error('加载提案失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createProposal(values);
      message.success('创建成功');
      setModalVisible(false);
      form.resetFields();
      loadProposals();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleVote = async (proposalId: string, option: string) => {
    try {
      const voterId = localStorage.getItem('node_id') || '';
      await vote(proposalId, { voter_id: voterId, option });
      message.success('投票成功');
      loadProposals();
    } catch (error) {
      message.error('投票失败');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>治理提案</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          创建提案
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={proposals}
        rowKey="proposal_id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="创建提案"
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
          <Form.Item name="proposal_type" label="类型" initialValue="generic">
            <Select>
              <Select.Option value="param">参数调整</Select.Option>
              <Select.Option value="treasury">国库支出</Select.Option>
              <Select.Option value="contract">合约升级</Select.Option>
              <Select.Option value="generic">通用</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Governance;
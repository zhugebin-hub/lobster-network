/**
 * 钱包页面
 */

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Button, Modal, Form, Input, InputNumber, message, Table } from 'antd';
import { SendOutlined, WalletOutlined, LockOutlined, UnlockOutlined } from '@ant-design/icons';
import { getWallet, getBalance, transfer } from '../services/api';

interface Wallet {
  node_id: string;
  address: string;
  balance: number;
  staked: number;
  created_at: string;
}

interface Transaction {
  tx_id: string;
  from: string;
  to: string;
  amount: number;
  type: string;
  timestamp: string;
}

const WalletPage: React.FC = () => {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [transferModalVisible, setTransferModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
    {
      title: '交易 ID',
      dataIndex: 'tx_id',
      key: 'tx_id',
    },
    {
      title: '发送方',
      dataIndex: 'from',
      key: 'from',
    },
    {
      title: '接收方',
      dataIndex: 'to',
      key: 'to',
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => `${amount} 🦞`,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
  ];

  useEffect(() => {
    loadWallet();
  }, []);

  const loadWallet = async () => {
    try {
      const nodeId = localStorage.getItem('node_id') || '';
      const [walletData, balanceData, transactionsData] = await Promise.all([
        getWallet(nodeId),
        getBalance(nodeId),
        // Assuming there's a getTransactions API
        Promise.resolve([]),
      ]);
      setWallet({ ...walletData, ...balanceData });
      setTransactions(transactionsData);
    } catch (error) {
      message.error('加载钱包失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async () => {
    try {
      const values = await form.validateFields();
      const nodeId = localStorage.getItem('node_id') || '';
      await transfer(nodeId, values);
      message.success('转账成功');
      setTransferModalVisible(false);
      form.resetFields();
      loadWallet();
    } catch (error) {
      message.error('转账失败');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>钱包</h1>
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => setTransferModalVisible(true)}
        >
          转账
        </Button>
      </div>

      {/* 钱包信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading}>
            <Statistic
              title="余额"
              value={wallet?.balance || 0}
              prefix={<WalletOutlined />}
              precision={2}
              suffix="🦞"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading}>
            <Statistic
              title="质押"
              value={wallet?.staked || 0}
              prefix={<LockOutlined />}
              precision={2}
              suffix="🦞"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading}>
            <Statistic
              title="总计"
              value={(wallet?.balance || 0) + (wallet?.staked || 0)}
              prefix={<WalletOutlined />}
              precision={2}
              suffix="🦞"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 钱包地址 */}
      <Card title="钱包地址" style={{ marginBottom: 24 }}>
        <p>{wallet?.address || '未创建'}</p>
      </Card>

      {/* 交易记录 */}
      <Card title="交易记录">
        <Table
          columns={columns}
          dataSource={transactions}
          rowKey="tx_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 转账弹窗 */}
      <Modal
        title="转账"
        open={transferModalVisible}
        onOk={handleTransfer}
        onCancel={() => setTransferModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="to_node_id" label="接收方节点 ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="amount" label="金额" rules={[{ required: true }]}>
            <InputNumber min={0.01} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="memo" label="备注">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WalletPage;
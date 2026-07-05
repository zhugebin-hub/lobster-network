/**
 * 钱包页面
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Card, Button, TextInput } from 'react-native-paper';
import { getWallet, getBalance, transfer } from '../services/api';
import * as SecureStore from 'expo-secure-store';

export default function WalletScreen() {
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toNodeId, setToNodeId] = useState('');
  const [amount, setAmount] = useState('');
  const [transferring, setTransferring] = useState(false);

  useEffect(() => {
    loadWallet();
  }, []);

  const loadWallet = async () => {
    try {
      const nodeId = await SecureStore.getItemAsync('userToken');
      if (!nodeId) return;

      const [walletData, balanceData] = await Promise.all([
        getWallet(nodeId),
        getBalance(nodeId),
      ]);

      setWallet({ ...walletData, ...balanceData });
    } catch (error) {
      console.error('加载钱包失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async () => {
    if (!toNodeId || !amount) {
      Alert.alert('提示', '请填写完整信息');
      return;
    }

    setTransferring(true);
    try {
      const nodeId = await SecureStore.getItemAsync('userToken');
      await transfer(nodeId, {
        to_node_id: toNodeId,
        amount: parseFloat(amount),
      });

      Alert.alert('成功', '转账成功');
      setToNodeId('');
      setAmount('');
      loadWallet();
    } catch (error) {
      Alert.alert('错误', '转账失败');
    } finally {
      setTransferring(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>💰 钱包</Text>
      </View>

      {/* 余额卡片 */}
      <Card style={styles.balanceCard}>
        <Card.Content>
          <Text style={styles.balanceLabel}>余额</Text>
          <Text style={styles.balanceValue}>
            {wallet?.balance || 0} 🦞
          </Text>
          <Text style={styles.stakedLabel}>
            质押: {wallet?.staked || 0} 🦞
          </Text>
        </Card.Content>
      </Card>

      {/* 转账 */}
      <Card style={styles.card}>
        <Card.Title title="转账" />
        <Card.Content>
          <TextInput
            label="接收方节点 ID"
            value={toNodeId}
            onChangeText={setToNodeId}
            style={styles.input}
          />
          <TextInput
            label="金额"
            value={amount}
            onChangeText={setAmount}
            keyboardType="numeric"
            style={styles.input}
          />
          <Button
            mode="contained"
            onPress={handleTransfer}
            loading={transferring}
            disabled={transferring}
            style={styles.button}
          >
            转账
          </Button>
        </Card.Content>
      </Card>

      {/* 钱包地址 */}
      <Card style={styles.card}>
        <Card.Title title="钱包地址" />
        <Card.Content>
          <Text style={styles.address}>{wallet?.address || '加载中...'}</Text>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#1890ff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  balanceCard: {
    margin: 20,
    padding: 20,
    backgroundColor: '#1890ff',
  },
  balanceLabel: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  balanceValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 10,
  },
  stakedLabel: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.6,
    marginTop: 5,
  },
  card: {
    margin: 10,
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
  address: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
  },
});
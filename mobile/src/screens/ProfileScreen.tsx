/**
 * 我的页面
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Card, Button, List, Divider } from 'react-native-paper';
import * as SecureStore from 'expo-secure-store';
import { getWallet } from '../services/api';

export default function ProfileScreen({ navigation }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const nodeId = await SecureStore.getItemAsync('userToken');
      if (!nodeId) return;

      const walletData = await getWallet(nodeId);
      setUser({ nodeId, ...walletData });
    } catch (error) {
      console.error('加载用户信息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      '退出登录',
      '确定要退出登录吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: async () => {
            await SecureStore.deleteItemAsync('userToken');
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>👤 我的</Text>
      </View>

      {/* 用户信息 */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.userInfo}>
            <Text style={styles.avatar}>🦞</Text>
            <View style={styles.userDetails}>
              <Text style={styles.userName}>{user?.nodeId || '未登录'}</Text>
              <Text style={styles.userAddress}>
                地址: {user?.address || '加载中...'}
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* 资产信息 */}
      <Card style={styles.card}>
        <Card.Title title="资产信息" />
        <Card.Content>
          <List.Item
            title="余额"
            description={`${user?.balance || 0} 🦞`}
            left={(props) => <List.Icon {...props} icon="wallet" />}
          />
          <Divider />
          <List.Item
            title="质押"
            description={`${user?.staked || 0} 🦞`}
            left={(props) => <List.Icon {...props} icon="lock" />}
          />
          <Divider />
          <List.Item
            title="总计"
            description={`${(user?.balance || 0) + (user?.staked || 0)} 🦞`}
            left={(props) => <List.Icon {...props} icon="chart-line" />}
          />
        </Card.Content>
      </Card>

      {/* 设置 */}
      <Card style={styles.card}>
        <Card.Title title="设置" />
        <Card.Content>
          <List.Item
            title="个人资料"
            description="编辑个人信息"
            left={(props) => <List.Icon {...props} icon="account" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="通知设置"
            description="管理通知偏好"
            left={(props) => <List.Icon {...props} icon="bell" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="关于"
            description="小龙虾网络 v4.0"
            left={(props) => <List.Icon {...props} icon="information" />}
            onPress={() => {}}
          />
        </Card.Content>
      </Card>

      {/* 退出登录 */}
      <Button
        mode="outlined"
        onPress={handleLogout}
        style={styles.logoutButton}
        textColor="#ff4d4f"
      >
        退出登录
      </Button>
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
  card: {
    margin: 10,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    fontSize: 60,
    marginRight: 20,
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  userAddress: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
    fontFamily: 'monospace',
  },
  logoutButton: {
    margin: 20,
    borderColor: '#ff4d4f',
  },
});
/**
 * 登录页面
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert } from 'react-native';
import { createWallet } from '../services/api';
import * as SecureStore from 'expo-secure-store';

export default function LoginScreen({ navigation }) {
  const [nodeId, setNodeId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!nodeId.trim()) {
      Alert.alert('提示', '请输入节点 ID');
      return;
    }

    setLoading(true);
    try {
      // 创建钱包或获取现有钱包
      await createWallet({ node_id: nodeId });

      // 保存 token
      await SecureStore.setItemAsync('userToken', nodeId);

      navigation.replace('Main');
    } catch (error) {
      Alert.alert('错误', '登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>🦞</Text>
        <Text style={styles.title}>小龙虾网络</Text>
        <Text style={styles.subtitle}>因陀罗网 · 认知编译系统</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>节点 ID</Text>
        <TextInput
          style={styles.input}
          value={nodeId}
          onChangeText={setNodeId}
          placeholder="输入你的节点 ID"
          autoCapitalize="none"
          autoCorrect={false}
        />

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {loading ? '登录中...' : '进入网络'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.registerButton}
          onPress={() => {
            // 自动生成节点 ID
            const randomId = `lobster-${Math.random().toString(36).substr(2, 8)}`;
            setNodeId(randomId);
          }}
        >
          <Text style={styles.registerButtonText}>
            🎲 随机生成节点 ID
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          加入因陀罗网，与其他小龙虾一起创造新世界
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    alignItems: 'center',
    paddingTop: 80,
    paddingBottom: 40,
  },
  logo: {
    fontSize: 80,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1890ff',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  form: {
    padding: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#f9f9f9',
  },
  button: {
    backgroundColor: '#1890ff',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonDisabled: {
    backgroundColor: '#91d5ff',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  registerButton: {
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  registerButtonText: {
    color: '#1890ff',
    fontSize: 16,
  },
  footer: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});
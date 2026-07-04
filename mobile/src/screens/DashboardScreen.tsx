/**
 * 仪表盘页面
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Button, Chip } from 'react-native-paper';
import { getStats, getNodes, getTasks } from '../services/api';

export default function DashboardScreen({ navigation }) {
  const [stats, setStats] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

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
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>🦞 小龙虾网络</Text>
        <Text style={styles.subtitle}>仪表盘</Text>
      </View>

      {/* 统计卡片 */}
      <View style={styles.statsContainer}>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.total_nodes || 0}</Text>
          <Text style={styles.statLabel}>总节点数</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.active_nodes || 0}</Text>
          <Text style={styles.statLabel}>活跃节点</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.total_supply || 0} 🦞</Text>
          <Text style={styles.statLabel}>总供应量</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.blockchain_length || 0}</Text>
          <Text style={styles.statLabel}>区块链长度</Text>
        </Card>
      </View>

      {/* 快速操作 */}
      <Card style={styles.card}>
        <Card.Title title="快速操作" />
        <Card.Content>
          <View style={styles.buttonContainer}>
            <Button mode="contained" onPress={() => navigation.navigate('Wallet')} style={styles.button}>
              💰 钱包
            </Button>
            <Button mode="contained" onPress={() => navigation.navigate('Tasks')} style={styles.button}>
              📋 任务
            </Button>
            <Button mode="contained" onPress={() => navigation.navigate('Governance')} style={styles.button}>
              🏛️ 治理
            </Button>
            <Button mode="contained" onPress={() => navigation.navigate('Profile')} style={styles.button}>
              👤 我的
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* 节点列表 */}
      <Card style={styles.card}>
        <Card.Title title="活跃节点" />
        <Card.Content>
          {nodes.slice(0, 5).map((node) => (
            <View key={node.node_id} style={styles.nodeItem}>
              <Text style={styles.nodeName}>{node.name}</Text>
              <Chip style={styles.chip}>
                {node.type}
              </Chip>
              <Chip style={[styles.chip, styles.activeChip]}>
                活跃
              </Chip>
            </View>
          ))}
        </Card.Content>
      </Card>

      {/* 任务列表 */}
      <Card style={styles.card}>
        <Card.Title title="最近任务" />
        <Card.Content>
          {tasks.slice(0, 5).map((task) => (
            <View key={task.task_id} style={styles.taskItem}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <Text style={styles.taskReward}>{task.reward_amount} 🦞</Text>
            </View>
          ))}
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
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
  },
  statCard: {
    flex: 1,
    margin: 5,
    minWidth: 150,
    padding: 15,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1890ff',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  card: {
    margin: 10,
  },
  buttonContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  button: {
    flex: 1,
    minWidth: '45%',
    margin: 5,
  },
  nodeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  nodeName: {
    fontSize: 16,
    flex: 1,
  },
  chip: {
    marginLeft: 5,
  },
  activeChip: {
    backgroundColor: '#52c41a',
  },
  taskItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  taskTitle: {
    fontSize: 16,
    flex: 1,
  },
  taskReward: {
    fontSize: 14,
    color: '#faad14',
  },
});
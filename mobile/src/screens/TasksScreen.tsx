/**
 * 任务页面
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Card, Button, Chip, FAB } from 'react-native-paper';
import { getTasks, claimTask } from '../services/api';
import * as SecureStore from 'expo-secure-store';

export default function TasksScreen() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error) {
      console.error('加载任务失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (taskId) => {
    try {
      const nodeId = await SecureStore.getItemAsync('userToken');
      await claimTask(taskId, { node_id: nodeId });
      loadTasks();
    } catch (error) {
      console.error('领取任务失败:', error);
    }
  };

  const renderItem = ({ item }) => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Text style={styles.title}>{item.title}</Text>
          <Chip
            style={[
              styles.statusChip,
              item.status === 'pending' && styles.pendingChip,
              item.status === 'assigned' && styles.assignedChip,
              item.status === 'completed' && styles.completedChip,
            ]}
          >
            {item.status === 'pending' ? '待领取' :
             item.status === 'assigned' ? '进行中' : '已完成'}
          </Chip>
        </View>
        <Text style={styles.description}>{item.description}</Text>
        <View style={styles.cardFooter}>
          <Text style={styles.reward}>{item.reward_amount} 🦞</Text>
          {item.status === 'pending' && (
            <Button mode="contained" onPress={() => handleClaim(item.task_id)}>
              领取
            </Button>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📋 任务</Text>
      </View>

      <FlatList
        data={tasks}
        renderItem={renderItem}
        keyExtractor={(item) => item.task_id}
        contentContainerStyle={styles.list}
        refreshing={loading}
        onRefresh={loadTasks}
      />
    </View>
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
  list: {
    padding: 10,
  },
  card: {
    marginBottom: 10,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
  },
  statusChip: {
    marginLeft: 10,
  },
  pendingChip: {
    backgroundColor: '#f0f0f0',
  },
  assignedChip: {
    backgroundColor: '#e6f7ff',
  },
  completedChip: {
    backgroundColor: '#f6ffed',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  reward: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#faad14',
  },
});
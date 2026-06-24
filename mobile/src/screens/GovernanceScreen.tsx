/**
 * 治理页面
 */

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Card, Button, Chip } from 'react-native-paper';
import { getProposals, vote } from '../services/api';
import * as SecureStore from 'expo-secure-store';

export default function GovernanceScreen() {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    try {
      const data = await getProposals();
      setProposals(data);
    } catch (error) {
      console.error('加载提案失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (proposalId, option) => {
    try {
      const nodeId = await SecureStore.getItemAsync('userToken');
      await vote(proposalId, { voter_id: nodeId, option });
      loadProposals();
    } catch (error) {
      console.error('投票失败:', error);
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
              item.status === 'active' && styles.activeChip,
              item.status === 'passed' && styles.passedChip,
              item.status === 'rejected' && styles.rejectedChip,
            ]}
          >
            {item.status === 'active' ? '投票中' :
             item.status === 'passed' ? '已通过' : '已拒绝'}
          </Chip>
        </View>
        <Text style={styles.description}>{item.description}</Text>
        <View style={styles.votesContainer}>
          <Text style={styles.votesText}>
            赞成: {item.for_votes} 🦞
          </Text>
          <Text style={styles.votesText}>
            反对: {item.against_votes} 🦞
          </Text>
        </View>
        {item.status === 'active' && (
          <View style={styles.voteButtons}>
            <Button
              mode="contained"
              onPress={() => handleVote(item.proposal_id, 'for')}
              style={styles.voteButton}
            >
              赞成
            </Button>
            <Button
              mode="outlined"
              onPress={() => handleVote(item.proposal_id, 'against')}
              style={styles.voteButton}
            >
              反对
            </Button>
          </View>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🏛️ 治理</Text>
      </View>

      <FlatList
        data={proposals}
        renderItem={renderItem}
        keyExtractor={(item) => item.proposal_id}
        contentContainerStyle={styles.list}
        refreshing={loading}
        onRefresh={loadProposals}
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
  activeChip: {
    backgroundColor: '#e6f7ff',
  },
  passedChip: {
    backgroundColor: '#f6ffed',
  },
  rejectedChip: {
    backgroundColor: '#fff1f0',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  votesContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  votesText: {
    fontSize: 14,
    color: '#333',
  },
  voteButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  voteButton: {
    flex: 1,
    marginHorizontal: 5,
  },
});
/**
 * 主标签导航
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import DashboardScreen from './DashboardScreen';
import WalletScreen from './WalletScreen';
import TasksScreen from './TasksScreen';
import GovernanceScreen from './GovernanceScreen';
import ProfileScreen from './ProfileScreen';

// 简单的标签导航实现（不依赖 @react-navigation/bottom-tabs）
export default function MainTabs() {
  return (
    <View style={styles.container}>
      <DashboardScreen />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

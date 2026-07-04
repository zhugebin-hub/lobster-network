/**
 * 小龙虾网络移动端 - 主应用
 */

import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as SecureStore from 'expo-secure-store';
import { ActivityIndicator, View, StyleSheet } from 'react-native';

// 页面
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import WalletScreen from './screens/WalletScreen';
import TasksScreen from './screens/TasksScreen';
import GovernanceScreen from './screens/GovernanceScreen';
import ProfileScreen from './screens/ProfileScreen';

// 服务
import api from './services/api';
import { registerForPushNotifications } from './services/notification';

const Stack = createNativeStackNavigator();
const queryClient = new QueryClient();

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState(null);

  useEffect(() => {
    // 检查登录状态
    const checkLogin = async () => {
      try {
        const token = await SecureStore.getItemAsync('userToken');
        setUserToken(token);

        // 注册推送通知
        if (token) {
          await registerForPushNotifications();
        }
      } catch (error) {
        console.error('检查登录状态失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkLogin();
  }, []);

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1890ff" />
      </View>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <NavigationContainer>
          <StatusBar style="auto" />
          <Stack.Navigator
            screenOptions={{ headerShown: false }}
            initialRouteName={userToken ? 'Main' : 'Login'}
          >
            {!userToken && (
              <Stack.Screen name="Login" component={LoginScreen} />
            )}
            <Stack.Screen name="Main" component={MainTabs} />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});
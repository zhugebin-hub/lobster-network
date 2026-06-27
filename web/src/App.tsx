/**
 * 小龙虾网络 Web 管理界面 - 主应用
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

// 页面
import Dashboard from './pages/Dashboard';
import Nodes from './pages/Nodes';
import Tasks from './pages/Tasks';
import Governance from './pages/Governance';
import Wallet from './pages/Wallet';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/nodes" element={<Nodes />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/governance" element={<Governance />} />
          <Route path="/wallet" element={<Wallet />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
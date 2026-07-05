/**
 * 暗色主题支持
 */

import { theme } from 'antd';

// 亮色主题
export const lightTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorBgContainer: '#fff',
    colorBgElevated: '#fff',
    colorBorder: '#d9d9d9',
    colorText: 'rgba(0, 0, 0, 0.85)',
    colorTextSecondary: 'rgba(0, 0, 0, 0.65)',
  },
};

// 暗色主题
export const darkTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#177dd0',
    colorBgContainer: '#141414',
    colorBgElevated: '#1f1f1f',
    colorBorder: '#303030',
    colorText: 'rgba(255, 255, 255, 0.85)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
  },
};
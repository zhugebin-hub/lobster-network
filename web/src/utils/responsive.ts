/**
 * 响应式设计支持
 */

import { useEffect, useState } from 'react';

// 断点定义
export const breakpoints = {
  xs: 480,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600,
};

// 使用断点 Hook
export const useBreakpoint = () => {
  const [screenSize, setScreenSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    ...screenSize,
    isMobile: screenSize.width < breakpoints.md,
    isTablet: screenSize.width >= breakpoints.md && screenSize.width < breakpoints.lg,
    isDesktop: screenSize.width >= breakpoints.lg,
    isLargeDesktop: screenSize.width >= breakpoints.xl,
  };
};

// 响应式样式工具
export const responsiveStyle = {
  // 列响应式
  col: (xs?: number, sm?: number, md?: number, lg?: number, xl?: number, xxl?: number) => ({
    xs,
    sm,
    md,
    lg,
    xl,
    xxl,
  }),

  // 间距响应式
  margin: (xs: number, sm?: number, md?: number, lg?: number) => ({
    margin: xs,
    [`@media (min-width: ${breakpoints.sm}px)`]: sm ? { margin: sm } : undefined,
    [`@media (min-width: ${breakpoints.md}px)`]: md ? { margin: md } : undefined,
    [`@media (min-width: ${breakpoints.lg}px)`]: lg ? { margin: lg } : undefined,
  }),

  // 字体响应式
  fontSize: (xs: number, sm?: number, md?: number, lg?: number) => ({
    fontSize: xs,
    [`@media (min-width: ${breakpoints.sm}px)`]: sm ? { fontSize: sm } : undefined,
    [`@media (min-width: ${breakpoints.md}px)`]: md ? { fontSize: md } : undefined,
    [`@media (min-width: ${breakpoints.lg}px)`]: lg ? { fontSize: lg } : undefined,
  }),
};
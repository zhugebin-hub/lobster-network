#!/usr/bin/env python3
"""
技术指标计算器

提供常用技术分析指标的计算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int = 5) -> pd.Series:
        """计算移动平均线"""
        return df['close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 12) -> pd.Series:
        """计算指数移动平均线"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> Dict:
        """
        计算MACD指标
        
        Returns:
            dict with 'macd', 'signal', 'histogram' series
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算RSI相对强弱指标"""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, 
                                 num_std: float = 2.0) -> Dict:
        """
        计算布林带
        
        Returns:
            dict with 'upper', 'middle', 'lower' series
        """
        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    @staticmethod
    def calculate_volume_ma(df: pd.DataFrame, period: int = 5) -> pd.Series:
        """计算成交量均线"""
        return df['volume'].rolling(window=period).mean()
    
    @staticmethod
    def detect_pattern(df: pd.DataFrame) -> List[str]:
        """
        检测K线形态
        
        Returns:
            list of detected patterns
        """
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        # 简单形态检测示例
        last_3 = df.tail(3)
        
        # 三连阳
        if all(last_3['close'] > last_3['open']):
            patterns.append('三连阳')
        
        # 三连阴
        if all(last_3['close'] < last_3['open']):
            patterns.append('三连阴')
        
        # 十字星（实体很小）
        last_row = df.iloc[-1]
        body = abs(last_row['close'] - last_row['open'])
        range_val = last_row['high'] - last_row['low']
        if range_val > 0 and body / range_val < 0.1:
            patterns.append('十字星')
        
        return patterns


def load_stock_data(csv_file: str) -> pd.DataFrame:
    """加载股票CSV数据"""
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 转换数值列
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 删除空值行
    df = df.dropna(subset=['close'])
    
    return df


def analyze_stock(csv_file: str) -> Dict:
    """
    对单只股票进行完整技术分析
    
    Args:
        csv_file: CSV文件路径
        
    Returns:
        分析结果字典
    """
    print(f"\n📊 正在分析: {csv_file}")
    print("="*60)
    
    # 加载数据
    df = load_stock_data(csv_file)
    print(f"数据条数: {len(df)}")
    print(f"时间范围: {df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}")
    
    # 计算技术指标
    indicators = TechnicalIndicators()
    
    # MA均线
    df['ma5'] = indicators.calculate_ma(df, 5)
    df['ma10'] = indicators.calculate_ma(df, 10)
    df['ma20'] = indicators.calculate_ma(df, 20)
    
    # MACD
    macd_data = indicators.calculate_macd(df)
    df['macd'] = macd_data['macd']
    df['macd_signal'] = macd_data['signal']
    df['macd_hist'] = macd_data['histogram']
    
    # RSI
    df['rsi'] = indicators.calculate_rsi(df)
    
    # 布林带
    bb_data = indicators.calculate_bollinger_bands(df)
    df['bb_upper'] = bb_data['upper']
    df['bb_middle'] = bb_data['middle']
    df['bb_lower'] = bb_data['lower']
    
    # 成交量均线
    df['vol_ma5'] = indicators.calculate_volume_ma(df, 5)
    
    # K线形态检测
    patterns = indicators.detect_pattern(df)
    
    # 最新数据分析
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    
    analysis = {
        'stock_file': csv_file,
        'data_points': len(df),
        'latest_date': latest['date'].strftime('%Y-%m-%d'),
        'latest_price': {
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'close': float(latest['close']),
            'volume': int(latest['volume'])
        },
        'moving_averages': {
            'ma5': float(latest['ma5']) if not pd.isna(latest['ma5']) else None,
            'ma10': float(latest['ma10']) if not pd.isna(latest['ma10']) else None,
            'ma20': float(latest['ma20']) if not pd.isna(latest['ma20']) else None,
        },
        'macd': {
            'macd': float(latest['macd']) if not pd.isna(latest['macd']) else None,
            'signal': float(latest['macd_signal']) if not pd.isna(latest['macd_signal']) else None,
            'histogram': float(latest['macd_hist']) if not pd.isna(latest['macd_hist']) else None,
        },
        'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else None,
        'bollinger_bands': {
            'upper': float(latest['bb_upper']) if not pd.isna(latest['bb_upper']) else None,
            'middle': float(latest['bb_middle']) if not pd.isna(latest['bb_middle']) else None,
            'lower': float(latest['bb_lower']) if not pd.isna(latest['bb_lower']) else None,
        },
        'patterns_detected': patterns,
        'price_change': {
            'daily': ((latest['close'] - prev['close']) / prev['close'] * 100) if prev is not None else None,
        }
    }
    
    # 打印摘要
    print(f"\n最新价格: ¥{analysis['latest_price']['close']:.2f}")
    if analysis['price_change']['daily'] is not None:
        change = analysis['price_change']['daily']
        symbol = "↑" if change > 0 else "↓"
        print(f"日涨跌幅: {symbol} {abs(change):.2f}%")
    
    print(f"MA5: {analysis['moving_averages']['ma5']:.2f}" if analysis['moving_averages']['ma5'] else "MA5: N/A")
    print(f"RSI: {analysis['rsi']:.2f}" if analysis['rsi'] else "RSI: N/A")
    
    if patterns:
        print(f"检测到形态: {', '.join(patterns)}")
    
    print("="*60)
    
    return analysis


if __name__ == '__main__':
    import os
    from pathlib import Path
    
    # 分析三只股票
    data_dir = Path(__file__).parent.parent / 'domains' / 'stock_prediction' / 'data'
    csv_files = [
        data_dir / '600519_贵州茅台.csv',
        data_dir / '000858_五粮液.csv',
        data_dir / '600036_招商银行.csv',
    ]
    
    results = []
    for csv_file in csv_files:
        if csv_file.exists():
            result = analyze_stock(str(csv_file))
            results.append(result)
        else:
            print(f"⚠️  文件不存在: {csv_file}")
    
    print(f"\n✅ 完成 {len(results)} 只股票的技术分析")

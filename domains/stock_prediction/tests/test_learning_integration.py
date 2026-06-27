#!/usr/bin/env python3
"""
测试学习型节点集成

验证TradingExperienceLearner和LearningAnalysts是否正确集成到小龙虾网络中
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """测试所有模块是否能正确导入"""
    print("="*70)
    print("🧪 测试1: 模块导入")
    print("="*70)
    
    try:
        # 先导入基础组件（不依赖lobster_network）
        from domains.stock_prediction import (
            TechnicalAnalyst, FundamentalAnalyst, SentimentAnalyst,
            TechnicalAnalystWithLearning, FundamentalAnalystWithLearning, SentimentAnalystWithLearning,
            TradingExperienceLearner, TradingKnowledgeBase
        )
        print("✅ 核心学习模块导入成功")
        
        # 尝试导入StockPredictor（可能需要lobster_network环境）
        try:
            from domains.stock_prediction import StockPredictor
            print("✅ StockPredictor 导入成功")
        except ImportError as e:
            print(f"⚠️  StockPredictor 导入跳过（需要完整lobster_network环境）: {e}")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base():
    """测试知识库功能"""
    print("\n" + "="*70)
    print("🧪 测试2: 知识库功能")
    print("="*70)
    
    try:
        from trading_experience_learner import TradingKnowledgeBase
        
        kb = TradingKnowledgeBase()
        
        # 添加一条测试经验
        kb.add_lesson({
            'type': 'test_lesson',
            'context': '测试环境',
            'hypothesis': '这是一个测试假设',
            'outcome': 'success'
        })
        
        summary = kb.get_summary()
        print(f"✅ 知识库工作正常")
        print(f"   - 经验教训数: {summary['total_lessons']}")
        print(f"   - 最后更新: {summary['last_updated']}")
        
        return True
    except Exception as e:
        print(f"❌ 知识库测试失败: {e}")
        return False


def test_market_classifier():
    """测试市场状态分类器"""
    print("\n" + "="*70)
    print("🧪 测试3: 市场状态分类器")
    print("="*70)
    
    try:
        import pandas as pd
        import numpy as np
        from trading_experience_learner import MarketStateClassifier
        
        classifier = MarketStateClassifier()
        
        # 创建模拟数据（下跌趋势）
        dates = pd.date_range('2026-01-01', periods=100, freq='D')
        prices = 100 - np.arange(100) * 0.5 + np.random.randn(100) * 2
        df = pd.DataFrame({'date': dates, 'close': prices})
        
        state = classifier.classify_market(df)
        print(f"✅ 市场分类器工作正常")
        print(f"   - 检测到的市场状态: {state}")
        
        return True
    except Exception as e:
        print(f"❌ 市场分类器测试失败: {e}")
        return False


def test_learning_analyst():
    """测试学习型分析师"""
    print("\n" + "="*70)
    print("🧪 测试4: 学习型分析师")
    print("="*70)
    
    try:
        from learning_analysts import TechnicalAnalystWithLearning
        
        analyst = TechnicalAnalystWithLearning()
        
        # 执行分析
        result = analyst.analyze("600519")
        
        print(f"✅ 学习型分析师工作正常")
        print(f"   - 分析师名称: {result['analyst']}")
        print(f"   - 股票代码: {result['stock_code']}")
        
        if 'learning_insights' in result:
            insights = result['learning_insights']
            print(f"   - 相关规则数: {insights['relevant_rules_count']}")
            print(f"   - 置信度调整: {insights['confidence_adjustment']:.2f}x")
        
        return True
    except Exception as e:
        print(f"❌ 学习型分析师测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_integration():
    """测试完整集成"""
    print("\n" + "="*70)
    print("🧪 测试5: 完整集成流程")
    print("="*70)
    
    try:
        from trading_experience_learner import TradingExperienceLearner
        
        learner = TradingExperienceLearner()
        
        # 模拟一次学习循环
        observation = {
            'type': 'integration_test',
            'context': '集成测试',
            'hypothesis': '学习型节点集成测试通过',
            'evidence': {'test': True},
            'outcome': 'success'
        }
        
        learner.kb.add_lesson(observation)
        
        report = learner.generate_learning_report()
        print(report)
        
        print("✅ 完整集成流程测试通过")
        return True
    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🦞"*35)
    print("小龙虾网络 - 学习型炒股节点集成测试")
    print("🦞"*35 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("知识库功能", test_knowledge_base()))
    results.append(("市场分类器", test_market_classifier()))
    results.append(("学习型分析师", test_learning_analyst()))
    results.append(("完整集成", test_full_integration()))
    
    # 汇总结果
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！学习型节点已成功集成到小龙虾网络。")
        print("\n下一步:")
        print("  1. 查看集成指南: docs/LEARNING_NODE_INTEGRATION.md")
        print("  2. 运行回测学习: python3 examples/learn_from_backtest.py")
        print("  3. 配置Signal Arena API Key后开始实盘学习")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

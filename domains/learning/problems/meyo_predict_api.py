"""
🦞 小龙虾网络 · 觅游足球预测API集成
支持：拉取赛事、提交预测、查看记录、排行榜
"""

import json
import os
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class MeYouPredictAPI:
    """觅游足球预测API集成"""
    
    def __init__(self, api_key: str = None, credential_file: str = None):
        """
        初始化API
        
        Args:
            api_key: API密钥
            credential_file: 凭证文件路径
        """
        self.api_key = api_key
        self.credential_file = credential_file or os.path.expanduser('~/.meyo/credentials.json')
        self.base_url = 'https://www.meyo123.com/api/v1'
        
        # 从凭证文件加载API Key
        if not self.api_key and os.path.exists(self.credential_file):
            with open(self.credential_file, 'r') as f:
                creds = json.load(f)
                self.api_key = creds.get('api_key')
                
    def _get_headers(self, trigger_source: str = 'human-order', 
                    trigger_reason: str = '诸葛斌要求获取足球预测数据') -> Dict:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-Skill-Version': '1.7.0',
            'X-Trigger-Source': trigger_source,
            'X-Trigger-Reason': trigger_reason,
            'Content-Type': 'application/json'
        }
    
    def get_open_markets(self, page_size: int = 20) -> List[Dict]:
        """
        获取可预测的赛事
        
        Returns:
            赛事列表
        """
        url = f'{self.base_url}/predictions/markets'
        params = {
            'category': 'footballforecast',
            'status': 'open',
            'pageSize': page_size
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"❌ 获取赛事失败: {response.status_code} {response.text}")
            return []
    
    def get_my_records(self) -> List[Dict]:
        """
        查看我的预测记录
        
        Returns:
            预测记录列表
        """
        url = f'{self.base_url}/predictions/my/records'
        params = {'category': 'footballforecast'}
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"❌ 获取记录失败: {response.status_code} {response.text}")
            return []
    
    def get_leaderboard(self, sort: str = 'total_score', 
                       page_size: int = 20) -> List[Dict]:
        """
        查看排行榜
        
        Args:
            sort: 排序方式（total_score/accuracy/participation）
            page_size: 每页数量
            
        Returns:
            排行榜列表
        """
        url = f'{self.base_url}/predictions/leaderboard'
        params = {
            'category': 'footballforecast',
            'sort': sort,
            'pageSize': page_size
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"❌ 获取排行榜失败: {response.status_code} {response.text}")
            return []
    
    def submit_prediction(self, market_id: str, option_name: str, 
                         reasoning: str) -> Dict:
        """
        提交预测
        
        Args:
            market_id: 赛事ID
            option_name: 选项名称
            reasoning: 预测理由
            
        Returns:
            提交结果
        """
        url = f'{self.base_url}/predictions/markets/{market_id}/predict'
        data = {
            'option_name': option_name,
            'reasoning': reasoning
        }
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 提交预测失败: {response.status_code} {response.text}")
            return {}
    
    def recommend_matches(self, engine, limit: int = 3) -> List[Dict]:
        """
        基于引擎推荐比赛
        
        Args:
            engine: 预测引擎
            limit: 推荐数量
            
        Returns:
            推荐列表
        """
        markets = self.get_open_markets()
        recommendations = []
        
        for market in markets[:10]:  # 检查前10场
            if len(recommendations) >= limit:
                break
                
            home_team = market.get('ff_match', {}).get('home_team', '')
            away_team = market.get('ff_match', {}).get('away_team', '')
            match_type = market.get('ff_match', {}).get('type', '')
            
            # 根据类型调用引擎预测
            if match_type == 'win_lose_draw':
                result = engine.predict_match_result(home_team, away_team)
                if result['confidence'] >= 0.65:
                    recommendations.append({
                        'market_id': market['id'],
                        'title': market['title'],
                        'match': f"{home_team} vs {away_team}",
                        'type': '胜平负',
                        'recommendation': result['prediction'],
                        'confidence': result['confidence'],
                        'reasoning': f"引擎预测置信度{result['confidence']:.1%}",
                        'close_time': market.get('close_time', ''),
                        'url': f"https://www.meyo123.com/community/activities/footballforecast/markets/{market['id']}"
                    })
            elif match_type == 'score':
                score = engine.predict_score(home_team, away_team)
                if score['confidence'] >= 0.10:
                    recommendations.append({
                        'market_id': market['id'],
                        'title': market['title'],
                        'match': f"{home_team} vs {away_team}",
                        'type': '比分',
                        'recommendation': score['predicted_score'],
                        'confidence': score['confidence'],
                        'reasoning': f"泊松分布预测，最可能比分",
                        'close_time': market.get('close_time', ''),
                        'url': f"https://www.meyo123.com/community/activities/footballforecast/markets/{market['id']}"
                    })
            elif match_type == 'total_goals':
                total = engine.predict_total_goals(home_team, away_team)
                if total['confidence'] >= 0.35:
                    recommendations.append({
                        'market_id': market['id'],
                        'title': market['title'],
                        'match': f"{home_team} vs {away_team}",
                        'type': '总进球数',
                        'recommendation': total['prediction'],
                        'confidence': total['confidence'],
                        'reasoning': f"期望总进球{total['expected_total']:.1f}个",
                        'close_time': market.get('close_time', ''),
                        'url': f"https://www.meyo123.com/community/activities/footballforecast/markets/{market['id']}"
                    })
                    
        return recommendations


# 演示
if __name__ == '__main__':
    from football_predict_engine import FootballPredictEngine
    
    print("=" * 50)
    print("🦞 小龙虾网络 · 觅游足球预测API集成")
    print("=" * 50)
    
    # 初始化
    api = MeYouPredictAPI()
    engine = FootballPredictEngine()
    
    # 1. 获取可预测赛事
    print("\n📊 获取可预测赛事:")
    markets = api.get_open_markets()
    print(f"   当前开放赛事: {len(markets)} 场")
    
    for market in markets[:5]:
        home = market.get('ff_match', {}).get('home_team', '')
        away = market.get('ff_match', {}).get('away_team', '')
        print(f"   - {home} vs {away}")
        
    # 2. 推荐比赛
    print("\n🎯 引擎推荐:")
    recommendations = api.recommend_matches(engine, limit=3)
    
    for rec in recommendations:
        print(f"\n   📌 {rec['title']}")
        print(f"      对阵：{rec['match']}")
        print(f"      类型：{rec['type']}")
        print(f"      推荐：{rec['recommendation']}")
        print(f"      置信度：{rec['confidence']:.1%}")
        print(f"      理由：{rec['reasoning']}")
        print(f"      链接：{rec['url']}")
        
    # 3. 查看排行榜
    print("\n🏆 排行榜:")
    leaderboard = api.get_leaderboard()
    
    for i, agent in enumerate(leaderboard[:5], 1):
        print(f"   {i}. {agent.get('nickname', 'N/A')} - 总分{agent.get('total_score', 0):.1f}")
        
    print("\n" + "=" * 50)
    print("✅ 觅游API集成测试完成！")

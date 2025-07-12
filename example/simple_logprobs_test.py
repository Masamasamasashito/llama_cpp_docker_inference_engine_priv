#!/usr/bin/env python3
"""
修正版: get_top_response_tokens テスト - 挙動の違いを解決
"""

import math
import requests
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    token: str
    prob: float
    top_candidates: Optional[List['Token']] = None

def get_top_response_tokens_from_llama_cpp(prompt: str = "The capital of Japan is", max_tokens: int = 100, temperature: float = 0.7) -> List[Token]:
    """llama.cppから直接logprobsを取得してToken形式に変換"""
    
    print(f"🔄 プロンプト: '{prompt}' (max_tokens={max_tokens}, temp={temperature})")
    
    # llama.cpp Chat APIリクエスト（設定を柔軟に）
    payload = {
        "model": "llama",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "logprobs": True,
        "top_logprobs": 3
    }
    
    try:
        response = requests.post(
            "http://localhost:8081/v1/chat/completions",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # 生成テキスト表示
        content = data['choices'][0]['message']['content']
        print(f"📝 生成結果: '{content}'")
        print(f"📊 トークン数: {data['usage']['completion_tokens']}")
        
        # logprobsからToken形式に変換
        logprobs_data = data['choices'][0]['logprobs']['content']
        tokens = []
        
        for token_data in logprobs_data:
            # メイントークン
            main_prob = math.exp(token_data['logprob'])
            
            # 上位候補
            candidates = []
            for candidate in token_data.get('top_logprobs', []):
                cand_prob = math.exp(candidate['logprob'])
                candidates.append(Token(candidate['token'], cand_prob))
            
            # Tokenオブジェクト作成
            token = Token(
                token=token_data['token'],
                prob=main_prob,
                top_candidates=candidates
            )
            tokens.append(token)
        
        return tokens
        
    except Exception as e:
        print(f"❌ Chat API エラー: {e}")
        return []

def get_completion_tokens(prompt: str = "The capital of Japan is", n_predict: int = 100, temperature: float = 0.7) -> List[Token]:
    """Completion APIでlogprobsを取得"""
    
    print(f"🔄 Completion API: '{prompt}' (n_predict={n_predict}, temp={temperature})")
    
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "n_probs": 3  # Completion APIのlogprobs
    }
    
    try:
        response = requests.post(
            "http://localhost:8081/completion",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # 生成テキスト表示
        content = data.get('content', '')
        print(f"📝 生成結果: '{content}'")
        print(f"📊 トークン数: {data.get('tokens_predicted', 0)}")
        
        # Completion APIのlogprobs処理
        completion_probs = data.get('completion_probabilities', [])
        tokens = []
        
        for token_data in completion_probs:
            # メイントークン
            main_prob = math.exp(token_data['logprob'])
            
            # 上位候補
            candidates = []
            for candidate in token_data.get('top_logprobs', []):
                cand_prob = math.exp(candidate['logprob'])
                candidates.append(Token(candidate['token'], cand_prob))
            
            # Tokenオブジェクト作成
            token = Token(
                token=token_data['token'],
                prob=main_prob,
                top_candidates=candidates
            )
            tokens.append(token)
        
        return tokens
        
    except Exception as e:
        print(f"❌ Completion API エラー: {e}")
        return []

def display_tokens(tokens: List[Token]):
    """Token情報を見やすく表示"""
    
    if not tokens:
        print("⚠️  トークンデータがありません")
        return
    
    print(f"\n📊 トークン分析結果 ({len(tokens)}個)")
    print("=" * 50)
    
    for i, token in enumerate(tokens):
        print(f"\n🎯 トークン {i+1}: {repr(token.token)}")
        print(f"   確率: {token.prob:.4f} ({token.prob*100:.2f}%)")
        
        if token.top_candidates:
            print(f"   上位候補:")
            for j, candidate in enumerate(token.top_candidates):
                print(f"     {j+1}位: {repr(candidate.token)} - {candidate.prob:.4f} ({candidate.prob*100:.2f}%)")

def compare_chat_vs_completion(prompt: str, max_tokens: int = 50, temperature: float = 0.7):
    """Chat API vs Completion APIの直接比較"""
    
    print(f"\n🆚 API比較テスト: '{prompt}'")
    print(f"設定: max_tokens={max_tokens}, temperature={temperature}")
    print("=" * 60)
    
    # Chat API
    print("📱 Chat API:")
    chat_tokens = get_top_response_tokens_from_llama_cpp(prompt, max_tokens, temperature)
    if chat_tokens:
        # 最初の5トークンのみ表示（スペース節約）
        display_tokens(chat_tokens[:5])
    
    print("\n" + "-" * 30)
    
    # Completion API
    print("📝 Completion API:")
    completion_tokens = get_completion_tokens(prompt, max_tokens, temperature)
    if completion_tokens:
        # 最初の5トークンのみ表示
        display_tokens(completion_tokens[:5])
    
    print("\n" + "=" * 60)

def test_various_prompts():
    """複数のプロンプトでテスト - 設定を統一"""
    
    test_prompts = [
        "The capital of Japan is",
        "1 + 1 =", 
        "Hello, my name is",
        "今日の天気は"
    ]
    
    # 設定を統一して比較
    MAX_TOKENS = 20  # 短めに設定
    TEMPERATURE = 0.7
    
    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"統一設定テスト: {prompt}")
        print(f"{'='*60}")
        
        # Chat APIでテスト
        print("📱 Chat API (統一設定):")
        tokens = get_top_response_tokens_from_llama_cpp(prompt, MAX_TOKENS, TEMPERATURE)
        if tokens:
            display_tokens(tokens[:3])  # 最初の3トークンのみ
            
            # 最高確率トークンの信頼度チェック
            max_prob = max(token.prob for token in tokens[:3])
            if max_prob > 0.8:
                print(f"\n✅ 高信頼度予測 (最大確率: {max_prob:.3f})")
            elif max_prob > 0.5:
                print(f"\n⚡ 中程度信頼度 (最大確率: {max_prob:.3f})")
            else:
                print(f"\n⚠️  低信頼度予測 (最大確率: {max_prob:.3f})")
        else:
            print("❌ トークン取得失敗")

def analyze_behavior_differences():
    """挙動の違いを詳細分析"""
    
    print(f"\n🔍 挙動の違い詳細分析")
    print("=" * 60)
    
    test_prompt = "今日の天気は"
    
    # 1. 短い生成での比較
    print("🔬 テスト1: 短い生成 (5トークン)")
    compare_chat_vs_completion(test_prompt, max_tokens=5, temperature=0.7)
    
    # 2. 長い生成での比較
    print("🔬 テスト2: 長い生成 (50トークン)")
    compare_chat_vs_completion(test_prompt, max_tokens=50, temperature=0.7)
    
    # 3. 低温度での比較
    print("🔬 テスト3: 低温度 (確定的)")
    compare_chat_vs_completion(test_prompt, max_tokens=20, temperature=0.1)

if __name__ == "__main__":
    print("🚀 修正版: get_top_response_tokens テスト")
    print("🎯 目的: Chat API vs Completion API の挙動の違いを解明")
    
    # サーバー確認
    try:
        health = requests.get("http://localhost:8081/health", timeout=5)
        if health.status_code != 200:
            print(f"❌ サーバーエラー: {health.text}")
            exit(1)
        print("✅ llama.cpp サーバー接続OK\n")
    except Exception as e:
        print(f"❌ サーバー接続失敗: {e}")
        exit(1)
    
    # 基本テスト（元の設定で）
    print("📋 基本テスト（長い生成）")
    tokens = get_top_response_tokens_from_llama_cpp("The capital of Japan is", 100, 0.7)
    if tokens:
        display_tokens(tokens[:5])  # 最初の5トークンのみ
    
    # 挙動の違いを分析
    analyze_behavior_differences()
    
    # 統一設定でのテスト
    print(f"\n📋 統一設定での複数プロンプトテスト")
    test_various_prompts()
    
    print(f"\n🏁 テスト完了！")
    print("💡 結論: APIの種類と設定によって応答が変わることを確認")

#!/usr/bin/env python3
"""
Chat API vs Completion API の logprobs（トークン確率）比較テスト

目的: 両APIのlogprobs取得方法と挙動の違いを検証する
使い方:
  python example/test_request_logprobs.py
  LDIE_BASE_URL=http://192.168.1.100:8081 LDIE_API_KEY=sk-local-xxx python example/test_request_logprobs.py
"""

import math
import os
import requests
from dataclasses import dataclass
from typing import List, Optional

# ---------------------------------------------------------------------------
# Configuration (環境変数 or デフォルト値)
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("LDIE_BASE_URL", "http://localhost:8081")
API_KEY = os.environ.get("LDIE_API_KEY", "")

HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"

# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------
@dataclass
class Token:
    token: str
    prob: float
    top_candidates: Optional[List['Token']] = None

# ---------------------------------------------------------------------------
# Chat API (OpenAI Compatible)
# ---------------------------------------------------------------------------
def get_chat_tokens(prompt: str = "The capital of Japan is", max_tokens: int = 100, temperature: float = 0.7) -> List[Token]:
    """Chat API (/v1/chat/completions) でlogprobsを取得"""

    print(f"  prompt: '{prompt}' (max_tokens={max_tokens}, temp={temperature})")

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "logprobs": True,
        "top_logprobs": 3
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        content = data['choices'][0]['message']['content']
        print(f"  result: '{content}'")
        print(f"  tokens: {data['usage']['completion_tokens']}")

        logprobs_data = data['choices'][0]['logprobs']['content']
        tokens = []

        for token_data in logprobs_data:
            main_prob = math.exp(token_data['logprob'])
            candidates = []
            for candidate in token_data.get('top_logprobs', []):
                cand_prob = math.exp(candidate['logprob'])
                candidates.append(Token(candidate['token'], cand_prob))

            token = Token(
                token=token_data['token'],
                prob=main_prob,
                top_candidates=candidates
            )
            tokens.append(token)

        return tokens

    except Exception as e:
        print(f"  [ERROR] Chat API: {e}")
        return []

# ---------------------------------------------------------------------------
# Completion API (llama.cpp native)
# ---------------------------------------------------------------------------
def get_completion_tokens(prompt: str = "The capital of Japan is", n_predict: int = 100, temperature: float = 0.7) -> List[Token]:
    """Completion API (/completion) でlogprobsを取得"""

    print(f"  prompt: '{prompt}' (n_predict={n_predict}, temp={temperature})")

    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "n_probs": 3
    }

    try:
        response = requests.post(
            f"{BASE_URL}/completion",
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        content = data.get('content', '')
        print(f"  result: '{content}'")
        print(f"  tokens: {data.get('tokens_predicted', 0)}")

        completion_probs = data.get('completion_probabilities', [])
        tokens = []

        for token_data in completion_probs:
            main_prob = math.exp(token_data['logprob'])
            candidates = []
            for candidate in token_data.get('top_logprobs', []):
                cand_prob = math.exp(candidate['logprob'])
                candidates.append(Token(candidate['token'], cand_prob))

            token = Token(
                token=token_data['token'],
                prob=main_prob,
                top_candidates=candidates
            )
            tokens.append(token)

        return tokens

    except Exception as e:
        print(f"  [ERROR] Completion API: {e}")
        return []

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display_tokens(tokens: List[Token]):
    """Token情報を見やすく表示"""

    if not tokens:
        print("  (no token data)")
        return

    print(f"\n  Token Analysis ({len(tokens)} tokens)")
    print("  " + "=" * 48)

    for i, token in enumerate(tokens):
        print(f"\n  [{i+1}] {repr(token.token)}")
        print(f"      prob: {token.prob:.4f} ({token.prob*100:.2f}%)")

        if token.top_candidates:
            print(f"      top candidates:")
            for j, candidate in enumerate(token.top_candidates):
                print(f"        {j+1}: {repr(candidate.token)} - {candidate.prob:.4f} ({candidate.prob*100:.2f}%)")

# ---------------------------------------------------------------------------
# Test: Chat API vs Completion API comparison
# ---------------------------------------------------------------------------
def compare_chat_vs_completion(prompt: str, max_tokens: int = 50, temperature: float = 0.7):
    """Chat API vs Completion API の直接比較"""

    print(f"\n--- Compare: '{prompt}' (max_tokens={max_tokens}, temp={temperature}) ---")

    print("\n[Chat API]")
    chat_tokens = get_chat_tokens(prompt, max_tokens, temperature)
    if chat_tokens:
        display_tokens(chat_tokens[:5])

    print("\n[Completion API]")
    completion_tokens = get_completion_tokens(prompt, max_tokens, temperature)
    if completion_tokens:
        display_tokens(completion_tokens[:5])

# ---------------------------------------------------------------------------
# Test: Multiple prompts
# ---------------------------------------------------------------------------
def test_various_prompts():
    """複数のプロンプトでテスト"""

    test_prompts = [
        "The capital of Japan is",
        "1 + 1 =",
        "Hello, my name is",
    ]

    MAX_TOKENS = 20
    TEMPERATURE = 0.7

    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print(f"{'='*60}")

        tokens = get_chat_tokens(prompt, MAX_TOKENS, TEMPERATURE)
        if tokens:
            display_tokens(tokens[:3])

            max_prob = max(token.prob for token in tokens[:3])
            if max_prob > 0.8:
                print(f"\n  -> High confidence (max prob: {max_prob:.3f})")
            elif max_prob > 0.5:
                print(f"\n  -> Medium confidence (max prob: {max_prob:.3f})")
            else:
                print(f"\n  -> Low confidence (max prob: {max_prob:.3f})")
        else:
            print("  [FAILED]")

# ---------------------------------------------------------------------------
# Test: Behavior differences
# ---------------------------------------------------------------------------
def analyze_behavior_differences():
    """挙動の違いを詳細分析"""

    print(f"\n{'='*60}")
    print("Behavior Difference Analysis")
    print(f"{'='*60}")

    test_prompt = "The capital of Japan is"

    print("\n[Test 1] Short generation (5 tokens)")
    compare_chat_vs_completion(test_prompt, max_tokens=5, temperature=0.7)

    print("\n[Test 2] Long generation (50 tokens)")
    compare_chat_vs_completion(test_prompt, max_tokens=50, temperature=0.7)

    print("\n[Test 3] Low temperature (deterministic)")
    compare_chat_vs_completion(test_prompt, max_tokens=20, temperature=0.1)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("LDIE - Logprobs Test: Chat API vs Completion API")
    print(f"Server: {BASE_URL}")
    print(f"API Key: {'set' if API_KEY else 'not set'}")
    print("=" * 60)

    # Health check
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"[ERROR] Server: {health.text}")
            exit(1)
        print("[OK] Server connected\n")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        exit(1)

    # Basic test
    print("[Basic Test] Long generation")
    tokens = get_chat_tokens("The capital of Japan is", 100, 0.7)
    if tokens:
        display_tokens(tokens[:5])

    # Behavior differences
    analyze_behavior_differences()

    # Multiple prompts
    print(f"\n[Multiple Prompts Test]")
    test_various_prompts()

    print(f"\n{'='*60}")
    print("Test complete.")
    print("=" * 60)

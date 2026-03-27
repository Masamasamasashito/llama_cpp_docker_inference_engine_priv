# 3. OpenClaw設定

OpenClawにWindows LDIEサーバーをローカルLLMプロバイダとして登録します。

---

## 3-1. openclaw.jsonの場所

```bash
ls ~/.openclaw/openclaw.json
```

> ファイルがない場合は `openclaw onboard` を先に実行してください。

## 3-2. 基本設定（単一モデル）

`~/.openclaw/openclaw.json` を編集します。

```bash
nano ~/.openclaw/openclaw.json
```

以下の内容に書き換えてください（IPアドレス・API Key・モデル名は実際の値に）:

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ldie/gemma-3-27b-it-Q4_K_M"
      }
    }
  },
  "models": {
    "providers": {
      "ldie": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local-your-secret-key-here",
        "api": "openai-completions",
        "models": [
          {
            "id": "gemma-3-27b-it-Q4_K_M",
            "name": "Gemma 3 27B (LDIE)",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 8192,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### 設定値の説明

| フィールド | 値 | 説明 |
|---|---|---|
| `"primary"` | `"ldie/gemma-3-27b-it-Q4_K_M"` | `プロバイダ名/モデルID` の形式 |
| `baseUrl` | `http://192.168.1.100:8081/v1` | Windows LDIEサーバーのプライベートIP:ポート + `/v1` |
| `apiKey` | `sk-local-...` | LDIEの `LLAMA_API_KEY` と同じ値 |
| `api` | `openai-completions` | OpenAI互換API形式（必ずこの値を使用） |
| `id` | モデルID | LDIEの `/v1/models` で返されるID |
| `contextWindow` | `8192` | LDIEの `.env` の `LLAMA_CTX_SIZE` と合わせる |
| `maxTokens` | `4096` | 1回の応答の最大トークン数 |
| `cost` | すべて `0` | ローカル実行のため課金なし |

## 3-3. 複数モデル構成（並行運用時）

Windows側で複数モデルを異なるポートで並行運用している場合、
プロバイダを分けて登録できます。

> ポート設計の詳細は [LDIE命名規則 - ポート設計ガイド](../LDIE_NamingConvention.md) を参照。

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ldie-gemma/gemma-3-27b-it-Q4_K_M"
      }
    }
  },
  "models": {
    "providers": {
      "ldie-gemma": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local-your-secret-key-here",
        "api": "openai-completions",
        "models": [
          {
            "id": "gemma-3-27b-it-Q4_K_M",
            "name": "Gemma 3 27B (Safe/Main)",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 8192,
            "maxTokens": 4096
          }
        ]
      },
      "ldie-coder": {
        "baseUrl": "http://192.168.1.100:8085/v1",
        "apiKey": "sk-local-your-secret-key-here",
        "api": "openai-completions",
        "models": [
          {
            "id": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M",
            "name": "Qwen3 Coder 30B (Code)",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 8192,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

## 3-4. モデルIDの確認方法

Windows LDIEサーバーで現在ロードされているモデルIDを確認:

```bash
curl -H "Authorization: Bearer sk-local-your-secret-key-here" \
  http://192.168.1.100:8081/v1/models | python3 -m json.tool
```

出力の `"id"` フィールドの値を `openclaw.json` の `"id"` にそのまま使います。

## 3-5. 設定の検証

```bash
# プロバイダとモデルが認識されているか確認
openclaw models list --provider ldie
```

登録したモデルが表示されればOKです。

---

[← ネットワーク確認](02_network_verification.md) | [次: 動作確認・自走テスト →](04_run_and_test.md) | [Ubuntu Readyトップ](README.md)

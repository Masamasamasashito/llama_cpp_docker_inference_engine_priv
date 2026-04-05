# 3. OpenClaw設定

OpenClawにLLMプロバイダを登録します。
**Pattern A（全ローカル）** と **Pattern B（司令塔クラウド + 作業役ローカル）** の2パターンから選択してください。

> 2パターンの詳細な比較は [LDIEアーキテクチャ](../LDIE_Architecture.md) を参照。

## 3-1. openclaw.jsonの場所

```bash
ls ~/.openclaw/openclaw.json
```

> ファイルがない場合は `openclaw onboard` を先に実行してください。

## 3-2. どちらのパターンを選ぶか

| 判断基準 | Pattern A（全ローカル） | Pattern B（ハイブリッド） |
|---|---|---|
| 月額コスト | 電気代のみ | +月$20-80のAPI課金 |
| インターネット | **不要** | 必要 |
| プライバシー | **最高** | 司令塔経由でクラウドに一部送信 |
| 精度 | 中〜高 | **最高** |
| 向いている用途 | 定型作業・プライバシー重視 | 複雑なタスク・高品質要求 |


## Pattern A: 全ローカルLLM（電気代のみ）

### 3-A1. openclaw.jsonの編集

```bash
nano ~/.openclaw/openclaw.json
```

以下の内容に書き換えてください:

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ldie/gemma-4-31B-it-Q4_K_M"
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
            "id": "gemma-4-31B-it-Q4_K_M",
            "name": "Gemma 4 31B IT (Local)",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

> `192.168.1.100` と `sk-local-your-secret-key-here` は実際の値に置き換えてください。

### 3-A2. 設定値の説明

| フィールド | 値 | 説明 |
|---|---|---|
| `"primary"` | `"ldie/gemma-4-31B-it-Q4_K_M"` | `プロバイダ名/モデルID` の形式 |
| `baseUrl` | `http://192.168.1.100:8081/v1` | Windows LDIEサーバーのプライベートIP:ポート + `/v1` |
| `apiKey` | `sk-local-...` | LDIEの `LLAMA_API_KEY` と同じ値 |
| `api` | `openai-completions` | OpenAI互換API形式（必ずこの値） |
| `contextWindow` | `8192` | LDIEの `.env` の `LLAMA_CTX_SIZE` と合わせる |
| `cost` | すべて `0` | ローカル実行のため課金なし |

### 3-A3. モデルの切り替え

別のモデルに切り替える場合:

1. Windows側: `.env` の `LLAMA_MODEL_FILE` を変更して `docker-compose restart`
2. Ubuntu側: `openclaw.json` の `id` と `name` を新モデルに変更


## Pattern B: 司令塔クラウド + 作業役ローカル（黄金バランス）

### 3-B1. クラウドAPIキーの準備

司令塔用のAPIキーを取得してください。

| プロバイダ | APIキー取得先 | 推奨モデル |
|---|---|---|
| Anthropic | https://console.anthropic.com/ | Claude Opus 4.6 |
| OpenAI | https://platform.openai.com/ | GPT-4o |

### 3-B2. openclaw.jsonの編集

```bash
nano ~/.openclaw/openclaw.json
```

以下の内容に書き換えてください:

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        // 司令塔: クラウドのフロンティアモデル（判断・計画・レビュー）
        "primary": "anthropic/claude-opus-4-6"
      }
    }
  },
  "models": {
    "providers": {
      // ──────────────────────────────────────────────────
      // 司令塔（クラウド）— 判断・計画・品質チェック
      // トークン消費: 全体の約5%（少量・高品質）
      // ──────────────────────────────────────────────────
      "anthropic": {
        "apiKey": "sk-ant-your-anthropic-key-here",
        "api": "anthropic-messages"
      },

      // ──────────────────────────────────────────────────
      // 作業役（LDIE ローカル）— コード生成・ファイル操作・検索
      // トークン消費: 全体の約95%（大量・電気代のみ）
      // ──────────────────────────────────────────────────
      "ldie-gemma": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local-your-secret-key-here",
        "api": "openai-completions",
        "models": [
          {
            "id": "gemma-3-27b-it-Q4_K_M",
            "name": "Gemma 3 27B (Local/Safe)",
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
            "name": "Qwen3 Coder 30B (Local/Code)",
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

### 3-B3. 設定値の説明

**司令塔（クラウド）:**

| フィールド | 値 | 説明 |
|---|---|---|
| `"primary"` | `"anthropic/claude-opus-4-6"` | 司令塔モデル。全タスクの判断・計画・レビューを担当 |
| `apiKey` | `sk-ant-...` | Anthropic APIキー（クラウド課金） |
| `api` | `anthropic-messages` | Anthropic API形式 |

**作業役（LDIE ローカル）:**

| フィールド | 値 | 説明 |
|---|---|---|
| `baseUrl` | `http://192.168.1.100:8081/v1` | Windows LDIEの汎用モデル |
| `baseUrl` | `http://192.168.1.100:8085/v1` | Windows LDIEのコーディングモデル（別ポート） |
| `apiKey` | `sk-local-...` | LDIEの `LLAMA_API_KEY`（両モデル共通でOK） |
| `cost` | すべて `0` | ローカル実行のため課金なし |

> 複数モデルを並行運用するにはWindows側でポートを分けて起動する必要があります。
> 詳細は [ポート設計ガイド](../LDIE_NamingConvention.md) を参照。

### 3-B4. OpenAI GPT-4oを司令塔にする場合

`anthropic` の代わりに `openai` を設定:

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-4o"
      }
    }
  },
  "models": {
    "providers": {
      "openai": {
        "apiKey": "sk-your-openai-key-here",
        "api": "openai-completions"
      },
      // 作業役（LDIE）は同じ
      "ldie-gemma": { ... },
      "ldie-coder": { ... }
    }
  }
}
```

## 3-3. 共通: モデルIDの確認方法

Windows LDIEサーバーでロード中のモデルIDを確認:

```bash
curl -H "Authorization: Bearer sk-local-your-secret-key-here" \
  http://192.168.1.100:8081/v1/models | python3 -m json.tool
```

出力の `"id"` フィールドを `openclaw.json` の `"id"` にそのまま使います。

## 3-4. 共通: 設定の検証

```bash
# Pattern A
openclaw models list --provider ldie

# Pattern B
openclaw models list --provider anthropic
openclaw models list --provider ldie-gemma
openclaw models list --provider ldie-coder
```

登録したモデルが表示されればOKです。

## 3-5. Pattern A → B への移行

Pattern A で始めて、精度が不足してきたらPattern Bに移行できます。
`openclaw.json` の変更のみで、Windows LDIE側の設定変更は不要です。

1. クラウドAPIキーを取得
2. `openclaw.json` に `anthropic`（または`openai`）プロバイダを追加
3. `agents.defaults.model.primary` をクラウドモデルに変更
4. LDIE作業役の設定はそのまま残す

[← ネットワーク確認](02_network_verification.md) | [次: 動作確認・自走テスト →](04_run_and_test.md) | [Ubuntu Readyトップ](README.md)

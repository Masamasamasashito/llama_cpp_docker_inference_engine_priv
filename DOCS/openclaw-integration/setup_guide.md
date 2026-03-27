# OpenClaw連携 セットアップ手順

LLMサーバーPCでllama.cppを起動し、他PCのOpenClawからローカルLLMを利用するまでの
全手順です。

---

## 全体の流れ

1. **LLMサーバーPC**: llama.cppサーバーを起動（LAN公開済み）
2. **LLMサーバーPC**: ファイアウォールでポート開放
3. **クライアントPC**: OpenClawをインストール
4. **クライアントPC**: openclaw.jsonにローカルLLMサーバーを登録
5. **動作確認**: OpenClawがローカルLLMで自走

---

## Step 1: LLMサーバーPCの準備

### 1-1. モデルのダウンロードと起動

テキスト生成LLMの [セットアップ手順](../text-llm/setup_guide.md) に従い、
モデルをダウンロードしてdocker-composeで起動します。

```bash
# .envを設定（例: Qwen3.5-27B）
cp .env.example.qwen3.5-27b .env

# モデルダウンロード
curl -L -o models/Qwen3.5-27B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/resolve/main/Qwen3.5-27B-Q4_K_M.gguf

# GPU版で起動
docker-compose up -d

# RTX 5090の場合
docker-compose -f docker-compose.high.yml up -d
```

### 1-2. LAN公開の確認

docker-compose.ymlではコンテナの8080ポートをホストの8081にマッピングしています。
Dockerの `0.0.0.0` バインドにより、デフォルトでLAN内の他PCからアクセス可能です。

```bash
# サーバーPC自身で確認
curl http://localhost:8081/health
curl http://localhost:8081/v1/models

# サーバーPCのLAN IPを確認
# Windows
ipconfig
# Linux
ip addr show
```

サーバーPCのIPアドレスを控えてください（例: `192.168.1.100`）。

### 1-3. ファイアウォール設定

詳細は [ネットワーク設定](network_config.md) を参照してください。

**Windows（PowerShell を管理者で実行）:**

```powershell
New-NetFirewallRule -DisplayName "llama.cpp API" -Direction Inbound -Port 8081 -Protocol TCP -Action Allow
```

**Linux（ufw）:**

```bash
sudo ufw allow 8081/tcp
```

### 1-4. 他PCからの疎通確認

クライアントPCから以下を実行して応答があることを確認します。

```bash
# サーバーPCのIPに置き換えてください
curl http://192.168.1.100:8081/health

# モデル一覧
curl http://192.168.1.100:8081/v1/models

# テスト推論
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-27B-Q4_K_M",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

応答が返れば、LLMサーバー側の準備は完了です。

---

## Step 2: クライアントPCにOpenClawをインストール

### 2-1. Node.jsのインストール

OpenClawにはNode.js 22以上が必要です。

```bash
# Node.js 22+ がインストール済みか確認
node -v

# 未インストールの場合
# Windows: https://nodejs.org/ からLTS版をダウンロード
# macOS: brew install node
# Linux: curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs
```

### 2-2. OpenClawのインストール

```bash
npm install -g @anthropic-ai/openclaw
```

### 2-3. 初期セットアップ

```bash
openclaw onboard
```

対話形式でセットアップが始まります。
LLMプロバイダの設定は次のステップで手動設定するため、ここではスキップしてOKです。

---

## Step 3: OpenClawにローカルLLMサーバーを登録

### 3-1. openclaw.jsonの編集

`~/.openclaw/openclaw.json` を編集して、ローカルLLMサーバーを登録します。

```jsonc
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "local-llm/Qwen3.5-27B-Q4_K_M"
      }
    }
  },
  "models": {
    "providers": {
      "local-llm": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "Qwen3.5-27B-Q4_K_M",
            "name": "Qwen3.5-27B (Local)",
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

**設定値の説明:**

| フィールド | 値 | 説明 |
|---|---|---|
| `baseUrl` | `http://192.168.1.100:8081/v1` | LLMサーバーPCのIP:ポート + `/v1` |
| `apiKey` | `sk-local` | llama.cppは認証不要だがダミー値が必要 |
| `api` | `openai-completions` | OpenAI互換APIとして接続 |
| `id` | モデル名 | llama.cppの `/v1/models` で返されるモデルID |
| `contextWindow` | `8192` | .envの `LLAMA_CTX_SIZE` と合わせる |
| `maxTokens` | `4096` | 1回の応答の最大トークン数 |
| `cost` | すべて `0` | ローカル実行のため課金なし |

### 3-2. 複数モデルの登録（オプション）

9Bモデルも併用する場合は `models` 配列に追加します。

```jsonc
{
  "models": {
    "providers": {
      "local-llm": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "Qwen3.5-27B-Q4_K_M",
            "name": "Qwen3.5-27B (Local)",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 8192,
            "maxTokens": 4096
          },
          {
            "id": "Qwen3.5-9B-Q4_K_M",
            "name": "Qwen3.5-9B (Local/Fast)",
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

> 注意: llama.cppは1つのモデルしか同時にロードできません。
> モデルを切り替える場合はサーバーPC側で `.env` を変更して再起動が必要です。

---

## Step 4: 動作確認

### 4-1. モデル認識の確認

```bash
openclaw models list --provider local-llm
```

登録したモデルが表示されればOKです。

### 4-2. OpenClawで会話テスト

```bash
openclaw
```

OpenClawが起動し、ローカルLLMを使って応答を返せば設定完了です。

### 4-3. 自走テストの例

```bash
# ファイル操作を含むタスクを指示
openclaw "このディレクトリのファイル一覧を取得して、READMEの概要を教えて"
```

OpenClawがローカルLLMの応答に基づいて自律的にコマンド実行・ファイル読み取りを
行えば、ローカルLLM駆動のAIエージェントとして正常に動作しています。

---

## トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| `Connection refused` | サーバーPCのファイアウォール確認。[ネットワーク設定](network_config.md) 参照 |
| `Model not found` | `curl http://サーバーIP:8081/v1/models` でモデルIDを確認し、openclaw.jsonの `id` と一致させる |
| OpenClawが応答しない | `contextWindow` が大きすぎると遅くなる。.envの `LLAMA_CTX_SIZE` と合わせる |
| `tool calling` が動かない | `api` を `openai-completions` にする。`openai-responses` は非対応の場合あり |
| 応答が遅い | サーバーPCで `nvidia-smi` 確認。GPUが使われているか。小さいモデル（9B）も検討 |
| `apiKey` エラー | llama.cppは認証不要だがOpenClawは `apiKey` 必須。ダミー値 `sk-local` を設定 |

---

[ネットワーク設定](network_config.md) | [OpenClaw連携トップ](README.md) | [ドキュメント一覧](../README.md)

# LDIE 命名規則（Naming Convention）

**LDIE** = **L**lama.cpp **D**ocker **I**nference **E**ngine

本リポジトリの環境変数・ファイル・ボリューム等の命名規則です。
[EdgeOptimizer](https://github.com/Masamasamasashito/EdgeOptimizer) の設計パターンを参考にしています。

---

## 1. 環境変数のプレフィックス体系

```
COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE
│      │    │      │     │   │
│      │    │      │     │   └─ 項目名（IMAGE / IMAGE_TAG）
│      │    │      │     └─ バリアント（GPU / CPU）
│      │    │      └─ サービス名（LLAMA）
│      │    └─ スコープ（DOCKER = Docker関連）
│      └─ プロジェクト識別子（LDIE）
└─ 共有レベル（COMMON = docker-compose.yml と Dockerfile で共有）
```

### プレフィックスの意味

| プレフィックス | 意味 | 用途 |
|---|---|---|
| `COMMON_LDIE_` | docker-compose.yml と Dockerfile の両方で参照 | イメージ名・タグ等 |
| `DOCKER_HOST_` | ホストマシン側の設定 | バインドアドレス・ホスト側ポート |
| `LLAMA_` | llama.cppサーバーの設定 | モデル・推論パラメータ・API Key |
| `COMMON_` | 全サービス共通の設定 | タイムゾーン等 |

---

## 2. ホスト側 vs コンテナ側の分離

ポートやアドレスは、**ホスト側かコンテナ側かが名前で判別できる**ようにします。

| 変数名 | スコープ | 説明 | デフォルト |
|---|---|---|---|
| `DOCKER_HOST_BIND_ADDR` | ホスト | バインドするIPアドレス | `127.0.0.1` |
| `DOCKER_HOST_PORT_LLAMA` | ホスト | 外部公開ポート | `8081`（GPU）/ `8082`（CPU）/ `8083`（High） |
| `LLAMA_CONTAINER_LISTEN_PORT` | コンテナ | コンテナ内部リッスンポート | `8080`（変更非推奨） |

docker-compose.ymlでの使い方:
```yaml
ports:
  - "${DOCKER_HOST_BIND_ADDR:-127.0.0.1}:${DOCKER_HOST_PORT_LLAMA:-8081}:${LLAMA_CONTAINER_LISTEN_PORT:-8080}"
#    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#    ホスト側バインドアドレス              ホスト側ポート                     コンテナ側ポート
```

---

## 3. Dockerイメージの変数化

イメージ名とタグを分離し、.envでバージョンピンが可能です。

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE` | GPU版イメージ名 | `ghcr.io/ggml-org/llama.cpp` |
| `COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE_TAG` | GPU版タグ | `server-cuda` |
| `COMMON_LDIE_DOCKER_LLAMA_CPU_IMAGE` | CPU版イメージ名 | `ghcr.io/ggerganov/llama.cpp` |
| `COMMON_LDIE_DOCKER_LLAMA_CPU_IMAGE_TAG` | CPU版タグ | `latest` |

docker-compose.ymlでの使い方:
```yaml
image: ${COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE:-ghcr.io/ggml-org/llama.cpp}:${COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE_TAG:-server-cuda}
```

---

## 4. .env.example のセクション構造

すべての `.env.example.*` ファイルは以下の統一構造に従います。

```
# ==============================================================================
# 🚀 .env GET READY: First Trial Setup
# ==============================================================================
# セットアップ手順、モデルダウンロードコマンド、シークレット生成コマンド

# ==============================================================================
# 📦 ADVANCED: Running Multiple Local Environments
# ==============================================================================
# 複数環境運用時の注意事項

# ==============================================================================
# ⚙️ Configuration
# ==============================================================================
# --- 1. Global Settings ---          COMMON_TIMEZONE
# --- 2. Docker Image & Version ---   COMMON_LDIE_DOCKER_*
# --- 3. Network Binding ---          DOCKER_HOST_*, LLAMA_CONTAINER_*
# --- 4. Model Settings ---           LLAMA_MODEL_FILE
# --- 5. Inference Parameters ---     LLAMA_CTX_SIZE, LLAMA_N_PARALLEL, etc.
# --- 6. Security ---                 LLAMA_API_KEY
```

---

## 5. 複数環境対応マーカー

複数環境を同時に動かす場合に変更が必要な項目には `🔄 IF MULTI-ENV:` コメントを付けます。

```bash
# 変更が必要な項目を一覧で確認
grep "MULTI-ENV" .env
```

```bash
# .env.example 内の例:
# 🔄 IF MULTI-ENV: Change this port (e.g., 8081 -> 18081)
DOCKER_HOST_PORT_LLAMA=8081
```

---

## 6. ポート設計ガイド（複数モデル並行運用）

多くのOSSプロジェクトでは、複数インスタンスの並行運用時にポートが競合し、手動でのポート管理が必要になります。
LDIEでは `DOCKER_HOST_PORT_LLAMA` を `.env` で変えるだけで並行運用できる設計になっています。

### 基本原則

- **1024以下は使わない**（特権ポート。root/管理者権限が必要）
- **既知サービスのポートを避ける**（下記の予約ポート表を参照）
- **連番で規則性を持たせる**（どのモデル/モードか一目で分かる）
- **コンテナ内部ポートは変えない**（`LLAMA_CONTAINER_LISTEN_PORT=8080` は固定。ホスト側ポートだけ変える）

### LDIEポート割り当て体系

```
8081 - 8099: テキスト生成LLM（llama.cpp）
8100 - 8199: 動画生成（ComfyUI）※将来用
```

#### デフォルトポート（モード別）

| ポート | モード | docker-compose |
|---|---|---|
| `8081` | GPU（デフォルト） | `docker-compose.yml` |
| `8082` | CPU | `docker-compose.cpu.yml` |
| `8083` | High（RTX 5090） | `docker-compose.high.yml` |

#### 複数モデル並行運用時のポート割り当て例

| ポート | モデル | 用途 |
|---|---|---|
| `8081` | Gemma 3 27B | メイン（安全性最高） |
| `8084` | Qwen3.5-27B | 日本語汎用 |
| `8085` | Qwen3-Coder-30B | コーディング |
| `8086` | Qwen3-32B | 最高品質 |
| `8087` | Qwen3.5-9B | 軽量・高速 |
| `8088` | DeepSeek R1 32B | 推論・分析（リスク高。用途を限定） |

### 並行運用の手順

ディレクトリを分けて、各 `.env` でポートとモデルを変えます。

```bash
# 1. モデル別ディレクトリを作成
mkdir model-gemma model-qwen

# 2. .env.exampleをコピーしてポートを変更
cp .env.example.gemma3-27b model-gemma/.env
cp .env.example.qwen3.5-27b model-qwen/.env

# 3. 各.envでポートを変更
# model-gemma/.env
DOCKER_HOST_PORT_LLAMA=8081  # デフォルトのまま

# model-qwen/.env
DOCKER_HOST_PORT_LLAMA=8084  # 別ポートに変更

# 4. 各ディレクトリからdocker-compose起動
cd model-gemma && docker-compose up -d
cd ../model-qwen && docker-compose up -d

# 5. 各モデルにアクセス
curl http://localhost:8081/health  # Gemma
curl http://localhost:8084/health  # Qwen
```

### 避けるべきポート

以下のポートは既知のサービスで使用されるため、LDIEでは使用を避けてください。

| ポート | 使用サービス | 競合リスク |
|---|---|---|
| `80` / `443` | HTTP / HTTPS | 高 |
| `3000` | Grafana / Next.js / Playwright | 高 |
| `3306` | MySQL | 中 |
| `5432` | PostgreSQL | 中 |
| `5678` | n8n | 中 |
| `6379` | Redis | 中 |
| `8080` | 多数のWebサーバー・プロキシ | **最高（意図的に避けている）** |
| `8188` | ComfyUI | 中（動画生成で使用） |
| `8443` | HTTPS代替 | 低 |
| `11434` | Ollama | 中 |

> `8080` をLDIEのデフォルトから外しているのは、最も競合リスクが高いポートであるためです。

### OpenClaw連携時のポート設計

OpenClawの `openclaw.json` でモデルごとに異なるポートを指定することで、
1台のWindows LLMサーバーで複数モデルを提供し、Ubuntu側のOpenClawから使い分けることができます。

```jsonc
{
  "models": {
    "providers": {
      "local-gemma": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local-xxx",
        "api": "openai-completions",
        "models": [{"id": "gemma-3-27b-it-Q4_K_M", "name": "Gemma 3 27B"}]
      },
      "local-qwen-coder": {
        "baseUrl": "http://192.168.1.100:8085/v1",
        "apiKey": "sk-local-xxx",
        "api": "openai-completions",
        "models": [{"id": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M", "name": "Qwen3 Coder"}]
      }
    }
  }
}
```

> OpenClawが用途に応じてモデルを使い分ける構成が可能になります。
> ただしモデル数分のVRAMが必要です（RTX 5090 32GBで2モデル同時が現実的な上限）。

---

## 7. シークレット管理

- シークレット値は `.env.example` に**書かない**
- 生成コマンドを `.env.example` 冒頭に記載し、ユーザーが実行して `.env` 末尾に追記する設計
- `.env` は `.gitignore` 対象（Gitにコミットしない）

```bash
# macOS / Linux
echo "LLAMA_API_KEY=sk-local-$(openssl rand -hex 32)" >> .env

# Windows PowerShell
$bytes = New-Object byte[] 32; ...; "LLAMA_API_KEY=sk-local-$hex" | Add-Content .env
```

---

## 8. ログローテーション

全サービスに統一のログ設定を `x-logging` YAMLアンカーで適用します。

```yaml
x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"    # 1ファイルあたり最大10MB
    max-file: "3"      # 最大3ファイルでローテーション

services:
  llama-cpp-gpu:
    logging: *default-logging
```

---

## 9. ファイル命名規則

| パターン | 例 | 説明 |
|---|---|---|
| `.env.example.<モデル名>` | `.env.example.qwen3.5-27b` | モデル別環境変数テンプレート |
| `test_request_<モデル名>.py` | `test_request_qwen3.5-27b.py` | モデル別テストリクエスト |
| `docker-compose.<バリアント>.yml` | `docker-compose.high.yml` | 構成別Docker Compose |
| `DOCS/<カテゴリ>/` | `DOCS/text-llm/` | カテゴリ別ドキュメント |

---

## 10. 変数一覧（全量）

### Global

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `COMMON_TIMEZONE` | 全サービス共通タイムゾーン | `Asia/Tokyo` |

### Docker Image

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE` | GPU版イメージ | `ghcr.io/ggml-org/llama.cpp` |
| `COMMON_LDIE_DOCKER_LLAMA_GPU_IMAGE_TAG` | GPU版タグ | `server-cuda` |
| `COMMON_LDIE_DOCKER_LLAMA_CPU_IMAGE` | CPU版イメージ | `ghcr.io/ggerganov/llama.cpp` |
| `COMMON_LDIE_DOCKER_LLAMA_CPU_IMAGE_TAG` | CPU版タグ | `latest` |

### Network

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `DOCKER_HOST_BIND_ADDR` | ホスト側バインドアドレス | `127.0.0.1` |
| `DOCKER_HOST_PORT_LLAMA` | ホスト側公開ポート | `8081`（GPU）/ `8082`（CPU）/ `8083`（High） |
| `LLAMA_CONTAINER_LISTEN_PORT` | コンテナ内リッスンポート | `8080`（変更非推奨） |

### Model

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `LLAMA_MODEL_FILE` | GGUFモデルファイル名 | モデルにより異なる |

### Inference

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `LLAMA_CTX_SIZE` | コンテキストサイズ | compose別 |
| `LLAMA_N_PARALLEL` | 並列処理数 | compose別 |
| `LLAMA_N_GPU_LAYERS` | GPUレイヤー数 | `99` |
| `LLAMA_THREADS` | スレッド数 | compose別 |
| `LLAMA_TEMP` | 温度 | compose別 |
| `LLAMA_TOP_K` | Top-K | compose別 |
| `LLAMA_TOP_P` | Top-P | compose別 |
| `LLAMA_MIN_P` | Min-P | compose別 |
| `LLAMA_REPEAT_PENALTY` | 繰り返しペナルティ | compose別 |
| `LLAMA_BATCH_SIZE` | バッチサイズ（high版のみ） | `4096` |
| `LLAMA_UBATCH_SIZE` | μバッチサイズ（high版のみ） | `2048` |

### Security

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `LLAMA_API_KEY` | Bearer Token認証キー | 空（認証なし） |

---

[ドキュメント一覧](README.md)

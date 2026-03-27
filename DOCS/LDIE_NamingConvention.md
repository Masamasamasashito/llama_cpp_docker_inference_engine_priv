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
| `DOCKER_HOST_PORT_LLAMA` | ホスト | 外部公開ポート | `8081`（GPU）/ `8080`（CPU） |
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

## 6. シークレット管理

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

## 7. ログローテーション

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

## 8. ファイル命名規則

| パターン | 例 | 説明 |
|---|---|---|
| `.env.example.<モデル名>` | `.env.example.qwen3.5-27b` | モデル別環境変数テンプレート |
| `client_sample_<モデル名>.py` | `client_sample_qwen3.5-27b.py` | モデル別クライアントサンプル |
| `docker-compose.<バリアント>.yml` | `docker-compose.high.yml` | 構成別Docker Compose |
| `DOCS/<カテゴリ>/` | `DOCS/text-llm/` | カテゴリ別ドキュメント |

---

## 9. 変数一覧（全量）

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
| `DOCKER_HOST_PORT_LLAMA` | ホスト側公開ポート | `8081`（GPU）/ `8080`（CPU） |
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

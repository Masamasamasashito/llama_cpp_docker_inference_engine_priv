<div align="center">

# 🦙 LDIE — Llama.cpp Docker Inference Engine

<!-- ヘッダー画像例（必要に応じてURLを差し替えてください） -->

![](https://github.com/user-attachments/assets/5960ce66-a66f-44a8-b6bc-413449fb1d8e)

<p>
  <img src="https://img.shields.io/badge/Docker-blue?logo=docker" />
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Windows_11_Pro-blue?logo=windows" />
  <img src="https://img.shields.io/badge/Ubuntu_24.04-orange?logo=ubuntu" />
  <img src="https://img.shields.io/badge/RTX_5090-76B900?logo=nvidia" />
</p>

</div>

> 参照元リポジトリ: [Sunwood-ai-labs/llama-cpp-docker-compose](https://github.com/Sunwood-ai-labs/llama-cpp-docker-compose)
> （本リポジトリ LDIE は上記をベースに、命名規則・セキュリティ・OpenClaw連携・マルチモデル対応等を大幅に強化したものです）

---

## 概要

llama.cpp をDocker上で動かし、**OpenAI互換API**と**組み込みWebUI**を提供するセットアップです。
ホームLAN内の他PCのOpenClawにローカルLLMとしてAPIを提供し、AIエージェントを自走させることを主目的としています。

### 主な特徴

- OpenAI互換API（`/v1/chat/completions`）でどんなクライアントからでも利用可能
- **組み込みWebUI** — llama.cppサーバーにブラウザでアクセスするだけでチャット可能（ChatGPT風）
- **OpenClaw連携** — LAN内の他PCのAIエージェントにローカルLLMを提供
- Qwen3.5-27B / Qwen3.5-9B / Gemma 3n E2B 等のマルチモデル対応
- RTX 5090最適化構成を含むGPU/CPU/High 3種のdocker-compose
- [LDIE命名規則](DOCS/LDIE_NamingConvention.md) に基づく高品質な変数設計
- `.env` だけでイメージバージョン・ポート・バインドアドレス・API Key等を一元管理
- デフォルト `127.0.0.1` バインド + API Key認証によるセキュリティ設計

---

## 📖 ドキュメント

| カテゴリ | 内容 | リンク |
|---|---|---|
| テキスト生成 LLM | llama.cpp + Docker によるテキスト生成 | [DOCS/text-llm/](DOCS/text-llm/README.md) |
| 動画生成 | ComfyUI による動画生成 | [DOCS/video-generation/](DOCS/video-generation/README.md) |
| OpenClaw連携 | 他PCのOpenClawにローカルLLMを提供 | [DOCS/openclaw-integration/](DOCS/openclaw-integration/README.md) |
| LDIE 命名規則 | 環境変数・ファイルの命名規則 | [DOCS/LDIE_NamingConvention.md](DOCS/LDIE_NamingConvention.md) |

詳細は [ドキュメント一覧](DOCS/README.md) を参照してください。

---

## 📁 ディレクトリ構成

```
LDIE/
├── models/                        # モデル(GGUF)ファイル配置用
├── logs/                          # サーバーログ保存用
├── example/                       # クライアントサンプルコード
│   ├── test_request_gemma3n-e2b.py
│   ├── test_request_qwen3.5-27b.py
│   ├── test_request_qwen3.5-9b.py
│   └── test_request_logprobs.py
├── DOCS/
│   ├── README.md                  # ドキュメントハブ
│   ├── LDIE_NamingConvention.md   # 命名規則リファレンス
│   ├── text-llm/                  # テキスト生成LLMドキュメント
│   ├── video-generation/          # 動画生成ドキュメント
│   └── openclaw-integration/      # OpenClaw連携ガイド
├── .env.example.gemma3n-e2b       # Gemma 3n E2B 用テンプレート
├── .env.example.qwen3.5-27b      # Qwen3.5-27B 用テンプレート
├── .env.example.qwen3.5-9b       # Qwen3.5-9B 用テンプレート
├── docker-compose.yml             # GPU版（デフォルト）
├── docker-compose.cpu.yml         # CPU版
├── docker-compose.high.yml        # RTX 5090向け高性能版
└── README.md
```

---

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone <your-repo-url>
cd llama_cpp_docker_inference_engine_priv
```

### 2. モデルのダウンロード

`models/` ディレクトリにGGUFファイルを配置します。

```bash
# Qwen3.5-27B（16.7GB, 推奨）
curl -L -o models/Qwen3.5-27B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/resolve/main/Qwen3.5-27B-Q4_K_M.gguf

# Qwen3.5-9B（5.68GB, 軽量）
curl -L -o models/Qwen3.5-9B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf

# Gemma 3n E2B
curl -L -o models/gemma3n-e2b-fixed.gguf \
  https://huggingface.co/unsloth/gemma-3n-E2B-it-GGUF/resolve/main/gemma-3n-E2B-it-UD-Q4_K_XL.gguf
```

### 3. 環境変数の設定

使いたいモデルの `.env.example.*` をコピーして `.env` を作成します。

```bash
# Qwen3.5-27B の場合
cp .env.example.qwen3.5-27b .env

# Qwen3.5-9B の場合
cp .env.example.qwen3.5-9b .env

# Gemma 3n E2B の場合
cp .env.example.gemma3n-e2b .env
```

> `.env.example.*` はセクション構造化されています。
> 詳細は [LDIE 命名規則](DOCS/LDIE_NamingConvention.md) を参照してください。

### 4. （オプション）API Key の生成

OpenClaw連携やLAN公開する場合は、API Key認証を有効化してください。

```bash
# macOS / Linux
echo "LLAMA_API_KEY=sk-local-$(openssl rand -hex 32)" >> .env
```

```powershell
# Windows PowerShell
$bytes = New-Object byte[] 32; (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); $hex = -join ($bytes | ForEach-Object { $_.ToString("x2") }); "LLAMA_API_KEY=sk-local-$hex" | Add-Content .env
```

### 5. 起動

```bash
# GPU版（デフォルト）
docker-compose up -d

# CPU版
docker-compose -f docker-compose.cpu.yml up -d

# RTX 5090向け高性能版
docker-compose -f docker-compose.high.yml up -d
```

### 6. 動作確認

```bash
# ヘルスチェック（GPU版のデフォルトポートは 8081）
curl http://localhost:8081/health

# モデル一覧（API Key認証を有効化した場合）
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8081/v1/models
```

### 7. 使い方

#### WebUI（ブラウザ）

llama.cppサーバーには**組み込みWebUI**が搭載されています。
ブラウザで以下のURLにアクセスするだけで、ChatGPT風のチャット画面が利用できます。

```
http://localhost:8081
```

- テキストファイルやPDFの添付に対応
- 特別なセットアップ不要（サーバー起動後すぐに利用可能）

#### API（curl / Python）

```bash
# Chat API（API Key認証あり）
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Qwen3.5-27B-Q4_K_M",
    "messages": [
      {"role": "user", "content": "こんにちは、あなたは誰ですか？"}
    ]
  }'
```

```bash
# Pythonサンプル
python example/test_request_qwen3.5-27b.py
```

### 8. 停止

```bash
docker-compose down
```

---

## 🔧 モード一覧

| モード | docker-compose | デフォルトポート | 用途 |
|---|---|---|---|
| GPU | `docker-compose.yml` | `8081` | 標準GPU推論 |
| CPU | `docker-compose.cpu.yml` | `8080` | GPU不要の検証用 |
| High | `docker-compose.high.yml` | `8081` | RTX 5090最適化（VRAM 32GB） |

> ポートは `.env` の `DOCKER_HOST_PORT_LLAMA` で変更可能です。

---

## 🔒 セキュリティ

| レイヤー | 対策 |
|---|---|
| バインドアドレス | デフォルト `127.0.0.1`（ローカルのみ）。LAN公開時はプライベートIPを明示指定 |
| API Key認証 | `--api-key` によるBearer Token認証 |
| ファイアウォール | 特定プライベートIPのみ許可（OpenClaw連携時） |

詳細は [OpenClaw連携 - ネットワーク設定](DOCS/openclaw-integration/network_config.md) を参照してください。

---

## ❓ よくあるトラブル

| 問題 | 原因・対策 |
|---|---|
| GPU効かない | NVIDIA Container Toolkit未導入 / CUDAバージョン不一致。`nvidia-smi` がDocker内で動くか確認 |
| モデルロード失敗 | `.env` の `LLAMA_MODEL_FILE` と `models/` 内のファイル名が一致しているか確認 |
| 応答が遅い | CPU実行になっている可能性。`LLAMA_N_GPU_LAYERS=99` を設定して全レイヤーGPUに |
| ポートに接続できない | GPU版は `8081`、CPU版は `8080` がデフォルト。`docker ps` でポート確認 |
| 401 Unauthorized | API Key不一致。`.env` の `LLAMA_API_KEY` とリクエストの `Authorization` ヘッダーを確認 |
| LAN内の他PCから接続不可 | `DOCKER_HOST_BIND_ADDR` がプライベートIPになっているか、ファイアウォールが開いているか確認 |

---

## 📊 Docker LLM推論エンジンの全体像

### なぜ LDIE を開発したか

RTX 5090（VRAM 32GB）をローカルLLM推論に使う際、既存ツールには以下の課題がありました。

- **Ollama**: 手軽だがGoデーモンが常駐し、GPUリソースをLLMに100%回せない。推論パラメータの細かいチューニングもできない
- **vLLM / SGLang**: 高スループットだがPyTorch+CUDAランタイムだけでVRAMを1-3GB消費する。マルチユーザー向けの設計で個人利用には過剰
- **LocalAI**: llama.cppを内包しているがGo製ラッパーのオーバーヘッドがあり、設定もシンプルではない

**「GPUリソースをLLMに最大限割り当てたい」** — この1点を最優先に、llama.cppのCUDAバイナリをDockerで直接実行し、`.env` だけで全パラメータを制御できる軽量な推論エンジンとしてLDIEを構築しました。

| エンジン | 軽量さ | LLMへのリソース割当最大化 | チューニング性 | Docker前提 | 個人GPU向き | OpenAI互換API |
|---|---|---|---|---|---|---|
| **LDIE (llama.cpp)** | 最軽量 | 最高（C++直実行、中間層なし。VRAM/CPU/メモリをほぼ100% LLMに使える） | 最高 | 設計思想そのもの | RTX 5090最適化済み | あり |
| Ollama | 中 | 中（Goデーモンが常駐しメモリ・CPU消費。KVキャッシュ管理もOllama側で制約あり） | 低 | 非公式 | 向いてる | あり |
| vLLM | 重い | 低（PyTorch+CUDAランタイムがVRAM 1-3GB消費。PagedAttentionのメタデータもオーバーヘッド） | 高 | 公式イメージあり | VRAM食う | あり |
| SGLang | 重い | 低（vLLM同等のPyTorchオーバーヘッド+RadixAttentionのツリー管理コスト） | 高 | 公式イメージあり | VRAM食う | あり |
| TGI | 中〜重 | 中（Rust+Python混成。PyTorchベースだがRust層で一部最適化） | 中 | 公式イメージあり | やや重い | あり |
| LocalAI | 中 | 中〜高（内部llama.cpp利用だがGo製ラッパー分のCPU/メモリ消費あり） | 中 | 公式イメージあり | 向いてる | あり |

> RTX 5090の32GB VRAMを1バイトでも多くLLMに使いたい場合、llama.cpp直実行のLDIEが最もロスが少ない。

### LDIEの強み

- **最小オーバーヘッド**: llama.cppのCUDAバイナリをDocker直実行。間にGo/Python/PyTorchが挟まらない
- **`.env`だけで全制御**: イメージバージョン・ポート・バインドアドレス・推論パラメータ・API Key
- **LDIE命名規則**: ホスト側/コンテナ側の区別が名前で明確（`DOCKER_HOST_` vs `LLAMA_CONTAINER_`）
- **RTX 5090最適化済み**: batch-size/ubatch-size/threads等がチューニング済みのdocker-compose.high.yml

### メリット・デメリット

**メリット**

- Ollamaより柔軟（パラメータ細かく制御可能）
- OpenAI互換APIで既存ツール・OpenClawと連携しやすい
- Dockerなので再現性が高い
- 組み込みWebUIでブラウザからすぐチャット可能
- `.env` だけで全設定を一元管理（LDIE命名規則）

**デメリット**

- モデル管理は手動（GGUFファイルを自分でダウンロード）
- 1コンテナ1モデル（モデル切り替えは再起動が必要）

<div align="center">

# 🦙 LDIE — Llama.cpp Docker Inference Engine with OpenClaw

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

- LDIEの参照元は Maki Sunwood ai labs さんのリポジトリ: [Sunwood-ai-labs/llama-cpp-docker-compose](https://github.com/Sunwood-ai-labs/llama-cpp-docker-compose) をベースに、命名規則・セキュリティ・OpenClaw連携(Windows11Pro▶OpenClaw(Ubuntu24.04))・マルチモデル対応等、模索、計測した記録です。まだ、ローカルLLMのパフォーマンス最適化までたどり着けてはいないです。
- Ollamaから始まり、RTX5090の小さなコンピューティング資源で高精度にレスポンスよくLLMを動かすための推論エンジンとして、Llama.cpp、vLLM、TensorRT-LLM、TGI、SGLang、LocalAI等、他のLLM推論エンジンについても模索、計測、チューニングして最適解を模索していく予定です。
- Claude CLIで細かく精査せず、勢いで進めてしまった部分もあり、明らかな失敗作リポジトリになっています（誤解を生まないように Maki Sunwood ai labs さんはシンプルできれいなリポジトリです）。LDIEはラフなバイブコーディングの過剰な表現も散見されますので、参照の際はご自身の判断でお願いします。
- [EdgeOptimizer](https://github.com/Masamasamasashito/EdgeOptimizer)のローカルLLM駆動開発や、LLM Edgeパフォーマンス最適化向けにEdge Optimizerを昇華させるための実験場として、様々な気付きをいただきました。ありがとうございます。

# 概要

2まで完了。

1. llama.cpp をDocker上で動かし、**OpenAI互換API**と**組み込みWebUI**を提供するセットアップ
2. ホームLAN内の他PCのOpenClawにローカルLLMとしてモデルをAPI提供
3. AIエージェントを自走させること

## 主な特徴

- OpenAI互換API（`/v1/chat/completions`）でどんなクライアントからでも利用可能
- **組み込みWebUI** — llama.cppサーバーにブラウザでアクセスするだけでチャット可能（ChatGPT風）
- **OpenClaw連携** — LAN内の他PC（Ubuntu 24.04.4 LTS）のAIエージェントにローカルLLMを提供
- テキスト生成7モデル + 動画生成4モデル対応
- RTX 5090最適化構成を含むGPU/CPU/High 3種のdocker-compose
- [LDIE命名規則](DOCS/LDIE_NamingConvention.md) に基づく高品質な変数設計（[EdgeOptimizer](https://github.com/Masamasamasashito/EdgeOptimizer)パターン準拠）
- `.env` だけでイメージバージョン・ポート・バインドアドレス・API Key等を一元管理
- デフォルト `127.0.0.1` バインド + API Key認証によるセキュリティ設計
- [モデルセキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) に基づくリスク管理

# 📊 Docker LLM推論エンジンの全体像

## なぜ LDIE を開発したか

RTX 5090（VRAM 32GB）をローカルLLM推論に使う際、既存ツールには以下の課題がありました。

- **Ollama**: 手軽だがGoデーモンが常駐し、GPUリソースをLLMに100%回せない。推論パラメータの細かいチューニングもできない
- **vLLM / SGLang**: 高スループットだがPyTorch+CUDAランタイムだけでVRAMを1-3GB消費する。マルチユーザー向けの設計で個人利用には過剰
- **LocalAI**: llama.cppを内包しているがGo製ラッパーのオーバーヘッドがあり、設定もシンプルではない
- **TensorRT-LLM**: Nvidia GPU のパフォーマンス最適化には一番よいと思われる。未着手。

**「GPUリソースをLLMに最大限割り当てたい」** — この1点を最優先に、llama.cppのCUDAバイナリをDockerで直接実行し、`.env` だけで全パラメータを制御できる軽量な推論エンジンとしてLDIEを構築しました。

| エンジン | 軽量さ | LLMへのリソース割当最大化 | チューニング性 | Docker前提 | 個人GPU向き | OpenAI互換API |
|---|---|---|---|---|---|---|
| **LDIE (llama.cpp)** | 最軽量 | C++直実行、中間層なし。VRAM/CPU/メモリをほぼ100% LLMに使える | 最高 | 設計思想そのもの | RTX 5090最適化済み | あり |
| Ollama | 中 | 中（Goデーモンが常駐しメモリ・CPU消費。KVキャッシュ管理もOllama側で制約あり） | 低 | 非公式 | 向いてる | あり |
| vLLM | 重い | 低（PyTorch+CUDAランタイムがVRAM 1-3GB消費。PagedAttentionのメタデータもオーバーヘッド） | 高 | 公式イメージあり | VRAM食う | あり |
| SGLang | 重い | 低（vLLM同等のPyTorchオーバーヘッド+RadixAttentionのツリー管理コスト） | 高 | 公式イメージあり | VRAM食う | あり |
| TGI | 中〜重 | 中（Rust+Python混成。PyTorchベースだがRust層で一部最適化） | 中 | 公式イメージあり | やや重い | あり |
| LocalAI | 中 | 中〜高（内部llama.cpp利用だがGo製ラッパー分のCPU/メモリ消費あり） | 中 | 公式イメージあり | 向いてる | あり |
| TensorRT-LLM | 重い | 高（Nvidia GPU のパフォーマンス最適化には一番よいと思われる。未着手。） | 高 | 公式イメージあり | 向いてる | あり |

> RTX 5090の32GB VRAMを1バイトでも多くLLMに使いたい場合、llama.cpp直実行のLDIEはロスが少なそう。

## LDIEの強み

- **最小オーバーヘッド**: llama.cppのCUDAバイナリをDocker直実行。間にGo/Python/PyTorchが挟まらない
- **`.env`だけで全制御**: イメージバージョン・ポート・バインドアドレス・推論パラメータ・API Key
- **LDIE命名規則**: ホスト側/コンテナ側の区別が名前で明確（`DOCKER_HOST_` vs `LLAMA_CONTAINER_`）
- **RTX 5090最適化済み**: batch-size/ubatch-size/threads等がチューニング済みのdocker-compose.high.yml

## 📖 ドキュメント

### 利用ガイド

| カテゴリ | 内容 | リンク |
|---|---|---|
| Quick Start | クイックスタート | [README.mdのクイックスタート](README.md) |
| テキスト生成 LLM | llama.cpp + Docker によるテキスト生成 | [DOCS/text-llm/](DOCS/text-llm/README.md) |
| OpenClaw連携 | 他PC(Ubuntu)のOpenClawにローカルLLMを提供 | [DOCS/openclaw-integration/](DOCS/openclaw-integration/README.md) |
| Ubuntu Ready | Ubuntu側のインストールからAPI連携までの完全手順 | [DOCS/ubuntu-ready/](DOCS/ubuntu-ready/README.md) |

### リファレンス

| カテゴリ | 内容 | リンク |
|---|---|---|
| LDIE アーキテクチャ | 全ローカル vs 司令塔クラウド+作業役ローカル | [DOCS/LDIE_Architecture.md](DOCS/LDIE_Architecture.md) |
| LDIE 命名規則 | 環境変数・ファイルの命名規則 | [DOCS/LDIE_NamingConvention.md](DOCS/LDIE_NamingConvention.md) |
| モデルセキュリティ評価 | リスク評価・脅威分析・採用判断基準 | [DOCS/LDIE_ModelSecurityAssessment.md](DOCS/LDIE_ModelSecurityAssessment.md) |

詳細は [ドキュメント一覧](DOCS/README.md) を参照してください。


## 🤖 対応モデル一覧

### テキスト生成（llama.cpp）

| モデル | 用途 | サイズ(Q4_K_M) | リスク | .env.example |
|---|---|---|---|---|
| **Gemma 4 31B IT** | 日本語汎用・Dense（[公式](https://huggingface.co/google/gemma-4-31B-it)） | 17.1GB（Q4_K_M） | 低 | `.env.example.gemma4-31b` |

> リスク評価の詳細は [モデルセキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) を参照。
> OpenClawバックエンドには Gemma 3 27B または Qwen3.5-27B を推奨。DeepSeek R1 は非推奨。

---

## 📁 ディレクトリ構成

```
LDIE/
├── LDIE_Infra_Docker/                   # Docker関連をここに集約
│   ├── docker-compose.yml               # GPU版（デフォルト）
│   ├── docker-compose.cpu.yml           # CPU版
│   ├── docker-compose.high.yml          # RTX 5090向け高性能版
│   ├── .env.example.gemma4-31b          # 現行のモデル別環境変数テンプレート
│   └── .env                             # 実行中の環境変数
├── LDIE_TEST_Req/                       # テスト・ベンチマーク用スクリプト
│   ├── test_request_gemma4-31b.py
│   ├── measure_inference_speed.sh
│   └── benchmark_with_log.sh
├── DOCS/
│   ├── README.md                        # ドキュメントハブ
│   ├── LDIE_Architecture.md             # アーキテクチャ（2パターン）
│   ├── LDIE_NamingConvention.md         # 命名規則リファレンス
│   ├── LDIE_ModelSecurityAssessment.md  # モデルセキュリティ評価
│   ├── text-llm/                        # テキスト生成LLMドキュメント
│   ├── openclaw-integration/            # OpenClaw連携ガイド
│   └── ubuntu-ready/                    # Ubuntu側完全手順
├── Archives/                            # 旧モデル/旧構成の退避
└── README.md                            # このファイル/Quick Start
```

# Quick Start

## 1. リポジトリのクローン(API提供側)

```bash
git clone https://github.com/Masamasamasashito/llama_cpp_docker_inference_engine_priv.git
cd llama_cpp_docker_inference_engine_priv
```

## 2. Docker作業ディレクトリに移動(API提供側)

```bash
cd LDIE_Infra_Docker
```

## 3. モデルのダウンロード(API提供側)

`models/` ディレクトリにGGUFファイルを配置します。

```bash
# Gemma 4 31B IT（約17.1GB, Q4_K_M・Dense・公式: huggingface.co/google/gemma-4-31B-it）
curl -L -o models/gemma-4-31B-it-Q4_K_M.gguf https://huggingface.co/unsloth/gemma-4-31B-it-GGUF/resolve/main/gemma-4-31B-it-Q4_K_M.gguf
```

## 4. Ubuntu PC(API利用側)のプライベートIP確認

```bash
# Ubuntu PCのプライベートIP確認
ip addr show
```

```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.200/24 brd 192.168.1.255    ← 自分のプライベートIP
```

## 5. 環境変数の設定(API提供側)

使いたいモデルの `.env.example.*` をコピーして `.env` を作成します。

```bash
# Gemma 4 31B IT の場合
cp .env.example.gemma4-31b .env
```

> `.env.example.*` はセクション構造化されています。
> 詳細は [LDIE 命名規則](DOCS/LDIE_NamingConvention.md) を参照してください。

## 6. （オプション）API Key の生成

- OpenClaw連携やLAN公開する場合は、API Key認証を有効化してください。
- Windows 側の LDIE（llama.cpp サーバー）で使う .env の LLAMA_API_KEY を作ります。

```powershell
# Windows PowerShell
$bytes = New-Object byte[] 32; (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); $hex = -join ($bytes | ForEach-Object { $_.ToString("x2") }); "LLAMA_API_KEY=sk-local-$hex" | Add-Content .env
```

```bash
# macOS / Linux
echo "LLAMA_API_KEY=sk-local-$(openssl rand -hex 32)" >> .env
```

## 7. Dockerホストバインドアドレス設定

DOCKER_HOST_BIND_ADDR=<Ubuntu PC(API利用側)のプライベートIPアドレス>

## 8. 起動(API提供側)Windows

```bash
# GPU版（デフォルト）
docker-compose up -d

# CPU版
docker-compose -f docker-compose.cpu.yml up -d

# RTX 5090向け高性能版
docker-compose -f docker-compose.high.yml up -d
```

## 9. (API提供側)Windows Defender ファイアウォールのローカルネットワークにおける8081ポートとUbuntu PCのプライベートIPを許可

受信の規則で新しい規則を作成し、8081ポートを許可する

1. コントロールパネル > システムとセキュリティ > Windows Defender ファイアウォール > (左ペイン)詳細設定 > ローカルコンピューターのセキュリティが強化されたWindows Defender ファイアウォール > 受信の規則 > 新しい規則
2. 受信の規則 > ポート > 次へ > TCP,特定のローカルポート,8081 > 次へ > 接続を許可する > 次へ > プロファイル > プライベート > 次へ > 名前: LLAMA_API_Port_and_Private_IP > 完了
3. 受信の規則 > LLAMA_API_Port_and_Private_IPを探し、右クリック > プロパティ > スコープ > リモートIPアドレス > これらのIPアドレス > 追加 > このIPアドレスまたはサブネット > Ubuntu PCのプライベートIPを入力 > OK > 適用 > OK

## 10. (API提供側)WindowsのプライベートIPアドレスを確認

```bash
# WindowsのプライベートIPアドレス確認
ipconfig
```

```bash
# 表示例
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.200/24 brd 192.168.1.255    ← 自分のプライベートIP
```

## 11. 動作確認(API提供側)

```bash
# ヘルスチェック（GPU版のデフォルトポートは 8081）
curl http://<WindowsのプライベートIPアドレス>:8081/health

# モデル一覧（API Key認証を有効化した場合）
curl -H "Authorization: Bearer YOUR_API_KEY" http://<WindowsのプライベートIPアドレス>:8081/v1/models
```

`YOUR_API_KEY` には、`LDIE_Infra_Docker/.env` に設定した `LLAMA_API_KEY` の値（例: `sk-local-...`）を入れてください。

## 12. 使い方

### WebUI（ブラウザ）

llama.cppサーバーには**組み込みWebUI**が搭載されています。
ブラウザで以下のURLにアクセスするだけで、ChatGPT風のチャット画面が利用できます。

```
http://<WindowsのプライベートIPアドレス>:8081
```

- テキストファイルやPDFの添付に対応
- 特別なセットアップ不要（サーバー起動後すぐに利用可能）

### API（curl / Python）

```bash
# Chat API（API Key認証あり）
curl -X POST http://<WindowsのプライベートIPアドレス>:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gemma-4-31B-it-Q4_K_M",
    "messages": [
      {"role": "user", "content": "こんにちは、あなたは誰ですか？"}
    ]
  }'
```

### Authorization無し版

```bash
curl -X POST http://<WindowsのプライベートIPアドレス>:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-31B-it-Q4_K_M",
    "messages": [
      {"role": "user", "content": "こんにちは、あなたは誰ですか？"}
    ]
  }'
```

### Authorization有り版（ワンライナー）

```bash
curl -X POST http://<WindowsのプライベートIPアドレス>:8081/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_API_KEY" -d '{"model": "gemma-4-31B-it-Q4_K_M", "messages": [ {"role": "user", "content": "こんにちは、あなたは誰ですか？"} ] }'
```

### Authorization無し版（ワンライナー）

```bash
curl -X POST http://<WindowsのプライベートIPアドレス>:8081/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "gemma-4-31B-it-Q4_K_M", "messages": [ {"role": "user", "content": "こんにちは、あなたは誰ですか？"} ] }'
```

### Pythonテストリクエスト

```bash
# Pythonテストリクエスト
python LDIE_TEST_Req/test_request_gemma3-27b.py
```

### 13. 停止(API提供側)

```bash
docker-compose down
```

## 🔧 モード一覧(API提供側)

| モード | docker-compose | デフォルトポート | 用途 |
|---|---|---|---|
| GPU | `docker-compose.yml` | `8081` | 標準GPU推論 |
| CPU | `docker-compose.cpu.yml` | `8082` | GPU不要の検証用 |
| High | `docker-compose.high.yml` | `8083` | RTX 5090最適化（VRAM 32GB） |
| Agent | `docker-compose.agents.yml` | `8188` | AIエージェント（OpenClaw連携） |

> 各種ポートは `.env` で変更可能です。

## 🔒 セキュリティ

| レイヤー | 対策 |
|---|---|
| バインドアドレス | デフォルト `127.0.0.1`（ローカルのみ）。LAN公開時はプライベートIPを明示指定 |
| API Key認証 | `--api-key` によるBearer Token認証 |
| ファイアウォール | Ubuntu PCのプライベートIPのみ許可（OpenClaw連携時） |
| モデルリスク管理 | [セキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) に基づくモデル選定 |

> LDIE構成では脅威の大半はUbuntu（OpenClaw）側に集中します。Windows（LLMサーバー）側はDocker隔離+多層防御で比較的安全です。
> 詳細は [モデルセキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) および [ネットワーク設定](DOCS/openclaw-integration/02_network_config.md) を参照してください。


## ❓ よくあるトラブル

| 問題 | 原因・対策 |
|---|---|
| GPU効かない | NVIDIA Container Toolkit未導入 / CUDAバージョン不一致。`nvidia-smi` がDocker内で動くか確認 |
| モデルロード失敗 | `.env` の `LLAMA_MODEL_FILE` と `models/` 内のファイル名が一致しているか確認 |
| 応答が遅い | CPU実行になっている可能性。`LLAMA_N_GPU_LAYERS=99` を設定して全レイヤーGPUに |
| ポートに接続できない | GPU版は `8081`、CPU版は `8082`、High版は `8083` がデフォルト。`docker ps` でポート確認 |
| 401 Unauthorized | API Key不一致。`.env` の `LLAMA_API_KEY` とリクエストの `Authorization` ヘッダーを確認 |
| LAN内の他PCから接続不可 | `DOCKER_HOST_BIND_ADDR` がプライベートIPになっているか、ファイアウォールが開いているか確認 |

## メリット・デメリット

**メリット**

- Ollamaより柔軟（パラメータ細かく制御可能）
- OpenAI互換APIで既存ツール・OpenClawと連携しやすい
- Dockerなので再現性が高い
- 組み込みWebUIでブラウザからすぐチャット可能
- `.env` だけで全設定を一元管理（LDIE命名規則）
- モデルのセキュリティリスクを評価・管理できるドキュメント付き

**デメリット**

- モデル管理は手動（GGUFファイルを自分でダウンロード）
- 1コンテナ1モデル（モデル切り替えは再起動が必要）


# OpenClaw起動とLDIEサーバー連携

クイックスタート（手順1〜11）まで完了し、Ubuntu から次が成功していること

```bash
curl -s http://<WindowsのプライベートIPアドレス>:8081/health
```

## Ubuntu PC（OpenClaw）API利用側

1. **環境**: Node.js 22 以上。詳細は [Ubuntu Ready — 環境構築](DOCS/ubuntu-ready/01_environment_setup.md) を参照。
2. **初回セットアップ**: `openclaw onboard` を実行し、`~/.openclaw/openclaw.json` を生成する。
3. **LDIE をプロバイダとして登録**: [OpenClaw設定（Pattern A 例）](DOCS/ubuntu-ready/03_openclaw_config.md) に従い `openclaw.json` を編集する。
   - `models.providers` にプロバイダ（例: `ldie`）を追加し、`baseUrl` を `http://<WindowsのプライベートIP>:8081/v1` にする（末尾は必ず `/v1`）。
   - `apiKey` を Windows の `LDIE_Infra_Docker/.env` の `LLAMA_API_KEY` と**同じ値**にする（未設定の場合は双方とも未設定のまま）。
   - `models[].id` は、Windows で `curl .../v1/models`（要 Bearer）の応答にある **`id` と完全一致**させる（例: Gemma 4 31B Dense なら `gemma-4-31B-it-Q4_K_M`）。
   - `agents.defaults.model.primary` を `プロバイダ名/id` 形式にする（例: `ldie/gemma-4-31B-it-Q4_K_M`）。
   - `contextWindow` は `.env` の `LLAMA_CTX_SIZE` と**同じ数値**にする。OpenClawは最低 16000 トークンが必要なため **16384 以上**にする。Gemma 4 31B では 16384 で不足することがあるため、**32768** を推奨。

### openclaw.json の例（Pattern A・Gemma 4 31B）

`~/.openclaw/openclaw.json` を以下の様に編集します。

```json
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
        "baseUrl": "http://192.168.xxx.xxx:8081/v1",
        "api": "openai-completions",
        "apiKey": "sk-local-your-secret-key-here",
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

- **確認**: `openclaw models list --provider ldie` でモデルが列挙されることを確認する。
- **起動**: ワークスペースで `openclaw` を実行し、会話・自走ができるか試す。詳細は [動作確認・自走テスト](DOCS/ubuntu-ready/04_run_and_test.md)。
- **2回目以降の起動**: `openclaw gateway`

### Windows PC 側（再掲）

LAN 公開・API Key・ファイアウォールは [OpenClaw連携 セットアップ手順](DOCS/openclaw-integration/01_setup_guide.md) の Step 1〜3 に従う。ネットワークの細部は [ネットワーク設定](DOCS/openclaw-integration/02_network_config.md)、全体像は [LDIE アーキテクチャ](DOCS/LDIE_Architecture.md) を参照。

# OpenClaw Update

```bash
npm update -g @anthropic-ai/openclaw
```

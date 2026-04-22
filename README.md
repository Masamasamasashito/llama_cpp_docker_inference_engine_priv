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

> 注意: Ubuntu のプライベートIPが再起動等で変わる場合、後続の「Windows Defender ファイアウォールで許可したリモートIP（Ubuntu側IP）」の再設定が必要です。

## 5. 環境変数の設定(API提供側)

使いたいモデルの `.env.example.*` をコピーして `.env` を作成します。

```bash
# Gemma 4 31B IT の場合
cp .env.example.gemma4-31b .env
# Qwen3.6-27B-FP8 の場合
cp .env.example.qwen36-27b-fp8 .env
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

## 7. (API提供側)WindowsのプライベートIPアドレスを確認

```bash
# WindowsのプライベートIPアドレス確認
ipconfig
```

```bash
# 表示例
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.200/24 brd 192.168.1.255    ← 自分のプライベートIP
```

## 8. Dockerホストバインドアドレス設定

API提供側のWindows PC（Docker/llama.cpp を起動する側）の `LDIE_Infra_Docker/.env` で記載を更新します。

```bash
DOCKER_HOST_BIND_ADDR=<Windows PC(API提供側)のプライベートIPアドレス>
```

（補足）127.0.0.1 はローカル専用、192.168.x.x はLAN公開用

## 9. 起動(API提供側)Windows

```bash
# GPU版（デフォルト）
docker-compose up -d

# CPU版
docker-compose -f docker-compose.cpu.yml up -d

# RTX 5090向け高性能版
docker-compose -f docker-compose.high.yml up -d
```

## 10. (API提供側)Windows Defender ファイアウォールのローカルネットワークにおける8081ポートとUbuntu PCのプライベートIPを許可

受信の規則で新しい規則を作成し、8081ポートを許可する

1. コントロールパネル > システムとセキュリティ > Windows Defender ファイアウォール > (左ペイン)詳細設定 > ローカルコンピューターのセキュリティが強化されたWindows Defender ファイアウォール > 受信の規則 > 新しい規則
2. 受信の規則 > ポート > 次へ > TCP,特定のローカルポート,8081 > 次へ > 接続を許可する > 次へ > プロファイル > プライベート > 次へ > 名前: LLAMA_API_Port_and_Private_IP > 完了
3. 受信の規則 > LLAMA_API_Port_and_Private_IPを探し、右クリック > プロパティ > スコープ > リモートIPアドレス > これらのIPアドレス > 追加 > このIPアドレスまたはサブネット > Ubuntu PCのプライベートIPを入力 > OK > 適用 > OK

> 注意: Ubuntu のプライベートIPが変わった場合は、この規則の「リモートIPアドレス」を新しいIPに更新してください（旧IPのままだと OpenClaw から接続できません）。

## 12. 動作確認(API提供側)

```bash
# ヘルスチェック（GPU版のデフォルトポートは 8081）
curl http://<WindowsのプライベートIPアドレス>:8081/health

# モデル一覧（API Key認証を有効化した場合）
curl -H "Authorization: Bearer YOUR_API_KEY" http://<WindowsのプライベートIPアドレス>:8081/v1/models
```

`YOUR_API_KEY` には、`LDIE_Infra_Docker/.env` に設定した `LLAMA_API_KEY` の値（例: `sk-local-...`）を入れてください。

## 13. 使い方

### WebUI（ブラウザ）

llama.cppサーバーには**組み込みWebUI**が搭載されています。
ブラウザで以下のURLにアクセスすると、ChatGPT風のチャット画面が利用できます。

`LDIE_Infra_Docker/.env` で **`LLAMA_API_KEY` を設定してサーバーを起動している場合**、llama.cpp のブラウザUIでは**チャットを始める前に、画面上でAPIキーを入力**する必要があります。`LLAMA_API_KEY` に設定した値（例: `sk-local-...`）と同じ文字列を入力してください。`LLAMA_API_KEY` が空（未設定）の場合は、WebUIでも認証なしで利用できます。

```
http://<WindowsのプライベートIPアドレス>:8081
```

- テキストファイルやPDFの添付に対応
- サーバー起動後すぐにURLを開ける（API Key認証を有効にしている場合は、上記のとおりWebUIでキー入力が必要）

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

## 14. 停止(API提供側)

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
| ファイアウォール | Ubuntu PCのプライベートIPのみ許可（OpenClaw連携時）。UbuntuのIPが変わったら受信規則のリモートIPを更新 |
| モデルリスク管理 | [セキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) に基づくモデル選定 |

> LDIE構成では脅威の大半はUbuntu（OpenClaw）側に集中します。Windows（LLMサーバー）側はDocker隔離+多層防御で比較的安全です。
> 詳細は [モデルセキュリティ評価](DOCS/LDIE_ModelSecurityAssessment.md) および [ネットワーク設定](DOCS/openclaw-integration/02_network_config.md) を参照してください。

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
npm install -g openclaw@latest
```

## OpenClaw + Discord 連携手順

Ubuntu 24.04.4 LTS の OpenClaw を Discord から使うための手順です。(Discord) Bot トークンは秘密情報なので、`README.md` やリポジトリに書かないでください。

### 大まかな流れ

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリと **Bot** を作成し、**(Discord) Bot トークン** を取得する。
2. **Privileged Gateway Intents** を設定する（特に **Message Content Intent** はメッセージ本文取得に必要）。
3. (Discord) Bot を自分の **(Discord) サーバー**（ギルド）に招待し、**サーバーID** と **ユーザーID** を控える（後述「(Discord) Bot を (Discord) サーバーに招待し、サーバーIDとユーザーIDを控える」）。
4. `~/.openclaw/openclaw.json` の **`channels` → `discord`** に、(Discord) Bot トークン・サーバー・ユーザー（許可リスト）を書き込む。
5. **DM** または **CLI** で OpenClaw の **ペアリング** を承認する。
6. `openclaw gateway` を起動し、Discord 側で応答を確認する。

### Discord Developer Portal: アプリ・(Discord) Bot・トークン

1. [Discord Developer Portal](https://discord.com/developers/applications) にログインし、`New Application` でアプリを作成する。分かりやすい名前（例: `OpenclawGatewayApp`）を付ける。
2. 左メニュー **Bot** → `Add Bot` で Bot を有効化する。ユーザー名は例として **`OpenclawGatewayBot`**（既に使用済みなら別名でよい）。
3. 同じ **Bot** ページで **Reset Token** / **Copy** により **(Discord) Bot トークン** を取得し、安全な場所に保管する（再表示されない）。
4. **Public Bot** は用途に応じて ON/OFF（個人運用なら OFF 推奨）。

OpenClaw は Ubuntu 上で `openclaw gateway` を動かし、この **(Discord) Bot トークン** で Discord API に接続してメッセージを中継します。Bot 本体は Discord 公式の仕組みで作る **通常の Bot** であり、OpenClaw が別途配布する「専用 Bot」ではありません。

### Privileged Gateway Intents

- **設定場所**: 対象アプリ → 左メニュー **Bot** → **Privileged Gateway Intents**
- **Presence Intent** / **Server Members Intent** は、必要な機能があるときだけオンにする。
- **Message Content Intent** をオンにする（チャンネルのメッセージ本文を読む場合に必須）。

### (Discord) Bot を (Discord) サーバーに招待し、(Discord) サーバーIDと自身の(Discord) ユーザーIDを控える

#### 招待リンクを作る（OAuth2 / URL Generator）

1. Developer Portal で対象アプリを開き、左メニュー **OAuth2** → **URL Generator** を開く。
2. **SCOPES** で次にチェックする: 
   - `bot`、（推奨）
   - `applications.commands`
3. **BOT PERMISSIONS** 次をオンにする:
   - General Permissions
    - `View Channels`（チャンネルを見る）
   - Text Permissions
    - `Send Messages`（メッセージを送信する）
    - `Embed Links`（リンクを埋め込む）
    - `Attach Files`（ファイルを添付する）
    - `Read Message History`（メッセージ履歴を読む）
    - `Mention Everyone`（全員にメンションする）
    - `Add Reactions`（リアクションを追加する）※任意
4. ページ最下部の **生成 URL をコピー**し、**ブラウザの別タブ**で開いて、`Add to server` でサーバーを選び、`Continue` を押して、Authorizeする。Go to Serverを押すと、Botがサーバーに追加されます。

**注意**: URL Generator に **保存ボタンはない**ため、左メニューを切り替えるとスコープや権限の選択が消えることがある。**生成 URL をコピーしてから**別画面へ移るか、このページを離れずに招待まで完了させる。

#### 開発者モードをオンにする（Discord クライアント）

ID をコピーするには **開発者モード**が必要です。

1. Discord アプリ左下の **ユーザー設定**（歯車）を開く。
2. 左メニュー **Developer** を開く。
3. **開発者モード**（Developer Mode）を **オン** にする。

#### サーバーID・ユーザーIDをコピーする

- **サーバーID**: 左のサーバー一覧で **サーバーアイコンを右クリック** → **サーバーIDをコピー**
- **ユーザーID**: **自分の名前またはアバターを右クリック** → **ユーザーIDをコピー**

#### メモしておくもの（チェックリスト）

- [ ] **(Discord) Bot トークン**（上記の手順で取得したもの）
- [ ] **サーバーID**（数字の文字列）
- [ ] **ユーザーID**（許可する自分のユーザーID）

### `openclaw.json` に Discord を書き込む

編集するファイル: `~/.openclaw/openclaw.json`（`openclaw onboard` 後に存在する想定）。

`channels` → `discord` に、概ね次のような意味で値を入れる（**キー名や入れ子は OpenClaw のバージョンで異なる場合がある**ので、手元の雛形・エラーメッセージ・公式ドキュメントを優先する）。

| 項目 | 例の意味 |
|------|----------|
| `token` | (Discord) Bot トークン（OpenClaw がその Bot として Discord にログインする） |
| `enabled` | `true` で Discord 連携を有効化 |
| `groupPolicy` | `"allowlist"` で「許可したユーザーだけ」に制限 |
| `guilds` | 利用する **サーバーID** を登録 |
| `requireMention` | `false` なら @Bot なしでも反応させられる（運用に合わせて変更） |
| `users` | 許可する **ユーザーID** のリスト |

イメージ（**実際の JSON 構造は環境に合わせて編集**）:

```jsonc
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "PASTE_BOT_TOKEN",
      "groupPolicy": "allowlist",
      "guilds": {
        "YOUR_GUILD_ID": {
          "requireMention": false,
          "users": ["YOUR_USER_ID"]
        }
      }
    }
  }
}
```

意図としては、「この (Discord) Bot トークンで、このサーバーにいる、このユーザーからのメッセージにだけ反応する」という設定を `openclaw.json` に保存する、ということです。変更後は `openclaw gateway` を再起動して反映します。

### ペアリングの承認

OpenClaw の指示に従い、**DM** または **CLI** でペアリング（信頼できるクライアントの登録）を承認します。ここまで済むと、Discord 経由でエージェントを操作できる状態になります。

### 起動と動作確認

- 通常は `openclaw gateway` でゲートウェイを起動する。常駐させる場合は `tmux` / `systemd` などで管理する。
- Discord で Bot がオンラインになること、テストチャンネルで応答があることを確認する。
- 応答しない場合は、(Discord) Bot トークン、Intent、チャンネル権限、`openclaw.json` の ID、ゲートウェイのログを順に確認する。

### セキュリティ運用

- **(Discord) Bot トークン**の漏えい時はすぐ **Reset Token** し、`openclaw.json` を更新してゲートウェイを再起動する。
- Bot 権限は必要最小限にし、公開サーバーでは利用チャンネルを限定する。

### 補足（用語）

- **OS 内の Discord アプリ**: 人間が使うクライアント。(Discord) Bot トークンや Portal の設定はここには保存されない。
- **Discord サーバー（ギルド）**: Bot を招待して運用する場所。メッセージの送受信は Discord クラウド経由で行われる。

### Discord での最初の会話（メンション名・確認プロンプト例）

本 README の例どおり、Developer Portal で Bot のユーザー名を **`OpenclawGatewayBot`** にしている場合、チャンネルでメンションする表記は **`@OpenclawGatewayBot`** になる（別名にした場合はその名前の**@**表記に読み替える）。入力欄で `@` を打つと候補が出るので、そこで正しい表記を確認してもよい。

`openclaw.json` で `requireMention` を `false` にしている場合は **メンションなし**でも反応する設定になり得るが、初回の切り分けでは **`@OpenclawGatewayBot` を付けて送る**と、Bot 宛てであることがはっきりする。

**確認用プロンプトの例（コピーして使い、必要に応じて Bot 名を置き換え）:**

```
@OpenclawGatewayBot 接続テストです。短く返信してください。
```

```
@OpenclawGatewayBot 動作確認です。あなたは OpenClaw 経由で応答していますか？ はい／いいえ、と一文で答えてください。
```

---

# ❓ よくあるトラブル

## LDIE（llama.cpp）関連

| 問題 | 対策 |
|---|---|
| GPU効かない | NVIDIA Container Toolkit未導入 / CUDAバージョン不一致。`nvidia-smi` がDocker内で動くか確認 |
| モデルロード失敗 | `.env` の `LLAMA_MODEL_FILE` と `models/` 内のファイル名が一致しているか確認 |
| 応答が遅い | CPU実行中の可能性。`LLAMA_N_GPU_LAYERS=99` を設定 |
| ポートに接続できない | GPU版 `8081` / CPU版 `8082` / High版 `8083` がデフォルト。`docker ps` でポート確認 |
| 401 Unauthorized | API Key不一致。`.env` の `LLAMA_API_KEY` と Authorization ヘッダーを確認 |

## OpenClaw / LAN関連

| 問題 | 対策 |
|---|---|
| LAN内の他PCから接続不可 | `DOCKER_HOST_BIND_ADDR` がプライベートIP設定か確認。ファイアウォール受信規則確認。Ubuntu再起動後は受信規則の許可IP（RemoteAddress）を更新 |
| OpenClaw GUI は動くが応答しない | `openclaw gateway` 確認。`~/.openclaw/openclaw.json` の構文エラー確認 |
| `discord failed to load` / `Cannot find module` | OpenClaw 依存関係不足。`npm cache clean --force` → `npm install -g openclaw@latest` で再インストール |

## Discord Bot関連

| 問題 | 対策 |
|---|---|
| **Bot がオンラインにならない** | [Discord Bot オンライン化チェックリスト](#discord-bot-オンライン化チェックリスト-1)参照 |
| **Bot は起動するが反応しない** | Intent 設定確認。ゲートウェイ再起動。`openclaw.json` のサーバーID・ユーザーID 確認 |

---

## Discord Bot オンライン化チェックリスト

Bot がオンラインにならない場合、以下を **上から順に** 確認してください。

### ❶ Bot がサーバーに招待されているか確認（基本）

Discord クライアントを開き、対象サーバーのメンバーリストに Bot が表示されるか確認します。

**見えない場合は招待する：**
1. Discord Developer Portal → 対象アプリ → **OAuth2** → **URL Generator**
2. SCOPES で以下をチェック:
   - `bot`
   - `applications.commands`
3. BOT PERMISSIONS で以下をチェック:
   - General: `View Channels`
   - Text: `Send Messages`, `Embed Links`, `Read Message History`
4. ページ下部の **生成 URL をコピー** → ブラウザで開く
5. **Add to server** でサーバーを選択 → **Authorize**

### ❷ `openclaw.json` が存在して、JSON 構文は正しいか確認（基本）

```bash
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json'))" && echo "OK" || echo "ERROR"
```

**ERROR が出た場合** — JSON ファイルの括弧やカンマを確認：
```bash
cat ~/.openclaw/openclaw.json
```

テキストエディタで開き、構文エラー（特に最後の `}` など）を修正してください。

### ❸ `openclaw.json` の discord セクション設定を確認

`~/.openclaw/openclaw.json` を開き、以下のような構造か確認：

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_LATEST_BOT_TOKEN",
      "groupPolicy": "allowlist",
      "guilds": {
        "YOUR_GUILD_ID": {
          "requireMention": false,
          "users": ["YOUR_USER_ID"]
        }
      }
    }
  }
}
```

チェックリスト：
- [ ] `enabled` は `true` か？
- [ ] `token` に Bot トークンが入っているか？（空白でないか？）
- [ ] `YOUR_GUILD_ID` が数字か？（Discord サーバーID）
- [ ] `YOUR_USER_ID` が数字か？（自分の Discord ユーザーID）

### ❹ Discord Developer Portal で Intent を有効化確認

**対象アプリ → Bot → Privileged Gateway Intents**：

- ✅ **Message Content Intent** → ON？
- ✅ **Presence Intent** → ON？
- ✅ **Server Members Intent** → ON？

**1つでも OFF なら ON に切り替えて保存。**

### ❺ `openclaw gateway` を起動してログを確認

```bash
cd ~/.openclaw
openclaw gateway
```

**ログの見方** — ターミナルのコンソール出力を確認。ターミナルウィンドウに流れるテキストを見てください。

**正常な場合** — こんなメッセージが出る：
```
[OpenClaw Gateway] Connected to Discord
[OpenClaw Gateway] Ready as @YourBotName
```

**トークン失効の場合** — このエラーが出る：
```
[Discord.js] Error: Invalid token provided
[Discord.js] Error: 401 Unauthorized
```

この場合は→ **ステップ❻へ**

**その他のエラー** — エラーメッセージを確認して対応

### ❻ Bot トークンが失効していないか（詳細診断）

ステップ❺で `Invalid token` エラーが出た場合のみ実行。

**トークン再発行手順：**

1. Discord Developer Portal → 対象アプリ → **Bot** → **Token** セクション
2. **Reset Token** をクリック → **Yes, do it!** で確認
3. 新しいトークンが表示される → すぐに **Copy** でコピー（再度表示されません）
4. `~/.openclaw/openclaw.json` をテキストエディタで開く
5. `channels.discord.token` の値を新しいトークンで置き換え
6. ファイル保存 → ターミナルで `openclaw gateway` を再起動

### トークン管理のベストプラクティス

- Reset Token 後、古いトークンを記録している箇所がないか確認（メモ、スクリプト等）
- トークン値を GitHub にコミットしない
- トークン漏えいの疑いがあれば、直ちに Reset Token を実行


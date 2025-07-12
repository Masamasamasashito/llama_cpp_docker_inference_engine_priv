# 🦙 Llama.cpp Docker Compose セットアップ

WindowsでLlama.cppを簡単に動かすためのDocker Composeセットアップです。  
WebUIはオプションで利用可能、APIサーバーのみの運用も可能です。

---

## 📁 ディレクトリ構成

```
llama-cpp-docker-compose/
├── models/           # モデル(GGUF)ファイル配置用
├── logs/             # サーバーログ保存用
├── webui-data/       # WebUI用データ（WebUI利用時のみ）
├── .env.example      # 環境変数サンプル
├── .gitignore
├── docker-compose.yml
├── docker-compose.cpu.yml
├── docker-compose.gpu.yml
└── README.md
```

---

## 🚀 セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/llama-cpp-docker-setup.git
cd llama-cpp-docker-setup
```

### 2. モデルファイルの配置

`models/`ディレクトリにGGUFファイルを配置してください。

例：
- `llama-2-7b-chat.Q4_K_M.gguf`
- `llama-2-13b-chat.Q4_K_M.gguf`

#### ダウンロード例（Gemma 3n E2B モデル）

```bash
curl -L -o gemma3n-e2b-fixed.gguf https://huggingface.co/unsloth/gemma-3n-E2B-it-GGUF/resolve/main/gemma-3n-E2B-it-UD-Q4_K_XL.gguf
# ダウンロード後、models/ ディレクトリに移動してください
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、モデルファイル名などを設定してください。

```bash
cp .env.example .env
# LLAMA_MODEL_FILE などを編集
```

### 4. 実行（GPU版）

```bash
docker-compose up -d
```

- サーバーはデフォルトでポート8081（ホスト側）で起動します。
- APIエンドポイント例: http://localhost:8081

> CPU環境で動かしたい場合は `docker-compose.cpu.yml` を参照してください。

---

## 🛠️ 使用方法

### API経由でテキスト生成

```bash
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "n_predict": 100,
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

### チャット形式

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### WebUI

WebUIプロファイルを使用している場合：  
[http://localhost:3000](http://localhost:3000)

---

## ⚙️ 設定オプション

### 主要パラメータ

- `--ctx-size`: コンテキストサイズ（デフォルト: 2048）
- `--n-parallel`: 並列処理数（デフォルト: 1）
- `--n-gpu-layers`: GPU使用レイヤー数（GPU版のみ）

### 環境変数（.envで設定）

- `LLAMA_MODEL_FILE`: モデルファイル名
- `LLAMA_CTX_SIZE`: コンテキストサイズ
- `LLAMA_N_PARALLEL`: 並列処理数
- `LLAMA_PORT`: APIポート番号
- `LLAMA_N_GPU_LAYERS`: GPUレイヤー数（GPU版のみ）

---

## 🧩 トラブルシューティング

### メモリ不足

Docker Desktopのメモリ設定を8GB以上に増やしてください。

### GPU使用時

1. NVIDIA Container Toolkitがインストールされていることを確認
2. Docker DesktopでGPUサポートが有効になっていることを確認

### ログ確認

```bash
docker-compose logs -f llama-cpp
```

---

## 🛑 停止方法

```bash
docker-compose down
```

---

## ➕ モデルの追加

1. `models/`ディレクトリにGGUFファイルを配置
2. `.env`ファイルの`LLAMA_MODEL_FILE`を更新
3. `docker-compose restart`

---

## 📄 ライセンス

このセットアップファイルはMITライセンスです。  
使用するモデルファイルは、それぞれのライセンスに従ってください。

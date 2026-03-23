<div align="center">

# 🦙 Llama.cpp Docker Compose セットアップ

<!-- ヘッダー画像例（必要に応じてURLを差し替えてください） -->

![](https://github.com/user-attachments/assets/5960ce66-a66f-44a8-b6bc-413449fb1d8e)

<p>
  <img src="https://img.shields.io/badge/Docker-blue?logo=docker" />
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Windows-11-blue?logo=windows" />
</p>

</div>

Githubリポジトリ : https://github.com/Sunwood-ai-labs/llama-cpp-docker-compose

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

### 4. 実行

```bash
# GPU
docker-compose up -d

# CPU
docker-compose -f docker-compose.cpu.yml up -d

# high
docker-compose -f docker-compose.high.yml up -d
```

### 5. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8080/health

# モデル一覧
curl http://localhost:8080/v1/models
```

### 6. 使い方

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma3n-e2b-fixed.gguf",
    "messages": [
      {
        "role": "user",
        "content": "こんにちは、あなたは誰ですか？"
      }
    ]
  }'
```

### 7. 構成

```bash
models/     ← モデル置く（必須）
logs/       ← ログ
.env        ← 設定
```

モード

|モード|用途|
|---|---|
|GPU|普通|
|CPU|検証用|
|high|4090用|

### 8. 停止

```bash
docker-compose down
```

### 9. よくあるハマり

#### ① GPU効かない

原因：

- NVIDIA Container Toolkit未導入
- CUDAバージョン不一致

対策：

- `nvidia-smi`がDocker内で動くか確認

#### ② モデルロード失敗

原因：

- .env のファイル名ミス
- パス違い

確認：

- `ls models/`

#### ③ 遅い

仮説：

- CPU実行になってる
- GPUレイヤー不足

調整：

- LLAMA_N_GPU_LAYERS=35

### 10. 実務視点の評価（重要）

メリット

- Ollamaより柔軟
- OpenAI互換APIで連携しやすい
- Dockerなので再現性高い

デメリット

- モデル管理は手動
- UIなし（完全API）
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
# ここに実行コマンドを記載
```

<!-- 必要に応じてAPI使用例やスクリーンショット、詳細手順、FAQ等を今後追記してください -->

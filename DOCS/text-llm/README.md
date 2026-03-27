# テキスト生成 LLM（llama.cpp + Docker）

llama.cpp をDocker上で動かし、OpenAI互換APIとしてテキスト生成を行うセクションです。

---

## ドキュメント

- [セットアップ手順](01_setup_guide.md) - モデルダウンロードからAPI実行まで
- [利用可能モデル一覧](02_available_models.md) - 対応モデル・量子化・RTX 5090ベンチマーク
- [WebUIガイド](03_webui_guide.md) - ブラウザからChatGPT風チャット（認証・機能一覧・使い分け）

## クイックスタート

```bash
# 1. Docker作業ディレクトリに移動
cd LDIE_Infra_Docker

# 2. envファイルをコピー（例: Qwen3.5-9B）
cp .env.example.qwen3.5-9b .env

# 3. モデルダウンロード
curl -L -o models/Qwen3.5-9B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf

# 4. 起動
docker-compose up -d

# 5. テスト（リポジトリルートに戻って実行）
cd ..
python LDIE_TEST_Req/test_request_qwen3.5-9b.py
```

## 関連ファイル（LDIE_Infra_Docker/ 内）

| ファイル | 説明 |
|---|---|
| `docker-compose.yml` | GPU版（デフォルト） |
| `docker-compose.cpu.yml` | CPU版 |
| `docker-compose.high.yml` | RTX 5090向け高性能版 |
| `.env.example.*` | モデル別環境変数テンプレート |
| `LDIE_TEST_Req/` | クライアントサンプルコード |

---

[トップに戻る](../../README.md) | [ドキュメント一覧](../README.md)

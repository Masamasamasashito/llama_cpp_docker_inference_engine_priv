# テキスト生成 LLM（llama.cpp + Docker）

llama.cpp をDocker上で動かし、OpenAI互換APIとしてテキスト生成を行うセクションです。

---

## ドキュメント

- [セットアップ手順](01_setup_guide.md) - モデルダウンロードからAPI実行まで
- [利用可能モデル一覧](02_available_models.md) - 対応モデル・量子化・RTX 5090ベンチマーク

## クイックスタート

```bash
# 1. envファイルをコピー（例: Qwen3.5-9B）
cp .env.example.qwen3.5-9b .env

# 2. モデルダウンロード
curl -L -o models/Qwen3.5-9B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf

# 3. 起動
docker-compose up -d

# 4. テスト
python example/test_request_qwen3.5-9b.py
```

## 関連ファイル

| ファイル | 説明 |
|---|---|
| `docker-compose.yml` | GPU版（デフォルト） |
| `docker-compose.cpu.yml` | CPU版 |
| `docker-compose.high.yml` | RTX 5090向け高性能版 |
| `.env.example.*` | モデル別環境変数テンプレート |
| `example/` | クライアントサンプルコード |

---

[トップに戻る](../../README.md) | [ドキュメント一覧](../README.md)

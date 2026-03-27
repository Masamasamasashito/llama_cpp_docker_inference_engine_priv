# セットアップ手順

モデルのダウンロードからAPI実行までの手順です。

---

## 1. モデルのダウンロード

`models/` ディレクトリにGGUFファイルをダウンロードします。

### Qwen3.5-27B（Q4_K_M: 16.7GB）

```bash
curl -L -o models/Qwen3.5-27B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/resolve/main/Qwen3.5-27B-Q4_K_M.gguf
```

### Qwen3.5-9B（Q4_K_M: 5.68GB）

```bash
curl -L -o models/Qwen3.5-9B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf
```

> 別の量子化を使いたい場合は [利用可能モデル一覧](02_available_models.md) を参照してください。

---

## 2. 環境変数の設定

使いたいモデルに対応する `.env.example.*` を `.env` にコピーします。

```bash
# Qwen3.5-27B の場合
cp .env.example.qwen3.5-27b .env

# Qwen3.5-9B の場合
cp .env.example.qwen3.5-9b .env

# Gemma 3n E2B の場合（既存）
cp .env.example.gemma3n-e2b .env
```

---

## 3. サーバー起動

```bash
# GPU版（デフォルト）
docker-compose up -d

# CPU版
docker-compose -f docker-compose.cpu.yml up -d

# RTX 5090向け高性能版
docker-compose -f docker-compose.high.yml up -d
```

---

## 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8081/health

# モデル一覧
curl http://localhost:8081/v1/models
```

> ポートは `docker-compose.yml` によって異なります。
> GPU版: `8081`、CPU版: `8082`、High版: `8083`（.envの`DOCKER_HOST_PORT_LLAMA`に依存）

---

## 5. クライアントからテスト

```bash
# Qwen3.5-27B
python example/test_request_qwen3.5-27b.py

# Qwen3.5-9B
python example/test_request_qwen3.5-9b.py

# Gemma 3n E2B（既存）
python example/test_request_gemma3n-e2b.py
```

---

## 6. 停止

```bash
docker-compose down
```

---

## モデル切り替え

別のモデルに切り替えるには、サーバーを停止してから `.env` を差し替えて再起動します。

```bash
docker-compose down
cp .env.example.qwen3.5-9b .env
docker-compose up -d
```

---

## トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| モデルロード失敗 | `.env` の `LLAMA_MODEL_FILE` と `models/` 内のファイル名が一致しているか確認 |
| OOM（メモリ不足） | 小さい量子化（Q3_K_M等）に変更、または `LLAMA_N_GPU_LAYERS` を減らす |
| GPU効かない | `nvidia-smi` がDocker内で動くか確認。NVIDIA Container Toolkit要 |
| 応答が遅い | CPU実行になっている可能性。`LLAMA_N_GPU_LAYERS=99` を確認 |
| ポート接続できない | GPU版は `8081`、CPU版は `8082`、High版は `8083` がデフォルト。`docker ps` でポート確認 |

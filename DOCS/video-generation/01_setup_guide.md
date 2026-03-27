# 動画生成 セットアップ手順

ComfyUI を使った動画生成環境の構築手順です。
RTX 5090（VRAM 32GB）を前提としています。

> テキスト生成LLM（llama.cpp）のセットアップは [こちら](../text-llm/01_setup_guide.md) を参照してください。

---

## 前提条件

- NVIDIA GPU（RTX 5090推奨、VRAM 16GB以上）
- Docker + NVIDIA Container Toolkit
- Python 3.10以上（ComfyUI用）

---

## 1. ComfyUI のインストール

### Docker を使う場合

```bash
docker run -it --gpus all -p 8188:8188 \
  -v $(pwd)/comfyui-models:/root/ComfyUI/models \
  ghcr.io/ai-dock/comfyui:latest
```

### 手動インストールの場合

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py --listen 0.0.0.0
```

ブラウザで `http://localhost:8188` にアクセスして起動を確認します。

---

## 2. モデルのダウンロード

### LTX-Video

```bash
# ComfyUI/models/checkpoints/ に配置
cd ComfyUI/models/checkpoints/
# HuggingFace からダウンロード（最新版はHFページで確認）
```

### Wan 2.1/2.2

```bash
# Wan 14B（高品質版）
cd ComfyUI/models/checkpoints/
# HuggingFace からダウンロード
```

### HunyuanVideo 1.5

```bash
# カスタムノードのインストールが必要
cd ComfyUI/custom_nodes/
git clone https://github.com/Tencent/HunyuanVideo-ComfyUI.git
# モデルファイルは ComfyUI/models/ 配下に配置
```

---

## 3. 動画生成の実行

1. ComfyUI の Web UI（`http://localhost:8188`）を開く
2. ワークフロー（.json）をロード
3. プロンプトを入力して「Queue Prompt」で生成開始
4. 出力は `ComfyUI/output/` に保存される

---

## 4. VRAM使用量の目安

| モデル | VRAM使用量 | RTX 5090での余裕 |
|---|---|---|
| LTX-Video | ~8GB | 24GB余裕 |
| Wan 2.2 (14B) | ~16GB | 16GB余裕 |
| HunyuanVideo 1.5 | ~16GB | 16GB余裕 |

RTX 5090のNVFP4/NVFP8対応により、さらにVRAM使用量を削減可能です。

---

## トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| ComfyUI起動しない | Python 3.10以上か確認。`pip install -r requirements.txt` を再実行 |
| GPU認識しない | `nvidia-smi` 確認。NVIDIA Container Toolkit のインストールが必要 |
| OOM（メモリ不足） | 解像度を下げる、またはより小さいモデル（LTX-Video, Wan 1.3B）を使用 |
| 生成が遅い | GPU使用率確認。CPU実行になっていないか `nvidia-smi` で確認 |
| カスタムノードエラー | `pip install -r requirements.txt` をカスタムノードディレクトリ内で実行 |

---

[利用可能モデル一覧](02_available_models.md) | [動画生成トップ](README.md) | [ドキュメント一覧](../README.md)

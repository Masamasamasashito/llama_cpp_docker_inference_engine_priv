# Example — テストリクエストスクリプト

LDIEサーバーおよびComfyUIへのテストリクエストスクリプト集です。
セットアップや詳細な使い方は [../README.md](../README.md) を参照してください。

## テキスト生成（llama.cpp API）

| ファイル | モデル | 用途 |
|---|---|---|
| `test_request_gemma3-27b.py` | Gemma 3 27B | 日本語汎用（安全性最高） |
| `test_request_gemma3n-e2b.py` | Gemma 3n E2B | 軽量テスト |
| `test_request_qwen3.5-27b.py` | Qwen3.5-27B | 日本語汎用 |
| `test_request_qwen3.5-9b.py` | Qwen3.5-9B | 軽量・高速 |
| `test_request_qwen3-32b.py` | Qwen3-32B | 最高品質 |
| `test_request_qwen3-coder-30b.py` | Qwen3-Coder-30B | コーディング特化 |
| `test_request_deepseek-r1-32b.py` | DeepSeek R1 32B | 推論・分析 |
| `test_request_logprobs.py` | （任意） | Chat API vs Completion API のlogprobs比較 |

## 動画生成（ComfyUI API）

| ファイル | モデル | 用途 |
|---|---|---|
| `test_request_ltx-video.py` | LTX-Video | 最速動画生成 |
| `test_request_wan-video-14b.py` | Wan 2.2 (14B) | 最高品質動画 |
| `test_request_wan-video-1.3b.py` | Wan 2.1 (1.3B) | 軽量版動画 |
| `test_request_hunyuanvideo-1.5.py` | HunyuanVideo 1.5 | 人物特化動画 |

## 環境変数

テキスト生成スクリプトは以下の環境変数で接続先を変更できます。

```bash
# デフォルト: http://localhost:8081
LDIE_BASE_URL=http://192.168.1.100:8081 LDIE_API_KEY=sk-local-xxx python test_request_gemma3-27b.py
```

動画生成スクリプトは `COMFYUI_BASE_URL`（デフォルト: `http://localhost:8188`）で変更可能です。

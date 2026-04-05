# 利用可能モデル一覧

本リポジトリで動作確認済みのモデル一覧です。
すべてGGUF形式で、llama.cpp上で動作します。

---

## Qwen3.5-27B

| 項目 | 内容 |
|---|---|
| モデル名 | Qwen3.5-27B |
| パラメータ数 | 27B |
| 推奨量子化 | Q4_K_M（16.7GB） |
| HuggingFace | https://huggingface.co/unsloth/Qwen3.5-27B-GGUF |
| env設定ファイル | `.env.example.qwen3.5-27b` |
| クライアント例 | `LDIE_TEST_Req/test_request_qwen3.5-27b.py` |
| 必要VRAM目安 | 約18GB以上（Q4_K_M, 全レイヤーGPU時） |

### 利用可能な量子化バリエーション

| 量子化 | サイズ | 備考 |
|---|---|---|
| UD-IQ2_XXS | 8.57 GB | 最小・低品質 |
| UD-IQ2_M | 10.2 GB | |
| UD-Q2_K_XL | 11.2 GB | |
| UD-IQ3_XXS | 11.5 GB | |
| Q3_K_S | 12.3 GB | |
| Q3_K_M | 13.5 GB | |
| UD-Q3_K_XL | 14.4 GB | |
| IQ4_XS | 15 GB | |
| Q4_K_S | 15.8 GB | |
| **Q4_K_M** | **16.7 GB** | **推奨** |
| UD-Q4_K_XL | 17.6 GB | |
| Q5_K_S | 18.9 GB | |
| Q5_K_M | 19.6 GB | |
| Q6_K | 22.5 GB | |
| Q8_0 | 28.6 GB | 高品質 |
| BF16 | 53.8 GB | フル精度 |

---

## Qwen3.5-9B

| 項目 | 内容 |
|---|---|
| モデル名 | Qwen3.5-9B |
| パラメータ数 | 9B |
| 推奨量子化 | Q4_K_M（5.68GB） |
| HuggingFace | https://huggingface.co/unsloth/Qwen3.5-9B-GGUF |
| env設定ファイル | `.env.example.qwen3.5-9b` |
| クライアント例 | `LDIE_TEST_Req/test_request_qwen3.5-9b.py` |
| 必要VRAM目安 | 約8GB以上（Q4_K_M, 全レイヤーGPU時） |

### 利用可能な量子化バリエーション

| 量子化 | サイズ | 備考 |
|---|---|---|
| UD-IQ2_XXS | 3.19 GB | 最小・低品質 |
| UD-IQ2_M | 3.65 GB | |
| UD-Q2_K_XL | 4.12 GB | |
| UD-IQ3_XXS | 4.02 GB | |
| Q3_K_S | 4.32 GB | |
| Q3_K_M | 4.67 GB | |
| UD-Q3_K_XL | 5.05 GB | |
| IQ4_XS | 5.17 GB | |
| Q4_K_S | 5.39 GB | |
| **Q4_K_M** | **5.68 GB** | **推奨** |
| UD-Q4_K_XL | 5.97 GB | |
| Q5_K_S | 6.36 GB | |
| Q5_K_M | 6.58 GB | |
| Q6_K | 7.46 GB | |
| Q8_0 | 9.53 GB | 高品質 |
| BF16 | 17.9 GB | フル精度 |

---

## Gemma 3n E2B（既存）

| 項目 | 内容 |
|---|---|
| モデル名 | Gemma 3n E2B |
| 推奨量子化 | Q4_K_XL |
| HuggingFace | https://huggingface.co/unsloth/gemma-3n-E2B-it-GGUF |
| env設定ファイル | `.env.example.gemma3n-e2b` |
| クライアント例 | `LDIE_TEST_Req/test_request_gemma3n-e2b.py` |

---

## Gemma 4 26B A4B IT

| 項目 | 内容 |
|---|---|
| モデル名 | Gemma 4 26B A4B IT（Instruction、MoE：総26B / 活性約4B） |
| 推奨量子化 | UD-Q4_K_M（約15.7GB） |
| HuggingFace | https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF |
| env設定ファイル | `.env.example.gemma4-26b` |
| クライアント例 | `LDIE_TEST_Req/test_request_gemma4-26b.py` |
| 必要VRAM目安 | 約17GB以上（UD-Q4_K_M、全レイヤーGPU時・目安） |

> 画像入力などマルチモーダル利用時は、同リポジトリの `mmproj-*.gguf` が別途必要です。本テンプレートは**テキストチャット用のメインGGUF**のみを対象にしています。

### 利用可能な量子化バリエーション（抜粋）

| 量子化 | サイズ | 備考 |
|---|---|---|
| UD-IQ2_M | 9.3 GB | 最小寄り・低品質 |
| UD-Q2_K_XL | 9.8 GB | |
| UD-Q3_K_M | 11.7 GB | |
| UD-Q3_K_XL | 12.0 GB | |
| UD-IQ4_XS | 12.5 GB | |
| UD-Q4_K_S | 15.3 GB | |
| **UD-Q4_K_M** | **15.7 GB** | **推奨** |
| UD-Q4_K_XL | 16.0 GB | |
| UD-Q5_K_S | 17.5 GB | |
| UD-Q5_K_M | 19.7 GB | |
| UD-Q6_K | 21.3 GB | |
| MXFP4_MOE | 15.5 GB | MoE向け形式（環境により選択可） |
| Q8_0 | 25.0 GB | 高品質 |

---

## Gemma 4 31B IT（Dense）

| 項目 | 内容 |
|---|---|
| モデル名 | Gemma 4 31B IT（Instruction、Dense 約31B） |
| 公式（Safetensors） | https://huggingface.co/google/gemma-4-31B-it |
| 推奨量子化（GGUF） | Q4_K_M（約17.1GB） |
| GGUF（llama.cpp） | https://huggingface.co/unsloth/gemma-4-31B-it-GGUF |
| env設定ファイル | `.env.example.gemma4-31b` |
| クライアント例 | `LDIE_TEST_Req/test_request_gemma4-31b.py` |
| 必要VRAM目安 | 約20GB以上（Q4_K_M、全レイヤーGPU・ctx 16384 時は目安） |

> 画像入力などマルチモーダル利用時は、同リポジトリの `mmproj-*.gguf` が別途必要です。本テンプレートは**テキストチャット用のメインGGUF**のみを対象にしています。

### 利用可能な量子化バリエーション（抜粋・Unsloth GGUF）

| 量子化 | サイズ | 備考 |
|---|---|---|
| UD-IQ2_M | 10.0 GB | 最小寄り・低品質 |
| UD-IQ3_XXS | 11.0 GB | |
| UD-Q2_K_XL | 11.0 GB | |
| Q3_K_S | 12.3 GB | |
| Q3_K_M | 13.7 GB | |
| UD-Q3_K_XL | 14.3 GB | |
| IQ4_XS | 15.2 GB | |
| IQ4_NL | 16.1 GB | |
| Q4_K_S | 16.2 GB | |
| **Q4_K_M** | **17.1 GB** | **推奨** |
| Q4_0 | 16.1 GB | |
| Q4_1 | 17.8 GB | |
| UD-Q4_K_XL | 17.5 GB | |
| Q5_K_S | 19.7 GB | |
| Q5_K_M | 20.2 GB | |
| UD-Q5_K_XL | 20.4 GB | |
| Q6_K | 23.5 GB | |
| UD-Q6_K_XL | 25.6 GB | |
| Q8_0 | 30.4 GB | 高品質 |
| UD-Q8_K_XL | 32.6 GB | |

---

## RTX 5090 おすすめモデル一覧

RTX 5090（VRAM 32GB / 帯域 1,792GB/s）で快適に動作するモデルの比較です。
Q4_K_M量子化基準。性能値は参考値であり、コンテキスト長や設定により変動します。

| モデル | パラメータ | Q4_K_Mサイズ | 生成速度(tok/s) | 特徴 | HuggingFace |
|---|---|---|---|---|---|
| **Qwen3.5-27B** | 27B | 16.7GB | **56（実測）** | 汎用・高性能。本リポジトリ対応済み。reasoning含む | [unsloth/Qwen3.5-27B-GGUF](https://huggingface.co/unsloth/Qwen3.5-27B-GGUF) |
| **Qwen3.5-9B** | 9B | 5.68GB | ~213 | 軽量・高速。本リポジトリ対応済み | [unsloth/Qwen3.5-9B-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) |
| **Gemma 3 27B** | 27B | ~17GB | **67（実測）** | Google製。128Kコンテキスト、140言語対応 | [unsloth/gemma-3-27b-it-GGUF](https://huggingface.co/unsloth/gemma-3-27b-it-GGUF) |
| **Gemma 4 26B A4B** | 26B MoE | ~15.7GB | ~65（推定） | Google製。MoEで高速寄り、256Kコンテキスト、ツール呼び出し | [unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) |
| **Gemma 4 31B IT** | 31B Dense | ~17.1GB | ~55（推定） | [公式](https://huggingface.co/google/gemma-4-31B-it)。Dense・256Kコンテキスト。GGUFは Unsloth | [unsloth/gemma-4-31B-it-GGUF](https://huggingface.co/unsloth/gemma-4-31B-it-GGUF) |
| **Qwen3-32B** | 32B | ~18-20GB | ~61 | RTX 5090で最も人気。汎用・高品質 | [unsloth/Qwen3-32B-GGUF](https://huggingface.co/unsloth/Qwen3-32B-GGUF) |
| **DeepSeek R1 32B** | 32B | ~18-20GB | ~64 | 推論・デバッグに強い。ステップバイステップ思考 | [unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF](https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF) |
| **Qwen3-Coder-30B** | 30B MoE | ~18.6GB | **110（実測）** | コーディング特化。MoE(3B活性化)で高速 | [unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF) |
| **RakutenAI 2.0 8x7B** | 47B MoE | ~26GB | ~40（推定） | 日本語特化。MoEアーキテクチャ | [mmnga/RakutenAI-2.0-8x7B-instruct-gguf](https://huggingface.co/mmnga/RakutenAI-2.0-8x7B-instruct-gguf) |
| **RakutenAI 7B** | 7B | ~4GB | ~200（推定） | 日本語特化。非常に軽量 | [mmnga/RakutenAI-7B-instruct-gguf](https://huggingface.co/mmnga/RakutenAI-7B-instruct-gguf) |

> 生成速度の出典: [RTX 5090 LLM Benchmarks (RunPod)](https://www.runpod.io/blog/rtx-5090-llm-benchmarks)、[hardware-corner.net](https://www.hardware-corner.net/rtx-5090-llm-benchmarks/)、[databasemart.com](https://www.databasemart.com/blog/ollama-gpu-benchmark-rtx5090)
> **「実測」** はLDIE実機（RTX 5090 + docker-compose.yml GPU版 + Q4_K_M）での `measure_inference_speed.sh` 計測値です。
> 「推定」はベンチマーク未確認のため、同規模モデルからの推定値です。

### 用途別おすすめ

| 用途 | おすすめモデル |
|---|---|
| 日本語汎用 | Qwen3.5-27B / Gemma 3 27B / Gemma 4 26B A4B / Gemma 4 31B IT |
| 日本語特化 | RakutenAI 2.0 8x7B / RakutenAI 7B |
| 高速レスポンス | Qwen3.5-9B / RakutenAI 7B |
| コーディング | Qwen3-Coder-30B |
| 推論・分析 | DeepSeek R1 32B |
| 最高品質 | Qwen3-32B |

> 動画生成モデルについては [動画生成モデル一覧](../video-generation/02_available_models.md) を参照してください。

---

## 量子化の選び方

| 優先事項 | 推奨量子化 |
|---|---|
| 品質重視（VRAM十分） | Q8_0 または Q6_K |
| バランス重視（推奨） | **Q4_K_M** |
| VRAM節約 | Q3_K_M または IQ4_XS |
| 最小サイズ | UD-IQ2_XXS |

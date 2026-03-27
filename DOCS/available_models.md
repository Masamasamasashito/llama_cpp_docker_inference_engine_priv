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
| クライアント例 | `example/client_sample_qwen3.5-27b.py` |
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
| クライアント例 | `example/client_sample_qwen3.5-9b.py` |
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
| クライアント例 | `example/client_sample.py` |

---

## 量子化の選び方

| 優先事項 | 推奨量子化 |
|---|---|
| 品質重視（VRAM十分） | Q8_0 または Q6_K |
| バランス重視（推奨） | **Q4_K_M** |
| VRAM節約 | Q3_K_M または IQ4_XS |
| 最小サイズ | UD-IQ2_XXS |

# LDIE モデルセキュリティ評価

LDIEで採用しているモデルのセキュリティリスク評価と、
ローカルLLMを採用する際の判断基準をまとめたドキュメントです。

最終更新: 2026-03-27

---

## 1. GGUFサプライチェーン攻撃（全モデル共通リスク）

2026年1月にPillar Securityが発見した**「Poisoned GGUF Templates」攻撃**が最大の共通リスクです。

| 項目 | 内容 |
|---|---|
| 攻撃手法 | GGUF内のチャットテンプレートに悪意ある指示を埋め込み、全ユーザーの会話を汚染 |
| 影響範囲 | HuggingFace上に15万以上のGGUFモデル。署名・検証の仕組みがない |
| 検知難易度 | テンプレートはバイナリ埋め込みのため、ダウンロード時に目視確認が困難 |
| 誤った安心感 | 「ダウンロード数が多い＝安全」ではない。コミュニティの信頼に依存した脆弱なエコシステム |

### 対策

- **信頼できるアップロード元のみ使用**: `unsloth`, `Qwen`公式, `google`公式 等の確立されたorg
- 非公式の個人アカウントからのGGUFは避ける
- ダウンロード後、`llama.cpp`の`--verbose`ログでチャットテンプレート内容を確認
- 可能であればハッシュ値を公式と照合

### 参考

- [Poisoned GGUF Templates (Pillar Security)](https://www.pillar.security/blog/llm-backdoors-at-the-inference-level-the-threat-of-poisoned-templates)
- [GGUF Security at Scale (Splunk)](https://www.splunk.com/en_us/blog/security/gguf-llm-security-inference-time-poisoning-templates.html)
- [OWASP LLM03:2025 — Supply Chain Vulnerabilities](https://harshkahate.medium.com/owasp-llm03-2025-supply-chain-vulnerabilities-the-threat-that-arrives-before-you-write-a-single-7c1079bf12e4)

---

## 2. モデル別リスク評価

### リスク一覧

| モデル | 開発元 | 開発国 | リスクレベル | 主なリスク |
|---|---|---|---|---|
| **Gemma 3 27B** | Google | 米国 | 低 | セキュリティ監査済み。最も安全な選択肢 |
| **Gemma 3n E2B** | Google | 米国 | 低 | 同上 |
| **Qwen3.5-27B** | Alibaba | 中国 | 中 | 中国政府政策に沿った検閲が訓練に組み込まれている |
| **Qwen3.5-9B** | Alibaba | 中国 | 中 | 同上 |
| **Qwen3-32B** | Alibaba | 中国 | 中 | 同上 |
| **Qwen3-Coder-30B** | Alibaba | 中国 | 中 | 同上。コード生成時の安全性は未検証 |
| **DeepSeek R1 32B** | DeepSeek | 中国 | **高** | NISTが「米国国家安全保障リスク」と評価 |

### 詳細評価

#### Gemma 3 27B / Gemma 3n E2B（リスク: 低）

- Google DeepMindが開発。企業内セキュリティ監査を経てリリース
- 128Kコンテキスト、140言語対応
- Apache 2.0ライセンス
- **LDIEで最も安全な選択肢**

#### Qwen3.5 / Qwen3 / Qwen3-Coder（リスク: 中）

- Alibaba Cloud（中国）が開発
- 中国政府政策に沿ったコンテンツ検閲が訓練段階で組み込まれている
  - 中国に関する回答は「肯定的で建設的」になるよう調整されている
  - 他国に関しては「中立的で客観的」とされるが、政治的トピックは回避
- ジェイルブレイク耐性に脆弱性あり（武器・薬物等の禁止コンテンツを生成可能なケースが報告）
- HuggingFace上で9.5百万回以上ダウンロード（2025年10-11月）、2,800以上の派生モデル
- **ローカル実行であれば外部へのデータ送信リスクはない**（クラウドAPI利用時はデータが中国に保存される）

参考: [Qwen Censorship Analysis (HuggingFace)](https://huggingface.co/blog/leonardlin/chinese-llm-censorship-analysis)

#### DeepSeek R1 32B（リスク: **高**）

**NIST（米国国立標準技術研究所）が正式に評価し、リスクを警告しています。**

| 指標 | DeepSeek R1 | 米国モデル比較 |
|---|---|---|
| 悪意ある指示への従順率 | 最も安全なR1-0528でも**12倍**高い | 基準 |
| ジェイルブレイク成功率 | **94%** | 8% |
| 有害コンテンツ生成確率 | **11倍** | 基準（OpenAI o1比） |
| サイバーセキュリティテスト突破率 | **78%** が悪意あるコード生成に成功 | — |

**政治トリガーによるコード品質劣化:**
- 「Falun Gong」「Uyghurs」「Tibet」等の政治的キーワードを含むプロンプトでコード生成すると、**セキュリティバグが50%増加**する
- 天安門事件・台湾の主権等の質問を拒否する挙動がベースモデルに埋め込まれている

**OpenClawバックエンドとして使用する場合の特別なリスク:**
- OpenClawはLLMの出力に基づいてコマンドを**自動実行**する
- DeepSeek R1が生成したセキュリティバグを含むコードが、検証なしに実行される可能性がある
- エージェントの自走において、リスクが増幅される

参考:
- [NIST DeepSeek Evaluation](https://www.nist.gov/news-events/news/2025/09/caisi-evaluation-deepseek-ai-models-finds-shortcomings-and-risks)
- [DeepSeek Political Trigger Bugs (VentureBeat)](https://venturebeat.com/security/deepseek-injects-50-more-security-bugs-when-prompted-with-chinese-political)
- [DeepSeek Security Gaps (Euronews)](https://www.euronews.com/next/2025/01/31/harmful-and-toxic-output-deepseek-has-major-security-and-safety-gaps-study-warns)

---

## 3. 動画生成モデルのリスク

| モデル | 開発元 | 開発国 | ライセンス | リスク |
|---|---|---|---|---|
| **LTX-Video** | Lightricks | イスラエル | Apache 2.0 | 低。NVIDIA公式が最適化を推進 |
| **Wan 2.1 / 2.2** | Alibaba | 中国 | Apache 2.0 | 低。動画生成モデルは検閲リスクが低い（テキスト出力がない） |
| **HunyuanVideo 1.5** | Tencent | 中国 | Tencent独自ライセンス | 中。独自ライセンスの利用条件を確認する必要あり |

動画生成モデルはテキスト出力がないため、LLMのような検閲・有害コンテンツ生成リスクは低い。
ただし、GGUFサプライチェーン攻撃と同様に、モデルファイル自体の改ざんリスクは存在する。

---

## 4. ローカルLLM採用時のセキュリティ判断基準

| # | 基準 | チェックポイント | 重要度 |
|---|---|---|---|
| 1 | **ソース信頼性** | 公式 or 信頼できるアップロード元（unsloth, 公式org）からのみダウンロード | 必須 |
| 2 | **開発国・法規制** | 中国製モデルは検閲・バイアスが訓練に含まれる前提で使う | 必須 |
| 3 | **ライセンス確認** | Apache 2.0 / MIT は安全。独自ライセンスは利用条件を確認 | 必須 |
| 4 | **GGUFテンプレート検証** | ダウンロード後、`--verbose`ログでテンプレート内容を確認 | 推奨 |
| 5 | **ハッシュ照合** | 公式が提供するSHA256等と照合 | 推奨 |
| 6 | **生成コードの検証** | 特にDeepSeek R1で生成されたコードは必ず人間がレビュー | 必須（R1使用時） |
| 7 | **ネットワーク隔離** | Dockerネットワークでモデルコンテナの外部通信を制限 | 推奨 |
| 8 | **出力フィルタリング** | OpenClaw等のエージェントに使う場合、実行前の出力検証を設ける | 推奨（エージェント使用時） |
| 9 | **NIST/OWASP評価の確認** | 新モデル採用時にNISTやOWASPの評価を確認 | 推奨 |
| 10 | **定期更新** | セキュリティ情報は変化する。定期的にモデルの評価情報を確認 | 推奨 |

---

## 5. LDIE推奨モデル（セキュリティ観点）

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| 安全性最優先 | **Gemma 3 27B** | Google製。最もセキュリティリスクが低い |
| 日本語汎用（バランス） | **Qwen3.5-27B** | 検閲リスクはあるが、ローカル実行ならデータ送信なし。性能は最高クラス |
| コーディング | **Qwen3-Coder-30B**（注意付き） | 生成コードは必ずレビュー。重要なプロジェクトではGemma推奨 |
| 推論・分析 | **Gemma 3 27B** を推奨 | DeepSeek R1は能力は高いが、NISTが警告するリスクを理解した上で判断 |
| OpenClawバックエンド | **Gemma 3 27B** または **Qwen3.5-27B** | エージェント自走ではリスクが増幅されるため、DeepSeek R1は非推奨 |

---

[LDIE命名規則](LDIE_NamingConvention.md) | [ドキュメント一覧](README.md)

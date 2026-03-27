# LDIE ドキュメント

**LDIE** = **L**lama.cpp **D**ocker **I**nference **E**ngine

---

## 利用ガイド

### [テキスト生成 LLM（llama.cpp）](text-llm/README.md)

llama.cpp + Docker によるテキスト生成AIの構築・運用ガイドです。

- [セットアップ手順](text-llm/setup_guide.md)
- [利用可能モデル一覧](text-llm/available_models.md)

### [動画生成（ComfyUI）](video-generation/README.md)

ComfyUI による動画生成AIの構築・運用ガイドです。

- [セットアップ手順](video-generation/setup_guide.md)
- [利用可能モデル一覧](video-generation/available_models.md)

### [OpenClaw連携](openclaw-integration/README.md)

ホームLAN内の他PC（Ubuntu 24.04）のOpenClawにローカルLLMをAPI提供し、AIエージェントを自走させるガイドです。

- [セットアップ手順](openclaw-integration/setup_guide.md)
- [ネットワーク設定](openclaw-integration/network_config.md)

---

## リファレンス

### [LDIE 命名規則](LDIE_NamingConvention.md)

環境変数・ファイル・ボリューム等の命名規則リファレンスです。
`COMMON_LDIE_`, `DOCKER_HOST_`, `LLAMA_CONTAINER_` 等のプレフィックス体系、.env.exampleのセクション構造を定義しています。

### [LDIE モデルセキュリティ評価](LDIE_ModelSecurityAssessment.md)

採用モデルのセキュリティリスク評価です。

- GGUFサプライチェーン攻撃（Poisoned Templates）の解説と対策
- モデル別リスク評価（Gemma: 低 / Qwen: 中 / DeepSeek R1: 高）
- LDIE構成における脅威の発生箇所（Windows側は安全、Ubuntu/OpenClaw側に脅威集中）
- ローカルLLM採用時のセキュリティ判断基準（10項目）
- 用途別推奨モデル（セキュリティ観点）

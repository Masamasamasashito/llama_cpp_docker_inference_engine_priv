# ドキュメント

本リポジトリのドキュメント一覧です。

---

## [テキスト生成 LLM（llama.cpp）](text-llm/README.md)

llama.cpp + Docker によるテキスト生成AIの構築・運用ガイドです。

- [セットアップ手順](text-llm/setup_guide.md)
- [利用可能モデル一覧](text-llm/available_models.md)

---

## [動画生成（ComfyUI）](video-generation/README.md)

ComfyUI による動画生成AIの構築・運用ガイドです。

- [セットアップ手順](video-generation/setup_guide.md)
- [利用可能モデル一覧](video-generation/available_models.md)

---

## [OpenClaw連携](openclaw-integration/README.md)

ホームLAN内の他PCのOpenClawにローカルLLMをAPI提供し、AIエージェントを自走させるガイドです。

- [セットアップ手順](openclaw-integration/setup_guide.md)
- [ネットワーク設定](openclaw-integration/network_config.md)

---

## [LDIE 命名規則](LDIE_NamingConvention.md)

環境変数・ファイル・ボリューム等の命名規則リファレンスです。
LDIE = **L**lama.cpp **D**ocker **I**nference **E**ngine

---

## [LDIE モデルセキュリティ評価](LDIE_ModelSecurityAssessment.md)

採用モデルのセキュリティリスク評価・GGUFサプライチェーン攻撃対策・ローカルLLM採用時の判断基準です。

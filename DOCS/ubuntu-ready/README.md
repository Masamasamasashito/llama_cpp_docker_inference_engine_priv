# Ubuntu 24.04.4 LTS セットアップガイド

Ubuntu PC にOpenClawをインストールし、Windows 11 ProのLDIE（llama.cppサーバー）に
API連携してAIエージェントを自走させるまでの完全手順です。

**このガイドはすべてUbuntu側で実行します。**

---

## 前提条件

| 項目 | 要件 |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| ネットワーク | Windows LDIEサーバーと同一LAN |
| Windows側 | LDIE起動済み、ファイアウォール設定済み、API Key発行済み |

> Windows側の準備がまだの場合は [OpenClaw連携 セットアップ手順](../openclaw-integration/01_setup_guide.md) のStep 1を先に完了してください。

## 2つの運用パターン

Step 3（OpenClaw設定）で、どちらのパターンで運用するかを選択します。

| | Pattern A（全ローカル） | Pattern B（司令塔クラウド + 作業役ローカル） |
|---|---|---|
| 司令塔 | LDIE（Gemma 3 27B等） | **クラウド（Claude Opus / GPT-4o）** |
| 作業役 | LDIE | LDIE |
| 月額 | 電気代 $25-50 | $45-130 |
| 精度 | 中〜高 | **最高** |
| オフライン | 可能 | 不可 |
| プライバシー | **最高** | 中（司令塔経由で一部クラウドに送信） |
| 移行 | — | Pattern A → B は `openclaw.json` の変更のみ |

> 詳細な比較は [LDIEアーキテクチャ](../LDIE_Architecture.md) を参照。
> まずPattern Aで始めて、精度が不足したらPattern Bに移行するのが推奨です。

## ドキュメント

- [1. 環境構築](01_environment_setup.md) — Node.js・OpenClawインストール
- [2. ネットワーク確認](02_network_verification.md) — LDIEサーバーへの疎通確認
- [3. OpenClaw設定](03_openclaw_config.md) — openclaw.jsonの設定・モデル登録
- [4. 動作確認・自走テスト](04_run_and_test.md) — OpenClawの起動と自走確認
- [5. セキュリティ対策](05_security.md) — Ubuntu側の推奨セキュリティ設定

---

[OpenClaw連携](../openclaw-integration/README.md) | [ドキュメント一覧](../README.md)

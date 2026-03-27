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

> Windows側の準備がまだの場合は [OpenClaw連携 セットアップ手順](../openclaw-integration/setup_guide.md) のStep 1を先に完了してください。

## ドキュメント

- [1. 環境構築](01_environment_setup.md) — Node.js・OpenClawインストール
- [2. ネットワーク確認](02_network_verification.md) — LDIEサーバーへの疎通確認
- [3. OpenClaw設定](03_openclaw_config.md) — openclaw.jsonの設定・モデル登録
- [4. 動作確認・自走テスト](04_run_and_test.md) — OpenClawの起動と自走確認
- [5. セキュリティ対策](05_security.md) — Ubuntu側の推奨セキュリティ設定

---

[OpenClaw連携](../openclaw-integration/README.md) | [ドキュメント一覧](../README.md)

# OpenClaw連携ガイド

ホームローカルネットワーク内で、本リポジトリのllama.cppサーバーをAPIとして
他PCのOpenClawに提供し、OpenClawがローカルLLMで自走するまでの設定ガイドです。

---

## 構成イメージ

```
┌─────────────────────┐          ┌─────────────────────┐
│  LLMサーバーPC       │          │  クライアントPC      │
│  (RTX 5090)         │          │  (OpenClaw)          │
│                     │   LAN    │                     │
│  llama.cpp          │◄────────►│  openclaw.json      │
│  :8081/v1           │          │  baseUrl指定         │
│  models/Qwen3.5-*   │          │                     │
└─────────────────────┘          └─────────────────────┘
```

## ドキュメント

- [セットアップ手順](setup_guide.md) - サーバー側・クライアント側の設定から動作確認まで
- [ネットワーク設定](network_config.md) - ファイアウォール・ポート開放・セキュリティ

## 前提条件

| 項目 | LLMサーバーPC | クライアントPC |
|---|---|---|
| OS | Windows / Linux | Windows / macOS / Linux |
| GPU | RTX 5090推奨 | 不要 |
| ソフトウェア | Docker, NVIDIA Container Toolkit | Node.js 22以上, OpenClaw |
| ネットワーク | 同一LAN内、固定IPまたはmDNS | 同一LAN内 |

---

[テキスト生成LLM](../text-llm/README.md) | [ドキュメント一覧](../README.md)

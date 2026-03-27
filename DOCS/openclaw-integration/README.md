# OpenClaw連携ガイド

ホームLAN内で、Windows 11 Pro（LDIEサーバー）からUbuntu 24.04（OpenClaw）に
ローカルLLMをAPI提供し、AIエージェントを自走させるための設定ガイドです。

---

## 構成イメージ

```
┌─────────────────────┐          ┌─────────────────────┐
│  Windows 11 Pro     │          │  Ubuntu 24.04       │
│  LDIEサーバー        │          │  OpenClaw           │
│  (RTX 5090)         │   LAN    │                     │
│                     │◄────────►│  openclaw.json      │
│  llama.cpp :8081/v1 │          │  baseUrl指定         │
│  API Key認証         │          │                     │
└─────────────────────┘          └─────────────────────┘
  本ガイド（Windows側）              Ubuntu Readyガイド
```

## ドキュメント（Windows側）

- [セットアップ手順](01_setup_guide.md) — LDIE起動・バインドアドレス・ファイアウォール・API Key
- [ネットワーク設定](02_network_config.md) — IP設計・ファイアウォール詳細・セキュリティ強化・管理コマンド

## Ubuntu側の手順

Ubuntu側（OpenClawインストール・設定・自走テスト）は別ガイドにまとめています:

**→ [Ubuntu Ready ガイド](../ubuntu-ready/README.md)**

## 前提条件

| 項目 | Windows 11 Pro（LDIEサーバー） | Ubuntu 24.04（OpenClaw） |
|---|---|---|
| GPU | RTX 5090推奨 | 不要 |
| ソフトウェア | Docker Desktop, NVIDIA Container Toolkit | Node.js 22以上, OpenClaw |
| ネットワーク | 同一LAN、固定プライベートIP推奨 | 同一LAN、固定プライベートIP推奨 |
| ファイアウォール | Ubuntu PCのIPのみ8081を許可 | 特になし |
| 担当ガイド | **本ガイド** | **[Ubuntu Ready](../ubuntu-ready/README.md)** |

---

[テキスト生成LLM](../text-llm/README.md) | [Ubuntu Ready](../ubuntu-ready/README.md) | [ドキュメント一覧](../README.md)

# OpenClaw連携 セットアップ手順

Windows 11 Pro（LDIEサーバー）側の準備手順です。
LAN内のUbuntu PCからOpenClawでAPI接続できる状態にします。

> **Ubuntu側（OpenClawインストール・設定・自走テスト）の手順は [Ubuntu Ready](../ubuntu-ready/README.md) を参照してください。**

---

## 全体の流れ

| Step | 実行場所 | 内容 | ガイド |
|---|---|---|---|
| 1 | **Windows** | LDIEサーバー起動・LAN公開 | 本ドキュメント |
| 2 | **Windows** | ファイアウォール設定 | 本ドキュメント |
| 3 | **Windows** | API Key認証の有効化 | 本ドキュメント |
| 4 | **Ubuntu** | OpenClawインストール | [Ubuntu Ready Step 1](../ubuntu-ready/01_environment_setup.md) |
| 5 | **Ubuntu** | ネットワーク疎通確認 | [Ubuntu Ready Step 2](../ubuntu-ready/02_network_verification.md) |
| 6 | **Ubuntu** | OpenClaw設定（openclaw.json） | [Ubuntu Ready Step 3](../ubuntu-ready/03_openclaw_config.md) |
| 7 | **Ubuntu** | 動作確認・自走テスト | [Ubuntu Ready Step 4](../ubuntu-ready/04_run_and_test.md) |

---

## Step 1: LDIEサーバーの起動とLAN公開

### 1-1. モデルのダウンロードと起動

テキスト生成LLMの [セットアップ手順](../text-llm/01_setup_guide.md) に従い、
モデルをダウンロードしてdocker-composeで起動します。

```bash
# Docker作業ディレクトリに移動
cd LDIE_Infra_Docker

# .envを設定（例: Gemma 3 27B — 安全性最高・推奨）
cp .env.example.gemma3-27b .env

# モデルダウンロード
curl -L -o models/gemma-3-27b-it-Q4_K_M.gguf \
  https://huggingface.co/unsloth/gemma-3-27b-it-GGUF/resolve/main/gemma-3-27b-it-Q4_K_M.gguf

# GPU版で起動
docker-compose up -d

# RTX 5090の場合
docker-compose -f docker-compose.high.yml up -d
```

### 1-2. バインドアドレスをプライベートIPに変更

デフォルトでは `127.0.0.1`（ローカルのみ）にバインドされます。
LAN内の他PCからアクセスするには、`.env` で `DOCKER_HOST_BIND_ADDR` をサーバーPCのプライベートIPに設定します。

```powershell
# サーバーPCのプライベートIPを確認
ipconfig
# 「IPv4 アドレス」の値を控える（例: 192.168.1.100）
```

`.env` を編集:

```bash
DOCKER_HOST_BIND_ADDR=192.168.1.100
```

```powershell
# docker-composeを再起動
docker-compose down
docker-compose up -d

# サーバーPC自身で確認
curl http://192.168.1.100:8081/health
```

> 詳細は [ネットワーク設定](02_network_config.md) を参照してください。

---

## Step 2: ファイアウォール設定（Windows 11 Pro）

Ubuntu PCのプライベートIPのみを許可する厳格なルールを設定します。
PowerShellを**管理者権限**で実行してください。

```powershell
# UbuntuクライアントPCのプライベートIPアドレス（環境に合わせて変更）
$UbuntuPrivateIP = "192.168.1.200"

# 指定IPからの8081のみ許可（プライベートネットワーク限定）
New-NetFirewallRule `
  -DisplayName "llama.cpp API - OpenClaw Only" `
  -Description "Ubuntu OpenClaw PC ($UbuntuPrivateIP) からのllama.cpp API接続のみ許可" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 8081 `
  -RemoteAddress $UbuntuPrivateIP `
  -Profile Private `
  -Enabled True

# 他のすべてのIPからの8081を明示的にブロック
New-NetFirewallRule `
  -DisplayName "llama.cpp API - Block Others" `
  -Direction Inbound `
  -Action Block `
  -Protocol TCP `
  -LocalPort 8081 `
  -Profile Any `
  -Enabled True
```

> 詳細なセキュリティ設定・ログ監視・管理方法は [ネットワーク設定](02_network_config.md) を参照してください。

---

## Step 3: API Key認証の有効化

`.env` にAPI Keyを追加してdocker-composeを再起動します。

```bash
# macOS / Linux でキー生成
echo "LLAMA_API_KEY=sk-local-$(openssl rand -hex 32)" >> .env
```

```powershell
# Windows PowerShell でキー生成
$bytes = New-Object byte[] 32; (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); $hex = -join ($bytes | ForEach-Object { $_.ToString("x2") }); "LLAMA_API_KEY=sk-local-$hex" | Add-Content .env
```

```powershell
# 再起動
docker-compose down
docker-compose up -d
```

確認:

```powershell
# API Keyなし → 401
curl http://192.168.1.100:8081/v1/models
# API Keyあり → 200
curl -H "Authorization: Bearer YOUR_API_KEY" http://192.168.1.100:8081/v1/models
```

> 生成されたAPI Keyの値をUbuntu側の担当者に安全に共有してください。
> Ubuntu側の設定は [Ubuntu Ready Step 3](../ubuntu-ready/03_openclaw_config.md) で行います。

---

## Windows側の準備が完了したら

Ubuntu側の手順に進んでください:

1. [環境構築](../ubuntu-ready/01_environment_setup.md) — Node.js・OpenClawインストール
2. [ネットワーク確認](../ubuntu-ready/02_network_verification.md) — LDIEサーバーへの疎通確認
3. [OpenClaw設定](../ubuntu-ready/03_openclaw_config.md) — openclaw.jsonの設定
4. [動作確認・自走テスト](../ubuntu-ready/04_run_and_test.md) — OpenClawの起動と自走確認
5. [セキュリティ対策](../ubuntu-ready/05_security.md) — Ubuntu側の推奨設定

---

[ネットワーク設定](02_network_config.md) | [OpenClaw連携トップ](README.md) | [ドキュメント一覧](../README.md)

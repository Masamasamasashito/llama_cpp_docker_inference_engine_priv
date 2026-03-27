# ネットワーク設定

ホームLAN内でllama.cppサーバー（Windows 11 Pro）を
OpenClawクライアント（Ubuntu 24.04.4 LTS）に公開するためのネットワーク設定です。

**設計方針: Windows 11 Pro側のセキュリティを最大限に確保する**

---

## 想定構成

```
┌──────────────────────────┐          ┌──────────────────────────┐
│  LLMサーバーPC            │          │  OpenClawクライアントPC   │
│  Windows 11 Pro          │   LAN    │  Ubuntu 24.04.4 LTS      │
│  IP: 192.168.1.100       │◄────────►│  IP: 192.168.1.200       │
│  Port: 8081              │          │                          │
│                          │          │  openclaw.json            │
│  ファイアウォール:        │          │  baseUrl → :8081/v1      │
│  8081を192.168.1.200のみ  │          │                          │
│  許可                    │          │                          │
└──────────────────────────┘          └──────────────────────────┘
```

> IPアドレスは例です。実際の環境に合わせて読み替えてください。

---

## ポート構成

| docker-compose | ホスト側ポート | 用途 |
|---|---|---|
| `docker-compose.yml`（GPU） | 8081 | デフォルトGPU版 |
| `docker-compose.cpu.yml` | 8080（LLAMA_PORT） | CPU版 |
| `docker-compose.high.yml` | 8081 | RTX 5090版 |

---

## Step 1: UbuntuクライアントPCの固定IP設定

ファイアウォールでIPを指定許可するため、Ubuntu側を先に固定IPにします。

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:  # インターフェース名は `ip link show` で確認
      addresses:
        - 192.168.1.200/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply

# 確認
ip addr show eth0
```

---

## Step 2: Windows 11 Pro ファイアウォール設定（セキュリティ最大化）

**すべてPowerShellを管理者権限で実行してください。**

### 2-1. 既存の広範なルールがないか確認

```powershell
# llama.cpp関連の既存ルールを確認
Get-NetFirewallRule -DisplayName "*llama*" 2>$null | Format-Table DisplayName, Enabled, Direction, Action

# もし全IP許可のルールが残っていたら削除
# Remove-NetFirewallRule -DisplayName "llama.cpp API"
```

### 2-2. Ubuntu PCのIPのみを許可するルールを作成

```powershell
# UbuntuクライアントPCのIPアドレス（環境に合わせて変更）
$UbuntuIP = "192.168.1.200"

# 受信ルール: 指定IPからの8081のみ許可
New-NetFirewallRule `
  -DisplayName "llama.cpp API - OpenClaw Only" `
  -Description "Ubuntu OpenClaw PC ($UbuntuIP) からのllama.cpp API接続のみ許可" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 8081 `
  -RemoteAddress $UbuntuIP `
  -Profile Private `
  -Enabled True

# 他のすべてのIPからの8081をブロック（明示的拒否）
New-NetFirewallRule `
  -DisplayName "llama.cpp API - Block Others" `
  -Description "8081への他IPからのアクセスを明示的にブロック" `
  -Direction Inbound `
  -Action Block `
  -Protocol TCP `
  -LocalPort 8081 `
  -Profile Any `
  -Enabled True
```

**ポイント:**
- `-RemoteAddress` で Ubuntu PC の IP だけを許可
- `-Profile Private` でプライベートネットワークのみ有効（パブリック/ドメインでは無効）
- 明示的なブロックルールで他IPを拒否（Windowsファイアウォールは許可ルール優先のため、Allow+Block 併用で確実に制御）

### 2-3. ルールの確認

```powershell
# 作成したルールを確認
Get-NetFirewallRule -DisplayName "llama.cpp API*" |
  Format-Table DisplayName, Enabled, Direction, Action, Profile

# 詳細確認（RemoteAddressを含む）
Get-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" |
  Get-NetFirewallAddressFilter |
  Format-Table RemoteAddress
```

### 2-4. 動作テスト後のログ確認（オプション）

```powershell
# ファイアウォールログを有効化（ブロックされた接続を記録）
Set-NetFirewallProfile -Profile Private -LogBlocked True -LogAllowed False -LogFileName "%SystemRoot%\System32\LogFiles\Firewall\pfirewall.log"

# ログ確認
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" -Tail 20
```

---

## Step 3: 追加のセキュリティ強化策

### 3-1. ネットワークプロファイルの確認

ホームLANが「プライベート」として認識されていることを確認します。

```powershell
# 現在のネットワークプロファイルを確認
Get-NetConnectionProfile | Format-Table Name, NetworkCategory, InterfaceAlias

# もし「Public」になっていたら「Private」に変更
# Set-NetConnectionProfile -InterfaceAlias "イーサネット" -NetworkCategory Private
```

> 「パブリック」のままだとファイアウォールルール（Profile Private）が適用されません。

### 3-2. Docker Desktop のファイアウォール自動ルールを確認

Docker Desktop は自動でファイアウォールルールを追加することがあります。
意図しない広範な許可が入っていないか確認してください。

```powershell
# Docker関連のファイアウォールルールを一覧
Get-NetFirewallRule -DisplayName "*Docker*" |
  Format-Table DisplayName, Enabled, Direction, Action
```

不要な受信許可ルールがあれば無効化を検討してください。

### 3-3. Windows 11 Pro のその他の推奨設定

```powershell
# ICMPエコー（ping）もUbuntu PCのみに制限（オプション）
New-NetFirewallRule `
  -DisplayName "ICMP - OpenClaw Only" `
  -Direction Inbound `
  -Action Allow `
  -Protocol ICMPv4 `
  -IcmpType 8 `
  -RemoteAddress "192.168.1.200" `
  -Profile Private `
  -Enabled True
```

### 3-4. セキュリティチェックリスト

| 項目 | 確認コマンド | 期待結果 |
|---|---|---|
| ネットワークプロファイル | `Get-NetConnectionProfile` | `Private` |
| 許可ルール | `Get-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"` | Enabled: True, Action: Allow |
| ブロックルール | `Get-NetFirewallRule -DisplayName "llama.cpp API - Block Others"` | Enabled: True, Action: Block |
| RemoteAddress制限 | `Get-NetFirewallRule ... \| Get-NetFirewallAddressFilter` | Ubuntu PCのIPのみ |
| Docker自動ルール | `Get-NetFirewallRule -DisplayName "*Docker*"` | 不要な受信許可がないこと |
| ログ有効 | `Get-NetFirewallProfile -Profile Private` | LogBlocked: True |

---

## Step 4: Windows 11 Pro の固定IP設定

サーバー側も固定IPを推奨します。

1. **設定** > **ネットワークとインターネット** > **イーサネット** > **IP割り当て** > **編集**
2. 手動に切り替えてIPv4を有効化:

| 項目 | 値（例） |
|---|---|
| IPアドレス | 192.168.1.100 |
| サブネットマスク | 255.255.255.0 |
| ゲートウェイ | 192.168.1.1 |
| 優先DNS | 8.8.8.8 |
| 代替DNS | 8.8.4.4 |

または PowerShell で設定:

```powershell
# インターフェース名を確認
Get-NetAdapter | Format-Table Name, Status, InterfaceDescription

# 固定IP設定（インターフェース名は環境に合わせて変更）
New-NetIPAddress -InterfaceAlias "イーサネット" -IPAddress 192.168.1.100 -PrefixLength 24 -DefaultGateway 192.168.1.1
Set-DnsClientServerAddress -InterfaceAlias "イーサネット" -ServerAddresses 8.8.8.8,8.8.4.4
```

---

## Step 5: 疎通確認

### Ubuntu側（クライアントPC）から実行

```bash
# 1. ネットワーク接続
ping 192.168.1.100

# 2. ポート開放確認
curl http://192.168.1.100:8081/health

# 3. API応答
curl http://192.168.1.100:8081/v1/models

# 4. 推論テスト
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.5-27B-Q4_K_M","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

### 許可されていないPCからの確認（オプション）

別のPCから接続を試み、ブロックされることを確認します。

```bash
# 別のPC（例: 192.168.1.201）から実行 → タイムアウトするはず
curl --connect-timeout 5 http://192.168.1.100:8081/health
# 期待結果: Connection timed out
```

Windows側のファイアウォールログでブロック記録を確認:

```powershell
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" -Tail 10 |
  Select-String "DROP"
```

### トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| Ubuntu PCから接続できない | `RemoteAddress` のIPが正しいか確認。`Get-NetFirewallRule ... \| Get-NetFirewallAddressFilter` |
| 別PCからも接続できてしまう | ブロックルールが有効か確認。ネットワークプロファイルが `Private` か確認 |
| `Connection refused` | Dockerコンテナが起動しているか `docker ps` で確認 |
| `Connection timed out` | ファイアウォールでブロックされている。許可ルールのIPとUbuntuの実IPが一致しているか確認 |

---

## ルールの管理

```powershell
# ルールを一時無効化
Disable-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"

# ルールを再有効化
Enable-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"

# UbuntuのIPが変わった場合（例: 192.168.1.201に変更）
Set-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" -RemoteAddress "192.168.1.201"

# 複数PCを許可する場合（カンマ区切り）
Set-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" -RemoteAddress "192.168.1.200","192.168.1.201"

# ルール完全削除
Remove-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"
Remove-NetFirewallRule -DisplayName "llama.cpp API - Block Others"
```

---

## セキュリティに関する注意

llama.cppサーバーは**認証なし**で動作します。以下を徹底してください。

- ファイアウォールで**特定IPのみ許可**（本ガイドの設定）
- ネットワークプロファイルは**プライベート**を維持
- **インターネットに絶対に公開しない**（ポートフォワーディング禁止）
- 外部アクセスが必要な場合は**VPN経由**を推奨
- 定期的にファイアウォールログを確認し、不審なアクセスがないか監視
- Ubuntu側のIPが変わったら速やかにルールを更新

---

[セットアップ手順](setup_guide.md) | [OpenClaw連携トップ](README.md) | [ドキュメント一覧](../README.md)

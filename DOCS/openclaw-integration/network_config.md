# ネットワーク設定

ホームLAN内でllama.cppサーバー（Windows 11 Pro）を
OpenClawクライアント（Ubuntu 24.04.4 LTS）に公開するためのネットワーク設定です。

**設計方針: Windows 11 Pro側のセキュリティを最大限に確保する**

---

## 想定構成

```
  ホームLAN（プライベートネットワーク 192.168.1.0/24）
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  ┌─────────────────────────┐  ┌─────────────────────────┐│
  │  │ LLMサーバーPC           │  │ OpenClawクライアントPC   ││
  │  │ Windows 11 Pro          │  │ Ubuntu 24.04.4 LTS      ││
  │  │                         │  │                         ││
  │  │ プライベートIP:         │  │ プライベートIP:         ││
  │  │   192.168.1.100         │  │   192.168.1.200         ││
  │  │ Port: 8081              │  │                         ││
  │  │ API Key: 認証あり       │  │ openclaw.json           ││
  │  │                         │  │   baseUrl → :8081/v1    ││
  │  │ ファイアウォール:       │  │   apiKey → Bearer認証   ││
  │  │   8081を                │  │                         ││
  │  │   192.168.1.200のみ許可 │  │                         ││
  │  └─────────────────────────┘  └─────────────────────────┘│
  │                                                          │
  └──────────────────────────────────────────────────────────┘
         ※ インターネットへのポート公開は禁止
```

> **プライベートIPアドレス** (`192.168.1.x`) はホームLAN内でのみ有効なアドレスです。
> インターネットからは到達できません。以下のIPはすべてプライベートIPです。

### プライベートIPアドレスの範囲

| クラス | 範囲 | よく使われるホームLAN |
|---|---|---|
| クラスA | `10.0.0.0` ～ `10.255.255.255` | 一部ルーター |
| クラスB | `172.16.0.0` ～ `172.31.255.255` | Docker内部等 |
| クラスC | `192.168.0.0` ～ `192.168.255.255` | **ほとんどのホームルーター** |

### 自分のネットワーク情報を確認する方法

設定を始める前に、以下のコマンドで自分のLAN環境を把握してください。

**Windows 11 Pro（LLMサーバーPC）:**

```powershell
# プライベートIP・サブネットマスク・デフォルトゲートウェイを一括確認
ipconfig
```

出力例:
```
イーサネット アダプター イーサネット:

   IPv4 アドレス . . . . . . . . . . . : 192.168.1.100   ← 自分のプライベートIP
   サブネット マスク . . . . . . . . . : 255.255.255.0    ← サブネットマスク（/24）
   デフォルト ゲートウェイ . . . . . . : 192.168.1.1      ← ルーターのプライベートIP
```

**Ubuntu 24.04.4 LTS（OpenClawクライアントPC）:**

```bash
# プライベートIPとサブネットを確認
ip addr show

# デフォルトゲートウェイ（ルーターのプライベートIP）を確認
ip route show default
```

出力例:
```
# ip addr show
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.200/24 brd 192.168.1.255    ← 自分のプライベートIP/サブネット

# ip route show default
default via 192.168.1.1 dev eth0               ← ルーターのプライベートIP
```

### 確認すべき3つの値

| 項目 | 確認コマンド（Windows） | 確認コマンド（Ubuntu） | 用途 |
|---|---|---|---|
| 自分のプライベートIP | `ipconfig` → IPv4 アドレス | `ip addr show` → inet | ファイアウォール許可ルール・固定IP設定 |
| サブネットマスク | `ipconfig` → サブネット マスク | `ip addr show` → /24等 | LAN範囲の把握（/24 = 255.255.255.0 = 254台） |
| デフォルトゲートウェイ | `ipconfig` → デフォルト ゲートウェイ | `ip route show default` → via | ルーターのIP。固定IP設定時のgatewayに使用 |

### プライベートIPかどうかの判定

上記で確認したIPアドレスが以下の範囲に入っていればプライベートIPです。

| 範囲 | サブネット | よく使われる場面 |
|---|---|---|
| `10.0.0.0` ～ `10.255.255.255` | 10.0.0.0/8 | 一部ルーター、企業LAN |
| `172.16.0.0` ～ `172.31.255.255` | 172.16.0.0/12 | Docker内部ネットワーク等 |
| `192.168.0.0` ～ `192.168.255.255` | 192.168.0.0/16 | **ほとんどのホームルーター** |

**上記以外のIPが表示された場合はパブリックIP（インターネット直結）の可能性があります。
その場合、本ガイドのLAN公開設定はセキュリティリスクが高いため、ネットワーク構成を見直してください。**

### デフォルトゲートウェイの役割

- デフォルトゲートウェイ = **ルーターのプライベートIPアドレス**
- LAN内の通信はルーター経由なしで直接行われますが、インターネットへの通信はこのゲートウェイを経由します
- 固定IP設定時に `gateway` / `デフォルトゲートウェイ` として必ず指定する値です
- 通常はLAN内のIPの末尾が `.1`（例: `192.168.1.1`）ですが、ルーターにより異なります

---

## ポート構成

| docker-compose | ホスト側ポート | 用途 |
|---|---|---|
| `docker-compose.yml`（GPU） | 8081 | デフォルトGPU版 |
| `docker-compose.cpu.yml` | 8080（DOCKER_HOST_PORT_LLAMA） | CPU版 |
| `docker-compose.high.yml` | 8081 | RTX 5090版 |

---

## Step 1: UbuntuクライアントPCの固定プライベートIP設定

ファイアウォールでIPを指定許可するため、Ubuntu側を先に固定プライベートIPにします。

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:  # インターフェース名は `ip link show` で確認
      addresses:
        - 192.168.1.200/24       # ← プライベートIP（固定）
      routes:
        - to: default
          via: 192.168.1.1       # ← ルーターのプライベートIP
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply

# 確認（プライベートIP 192.168.1.200 が表示されること）
ip addr show eth0
```

---

## Step 2: llama.cppのAPI Key認証を有効化

llama.cppサーバーは `--api-key` オプションでBearer Token認証をサポートしています。
**ファイアウォールに加えて、API Key認証を必ず有効化してください。**

### 2-1. docker-compose.ymlのcommandに `--api-key` を追加

`docker-compose.yml`（または `docker-compose.high.yml`）の `command` セクションに追加します。

```yaml
    command: >
      -m /models/${LLAMA_MODEL_FILE}
      --host 0.0.0.0
      --port 8080
      --api-key ${LLAMA_API_KEY}
      ...（以下既存の設定）
```

### 2-2. .envにAPI Keyを設定

```bash
# .env に追加（推測されにくいランダムな文字列を使用）
LLAMA_API_KEY=sk-local-your-secret-key-here
```

API Keyの生成例:

```bash
# Linux/macOS で安全なランダムキーを生成
openssl rand -hex 32
# 例: a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0

# Windows PowerShell で生成
-join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
```

### 2-3. 認証の動作確認

```bash
# API Keyなし → 401 Unauthorized
curl http://192.168.1.100:8081/v1/models
# 期待結果: {"error":{"message":"Invalid API Key",...}}

# API Keyあり → 正常応答
curl -H "Authorization: Bearer sk-local-your-secret-key-here" \
  http://192.168.1.100:8081/v1/models
# 期待結果: モデル一覧のJSON
```

### 2-4. OpenClaw側のapiKeyを更新

`~/.openclaw/openclaw.json` の `apiKey` をダミー値から実際のキーに変更:

```jsonc
{
  "models": {
    "providers": {
      "local-llm": {
        "baseUrl": "http://192.168.1.100:8081/v1",
        "apiKey": "sk-local-your-secret-key-here",  // ← 実際のAPI Keyに変更
        "api": "openai-completions",
        ...
      }
    }
  }
}
```

---

## Step 3: Windows 11 Pro ファイアウォール設定（セキュリティ最大化）

**すべてPowerShellを管理者権限で実行してください。**

### 3-1. 既存の広範なルールがないか確認

```powershell
# llama.cpp関連の既存ルールを確認
Get-NetFirewallRule -DisplayName "*llama*" 2>$null | Format-Table DisplayName, Enabled, Direction, Action

# もし全IP許可のルールが残っていたら削除
# Remove-NetFirewallRule -DisplayName "llama.cpp API"
```

### 3-2. Ubuntu PCのプライベートIPのみを許可するルールを作成

```powershell
# UbuntuクライアントPCのプライベートIPアドレス（環境に合わせて変更）
$UbuntuIP = "192.168.1.200"

# 受信ルール: 指定プライベートIPからの8081のみ許可
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
- `-RemoteAddress` で Ubuntu PC のプライベートIPだけを許可
- `-Profile Private` でプライベートネットワークプロファイルでのみ有効（パブリック/ドメインでは無効）
- 明示的なブロックルールで他IPを拒否（Windowsファイアウォールは許可ルール優先のため、Allow+Block 併用で確実に制御）

### 3-3. ルールの確認

```powershell
# 作成したルールを確認
Get-NetFirewallRule -DisplayName "llama.cpp API*" |
  Format-Table DisplayName, Enabled, Direction, Action, Profile

# 詳細確認（RemoteAddressを含む）
Get-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" |
  Get-NetFirewallAddressFilter |
  Format-Table RemoteAddress
```

### 3-4. ファイアウォールログの有効化（推奨）

```powershell
# ブロックされた接続をログに記録
Set-NetFirewallProfile -Profile Private -LogBlocked True -LogAllowed False -LogFileName "%SystemRoot%\System32\LogFiles\Firewall\pfirewall.log"

# ログ確認
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" -Tail 20
```

---

## Step 4: 追加のセキュリティ強化策

### 4-1. ネットワークプロファイルの確認

ホームLANが「プライベート」として認識されていることを確認します。

```powershell
# 現在のネットワークプロファイルを確認
Get-NetConnectionProfile | Format-Table Name, NetworkCategory, InterfaceAlias

# もし「Public」になっていたら「Private」に変更
# Set-NetConnectionProfile -InterfaceAlias "イーサネット" -NetworkCategory Private
```

> 「パブリック」のままだとファイアウォールルール（Profile Private）が適用されません。

### 4-2. Docker Desktop のファイアウォール自動ルールを確認

Docker Desktop は自動でファイアウォールルールを追加することがあります。
意図しない広範な許可が入っていないか確認してください。

```powershell
# Docker関連のファイアウォールルールを一覧
Get-NetFirewallRule -DisplayName "*Docker*" |
  Format-Table DisplayName, Enabled, Direction, Action
```

不要な受信許可ルールがあれば無効化を検討してください。

### 4-3. ICMPも制限（オプション）

```powershell
# ping もUbuntu PCのプライベートIPのみに制限
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

---

## Step 5: Windows 11 Pro の固定プライベートIP設定

サーバー側も固定プライベートIPにします。

1. **設定** > **ネットワークとインターネット** > **イーサネット** > **IP割り当て** > **編集**
2. 手動に切り替えてIPv4を有効化:

| 項目 | 値（例） | 備考 |
|---|---|---|
| IPアドレス | `192.168.1.100` | プライベートIP |
| サブネットマスク | `255.255.255.0` | /24 |
| ゲートウェイ | `192.168.1.1` | ルーターのプライベートIP |
| 優先DNS | `8.8.8.8` | Google DNS（パブリック） |
| 代替DNS | `8.8.4.4` | Google DNS（パブリック） |

> DNSサーバー（8.8.8.8等）は**パブリックIP**です。
> これはインターネット上の名前解決サービスのアドレスであり、LAN設定とは別物です。

または PowerShell で設定:

```powershell
# インターフェース名を確認
Get-NetAdapter | Format-Table Name, Status, InterfaceDescription

# 固定プライベートIP設定（インターフェース名は環境に合わせて変更）
New-NetIPAddress -InterfaceAlias "イーサネット" -IPAddress 192.168.1.100 -PrefixLength 24 -DefaultGateway 192.168.1.1
Set-DnsClientServerAddress -InterfaceAlias "イーサネット" -ServerAddresses 8.8.8.8,8.8.4.4
```

---

## Step 6: 疎通確認

### Ubuntu側（クライアントPC）から実行

```bash
# 1. ネットワーク接続（プライベートIP宛）
ping 192.168.1.100

# 2. ポート開放確認（API Key不要のエンドポイント）
curl http://192.168.1.100:8081/health

# 3. API応答（API Key認証あり）
curl -H "Authorization: Bearer sk-local-your-secret-key-here" \
  http://192.168.1.100:8081/v1/models

# 4. 推論テスト（API Key認証あり）
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-your-secret-key-here" \
  -d '{"model":"Qwen3.5-27B-Q4_K_M","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

### 許可されていないPCからの確認（オプション）

```bash
# 別のPC（例: プライベートIP 192.168.1.201）から実行 → タイムアウトするはず
curl --connect-timeout 5 http://192.168.1.100:8081/health
# 期待結果: Connection timed out（ファイアウォールでブロック）
```

Windows側のファイアウォールログでブロック記録を確認:

```powershell
Get-Content "$env:SystemRoot\System32\LogFiles\Firewall\pfirewall.log" -Tail 10 |
  Select-String "DROP"
```

---

## セキュリティ強化ポイントまとめ

本ガイドでは以下の多層防御を実装しています。

| レイヤー | 対策 | 効果 |
|---|---|---|
| **L1: ネットワーク** | プライベートIPのみ使用 | インターネットから到達不可 |
| **L2: バインドアドレス制限** | `DOCKER_HOST_BIND_ADDR` でプライベートIPにのみバインド | `0.0.0.0` 全公開を防止。デフォルト `127.0.0.1` で安全 |
| **L3: ファイアウォール（IP制限）** | `-RemoteAddress` でUbuntuのプライベートIPのみ許可 | LAN内の他PCからもブロック |
| **L4: ファイアウォール（明示的拒否）** | 他IP全てをBlockルールで拒否 | 許可ルール漏れへの安全策 |
| **L5: ファイアウォール（プロファイル制限）** | `-Profile Private` のみで有効 | パブリックネットワーク接続時は自動無効 |
| **L6: API Key認証** | `--api-key` によるBearer Token認証 | IPスプーフィング・ARP偽装への対策 |
| **L7: ログ監視** | ファイアウォールログ有効化 | 不審なアクセスの検知 |
| **L8: Docker自動ルール確認** | Docker Desktopの意図しないルールを監視 | ファイアウォールのバイパスを防止 |
| **L9: 固定IP** | 両PCをDHCPから固定IPに | IPアドレス変動によるルール無効化を防止 |
| **L10: ポート公開禁止** | ルーターでのポートフォワーディング禁止 | インターネットからの直接アクセスを遮断 |

### やってはいけないこと

- `DOCKER_HOST_BIND_ADDR` を `0.0.0.0` にする（全インターフェースに公開される）
- ルーターで8081をポートフォワーディングする（インターネット公開になる）
- ファイアウォールルールの `RemoteAddress` を `Any` にする
- API Keyを空にする、または推測しやすい値にする
- ネットワークプロファイルを `Public` のまま放置する
- `.env` ファイルをGitにコミットする（API Keyが漏洩する）

---

## ルールの管理

```powershell
# ルールを一時無効化
Disable-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"

# ルールを再有効化
Enable-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"

# UbuntuのプライベートIPが変わった場合（例: 192.168.1.201に変更）
Set-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" -RemoteAddress "192.168.1.201"

# 複数PCを許可する場合（カンマ区切り）
Set-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only" -RemoteAddress "192.168.1.200","192.168.1.201"

# ルール完全削除
Remove-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"
Remove-NetFirewallRule -DisplayName "llama.cpp API - Block Others"
```

---

## セキュリティチェックリスト

| # | 項目 | 確認コマンド | 期待結果 |
|---|---|---|---|
| 1 | ネットワークプロファイル | `Get-NetConnectionProfile` | `Private` |
| 2 | 許可ルール | `Get-NetFirewallRule -DisplayName "llama.cpp API - OpenClaw Only"` | Enabled: True, Allow |
| 3 | ブロックルール | `Get-NetFirewallRule -DisplayName "llama.cpp API - Block Others"` | Enabled: True, Block |
| 4 | RemoteAddress制限 | `... \| Get-NetFirewallAddressFilter` | UbuntuのプライベートIPのみ |
| 5 | API Key認証 | `curl http://サーバー:8081/v1/models`（キーなし） | 401 Unauthorized |
| 6 | API Key認証 | `curl -H "Authorization: Bearer ..." ...`（キーあり） | 正常応答 |
| 7 | Docker自動ルール | `Get-NetFirewallRule -DisplayName "*Docker*"` | 不要な受信許可がないこと |
| 8 | ファイアウォールログ | `Get-NetFirewallProfile -Profile Private` | LogBlocked: True |
| 9 | .envがgitignore対象 | `git status` | `.env` が追跡されていないこと |

---

[セットアップ手順](setup_guide.md) | [OpenClaw連携トップ](README.md) | [ドキュメント一覧](../README.md)

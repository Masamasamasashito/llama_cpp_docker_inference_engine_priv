# ネットワーク設定

ホームLAN内でllama.cppサーバーを他PCに公開するためのネットワーク設定です。

---

## ポート構成

| docker-compose | ホスト側ポート | 用途 |
|---|---|---|
| `docker-compose.yml`（GPU） | 8081 | デフォルトGPU版 |
| `docker-compose.cpu.yml` | 8080（LLAMA_PORT） | CPU版 |
| `docker-compose.high.yml` | 8081 | RTX 5090版 |

OpenClawの `baseUrl` にはホスト側ポートを指定します。

---

## ファイアウォール設定

### Windows（PowerShell を管理者権限で実行）

```powershell
# ポート8081の受信を許可
New-NetFirewallRule -DisplayName "llama.cpp API" -Direction Inbound -Port 8081 -Protocol TCP -Action Allow

# 確認
Get-NetFirewallRule -DisplayName "llama.cpp API" | Format-Table

# 削除する場合
# Remove-NetFirewallRule -DisplayName "llama.cpp API"
```

### Linux（ufw）

```bash
# ポート8081の受信を許可
sudo ufw allow 8081/tcp

# 確認
sudo ufw status

# 削除する場合
# sudo ufw delete allow 8081/tcp
```

### Linux（firewalld）

```bash
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

---

## IPアドレスの確認

### サーバーPCのLAN IPを確認

```bash
# Windows
ipconfig
# 「IPv4 アドレス」の値（例: 192.168.1.100）

# Linux
ip addr show | grep "inet "
# または
hostname -I
```

### 固定IPの設定（推奨）

DHCPだとIPが変わる可能性があるため、LLMサーバーPCは固定IPを推奨します。

**Windows:**
1. 設定 > ネットワークとインターネット > イーサネット > IP割り当て > 編集
2. 手動に切り替えてIPv4を有効化
3. IPアドレス、サブネット、ゲートウェイ、DNSを入力

**Linux（netplan の場合）:**

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply
```

---

## 疎通確認チェックリスト

クライアントPCから順番に確認してください。

```bash
# 1. ネットワーク接続（ping）
ping 192.168.1.100

# 2. ポート開放（curl）
curl http://192.168.1.100:8081/health

# 3. API応答（モデル一覧）
curl http://192.168.1.100:8081/v1/models

# 4. 推論テスト
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.5-27B-Q4_K_M","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

| ステップ | 失敗時の確認ポイント |
|---|---|
| 1. ping | 同一LANに接続されているか。ルーターのクライアント一覧を確認 |
| 2. curl health | ファイアウォールでポート8081が開放されているか |
| 3. v1/models | Dockerコンテナが起動しているか（`docker ps`） |
| 4. 推論 | モデルが正常にロードされているか（`docker logs`） |

---

## セキュリティに関する注意

llama.cppサーバーは**認証なし**で動作します。

- ホームLAN内での利用を前提としています
- インターネットに公開しないでください（ポートフォワーディング禁止）
- 外部からアクセスが必要な場合はVPN経由を推奨します

---

[セットアップ手順](setup_guide.md) | [OpenClaw連携トップ](README.md) | [ドキュメント一覧](../README.md)

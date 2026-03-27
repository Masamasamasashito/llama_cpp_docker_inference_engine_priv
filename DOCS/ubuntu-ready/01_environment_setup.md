# 1. 環境構築

Ubuntu 24.04.4 LTS にOpenClawの実行環境を構築します。

---

## 1-1. システムの更新

```bash
sudo apt update && sudo apt upgrade -y
```

## 1-2. 必須パッケージのインストール

```bash
sudo apt install -y curl wget git build-essential
```

## 1-3. Node.js 22 のインストール

OpenClawにはNode.js 22以上が必要です。

```bash
# Node.jsが既にインストールされているか確認
node -v

# Node.js 22をインストール
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 確認
node -v   # v22.x.x が表示されること
npm -v    # 10.x.x 以上が表示されること
```

## 1-4. OpenClawのインストール

```bash
npm install -g @anthropic-ai/openclaw

# 確認
openclaw --version
```

## 1-5. OpenClawの初期セットアップ

```bash
openclaw onboard
```

対話形式でセットアップが始まります。

- **Gateway**: そのままEnterでOK
- **Workspace**: そのままEnterでOK（`~/.openclaw/` に作成される）
- **LLMプロバイダ**: **スキップ**してOK（次のステップで手動設定する）

> セットアップ完了後、`~/.openclaw/openclaw.json` が作成されます。

## 1-6. 固定プライベートIPの設定（推奨）

Windows側のファイアウォールでUbuntuのIPを許可するため、固定IPにします。

```bash
# 現在のIPとインターフェース名を確認
ip addr show
# 例: eth0 に 192.168.1.200/24 が表示される

# デフォルトゲートウェイ（ルーターのIP）を確認
ip route show default
# 例: default via 192.168.1.1 dev eth0
```

netplanで固定IPを設定:

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:  # ← ip addr show で確認したインターフェース名に合わせる
      addresses:
        - 192.168.1.200/24       # ← 固定プライベートIP
      routes:
        - to: default
          via: 192.168.1.1       # ← デフォルトゲートウェイ
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply

# 確認
ip addr show eth0
# 192.168.1.200/24 が表示されること
```

---

[次: ネットワーク確認 →](02_network_verification.md) | [Ubuntu Readyトップ](README.md)

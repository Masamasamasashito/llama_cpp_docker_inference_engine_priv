# 5. セキュリティ対策

Ubuntu側（OpenClaw）はLDIE構成において**脅威が集中する箇所**です。
OpenClawはLLMの出力に基づいてコマンド実行・ファイル操作を行うため、
適切なセキュリティ対策が必要です。

> 詳細な脅威分析は [LDIEモデルセキュリティ評価](../LDIE_ModelSecurityAssessment.md) を参照。

---

## 5-1. 専用ユーザーで実行

OpenClawをroot以外の専用ユーザーで実行し、権限を制限します。

```bash
# OpenClaw専用ユーザーを作成
sudo adduser openclaw-agent
sudo usermod -aG sudo openclaw-agent  # 必要な場合のみ

# 専用ユーザーに切り替え
su - openclaw-agent

# Node.js・OpenClawをこのユーザーでインストール
npm install -g @anthropic-ai/openclaw
```

## 5-2. ワークスペースの制限

OpenClawのワークスペースを限定し、重要ディレクトリへのアクセスを防ぎます。

```bash
# OpenClaw用ワークディレクトリを作成
mkdir -p ~/openclaw-workspace
cd ~/openclaw-workspace

# OpenClawはこのディレクトリ内でのみ実行
openclaw
```

### 保護すべきディレクトリ

| ディレクトリ | リスク | 対策 |
|---|---|---|
| `~/.ssh/` | 秘密鍵漏洩 | OpenClawユーザーにSSH鍵を置かない |
| `/etc/` | システム設定改ざん | sudo権限を必要最小限に |
| `~/.openclaw/` | API Key漏洩 | `openclaw.json` のパーミッションを `600` に |
| `~/` 直下 | 他プロジェクトへの干渉 | ワークスペースを分離 |

```bash
# openclaw.jsonのパーミッションを制限
chmod 600 ~/.openclaw/openclaw.json
```

## 5-3. OpenClawの自動実行制限

OpenClawの設定で、コマンド実行前に確認プロンプトを表示させます。

```jsonc
// ~/.openclaw/openclaw.json に追加
{
  "agents": {
    "defaults": {
      "requireConfirmation": true
    }
  }
}
```

> `requireConfirmation: true` で、OpenClawがコマンド実行前にユーザーの承認を求めるようになります。

## 5-4. モデル選択のセキュリティ

OpenClawのバックエンドLLMとして安全なモデルを選択してください。

| 推奨度 | モデル | 理由 |
|---|---|---|
| **推奨** | Gemma 3 27B | Google製。セキュリティリスク最低。OpenClawバックエンドに最適 |
| 使用可 | Qwen3.5-27B | 性能高い。検閲リスクはあるがローカル実行ならデータ送信なし |
| **非推奨** | DeepSeek R1 32B | NISTが警告。有害コード生成率が高く、OpenClawの自動実行と相性が悪い |

> 詳細は [LDIEモデルセキュリティ評価 - 推奨モデル](../LDIE_ModelSecurityAssessment.md) を参照。

## 5-5. ネットワーク監視

OpenClawが意図しない外部通信をしていないか監視します。

```bash
# OpenClaw実行中のネットワーク接続を確認
ss -tunp | grep node

# 期待される接続先:
# - 192.168.1.100:8081 (Windows LDIEサーバー) のみ
# - それ以外の外部IPへの接続があれば要調査
```

## 5-6. ログの確認

OpenClawの実行ログを定期的に確認し、不審な操作がないか監視します。

```bash
# OpenClawのログ場所
ls ~/.openclaw/logs/

# 最新ログの確認
tail -50 ~/.openclaw/logs/*.log
```

## 5-7. セキュリティチェックリスト

| # | 項目 | 確認方法 | 期待結果 |
|---|---|---|---|
| 1 | 専用ユーザー | `whoami` | `openclaw-agent`（rootではない） |
| 2 | openclaw.json権限 | `ls -la ~/.openclaw/openclaw.json` | `-rw-------`（600） |
| 3 | 安全なモデル | `openclaw.json` の `primary` | Gemma 3 27B or Qwen3.5-27B |
| 4 | ネットワーク | `ss -tunp \| grep node` | LDIEサーバーIPのみ |
| 5 | 自動実行制限 | `openclaw.json` の `requireConfirmation` | `true` |

---

[← 動作確認・自走テスト](04_run_and_test.md) | [Ubuntu Readyトップ](README.md) | [ドキュメント一覧](../README.md)

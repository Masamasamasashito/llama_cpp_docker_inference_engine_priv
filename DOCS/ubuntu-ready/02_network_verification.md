# 2. ネットワーク確認

Ubuntu PCからWindows LDIEサーバーへの疎通を確認します。

> 以下の例では Windows LDIEサーバーのプライベートIPを `192.168.1.100`、
> ポートを `8081`（GPU版デフォルト）としています。実際の値に置き換えてください。

---

## 2-1. Windows側で確認しておく情報

Ubuntu側の作業を始める前に、Windows側の以下の値を控えてください。

| 項目 | 確認方法（Windows PowerShell） | 例 |
|---|---|---|
| プライベートIP | `ipconfig` → IPv4 アドレス | `192.168.1.100` |
| ホスト側ポート | `.env` の `DOCKER_HOST_PORT_LLAMA` | `8081` |
| API Key | `.env` の `LLAMA_API_KEY` | `sk-local-abc123...` |

## 2-2. ping確認

```bash
ping -c 3 192.168.1.100
```

期待結果:
```
64 bytes from 192.168.1.100: icmp_seq=1 ttl=128 time=0.5 ms
```

**失敗した場合:**
- 同一LANに接続されているか確認
- Windows側のファイアウォールでICMPが許可されているか確認

## 2-3. ポート疎通確認

```bash
# curlがなければインストール
sudo apt install -y curl

# ヘルスチェック（API Key不要）
curl -v http://192.168.1.100:8081/health
```

期待結果:
```json
{"status":"ok"}
```

**失敗した場合:**
- Windows側でDockerコンテナが起動しているか（`docker ps`）
- `.env` の `DOCKER_HOST_BIND_ADDR` がプライベートIP（`192.168.1.100`）になっているか
- Windows側ファイアウォールでUbuntuのIPが許可されているか
- ポート番号が合っているか（GPU: `8081`, CPU: `8082`, High: `8083`）

## 2-4. API Key認証の確認

```bash
# API Keyなしでアクセス → 401が返ること
curl -s -o /dev/null -w "%{http_code}" http://192.168.1.100:8081/v1/models
# 期待結果: 401

# API Keyありでアクセス → 200が返ること
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer sk-local-your-secret-key-here" \
  http://192.168.1.100:8081/v1/models
# 期待結果: 200
```

## 2-5. 推論テスト API Keyあり

```bash
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-your-secret-key-here" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, who are you?"}],
    "max_tokens": 50
  }'
```

JSONレスポンスが返ればネットワーク確認は完了です。

## 2-6. 推論テスト API Keyなし

```bash
curl -X POST http://192.168.1.100:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, who are you?"}],
    "max_tokens": 50
  }'
```

curl -X POST http://192.168.1.100:8081/v1/chat/completions -H "Content-Type: application/json" -d '{ "messages": [{"role": "user", "content": "Hello, who are you?"}], "max_tokens": 50 }'
```

JSONレスポンスが返ればネットワーク確認は完了です。


## 2-6. 確認チェックリスト

| # | 確認項目 | コマンド | 期待結果 |
|---|---|---|---|
| 1 | ping | `ping -c 3 192.168.1.100` | 応答あり |
| 2 | health | `curl http://...:8081/health` | `{"status":"ok"}` |
| 3 | 認証なし | `curl http://...:8081/v1/models` | 401 |
| 4 | 認証あり | `curl -H "Authorization: ..." .../v1/models` | 200 + モデル一覧 |
| 5 | 推論 | `curl -X POST .../v1/chat/completions` | 生成テキストが返る |

---

[← 環境構築](01_environment_setup.md) | [次: OpenClaw設定 →](03_openclaw_config.md) | [Ubuntu Readyトップ](README.md)

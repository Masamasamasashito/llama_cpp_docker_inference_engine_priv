# 4. 動作確認・自走テスト

OpenClawがWindows LDIEサーバーのローカルLLMで正常に動作するか確認します。

---

## 4-1. OpenClawの起動

```bash
openclaw
```

OpenClawのプロンプトが表示されれば起動成功です。

## 4-2. 基本的な会話テスト

OpenClawのプロンプトで以下を入力:

```
こんにちは。あなたは何ができますか？
```

LDIEサーバーのローカルLLMから応答が返ればAPI連携は成功です。

## 4-3. ファイル操作テスト

OpenClawがローカルLLMの応答に基づいてファイルシステムを操作できるか確認します。

```bash
# テスト用ディレクトリを作成
mkdir -p ~/openclaw-test
cd ~/openclaw-test
echo "This is a test file." > test.txt

# OpenClawを起動
openclaw
```

OpenClawに以下を指示:

```
このディレクトリのファイル一覧を取得して、test.txtの内容を教えて
```

OpenClawが `ls` や `cat` コマンドを自律的に実行してファイル内容を返せば、
AIエージェントとして正常に動作しています。

## 4-4. コマンドライン直接実行テスト

対話モードを使わず、ワンショットで指示:

```bash
openclaw "現在のディレクトリ構成をツリー形式で表示して"
```

## 4-5. 応答速度の確認

```bash
# 簡単な質問で応答時間を計測
time openclaw "1+1は？"
```

| モデル | 目安応答時間（RTX 5090） |
|---|---|
| Qwen3.5-9B | 1-3秒 |
| Gemma 3 27B | 3-8秒 |
| Qwen3.5-27B | 3-8秒 |
| Qwen3-32B | 5-10秒 |

> ネットワークレイテンシ（LAN内 <1ms）は無視できるレベルです。
> 応答時間のほとんどはLLMの推論時間です。

## 4-6. トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| OpenClawが起動しない | `node -v` で22以上か確認。`npm install -g @anthropic-ai/openclaw` を再実行 |
| `Connection refused` | Windows側のLDIE・ファイアウォール・バインドアドレスを確認。[ネットワーク確認](02_network_verification.md) を再実行 |
| `401 Unauthorized` | `openclaw.json` の `apiKey` とWindows `.env` の `LLAMA_API_KEY` が一致しているか確認 |
| `Model not found` | `openclaw.json` の `id` とLDIEの `/v1/models` のIDが一致しているか確認 |
| 応答が非常に遅い | `openclaw.json` の `contextWindow` がLDIEの `LLAMA_CTX_SIZE` と合っているか確認。Windows側で `nvidia-smi` でGPU使用率を確認 |
| OpenClawが勝手に操作する | [セキュリティ対策](05_security.md) を参照。自動実行の制限を設定 |

---

[← OpenClaw設定](03_openclaw_config.md) | [次: セキュリティ対策 →](05_security.md) | [Ubuntu Readyトップ](README.md)

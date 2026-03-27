# 3. ComfyUI WebUI ガイド

ComfyUIはノードベースのビジュアルエディタで、ブラウザから動画生成ワークフローを構築・実行できます。

> WebUIはLLMサーバーPC（Windows 11 Pro）のブラウザからのみ利用します。

---

## アクセス方法

ComfyUI起動後、Windows 11 Proのブラウザで以下にアクセス:

```
http://localhost:8188
```

> ポートを変更している場合は `.env` の `DOCKER_HOST_PORT_COMFYUI` の値に合わせてください。

---

## ComfyUI WebUIの特徴

ComfyUIはllama.cppの組み込みWebUI（テキストチャット画面）とは大きく異なります。

| 項目 | ComfyUI WebUI | llama.cpp WebUI |
|---|---|---|
| インターフェース | ノードベース（接続線でワークフロー構築） | ChatGPT風テキストチャット |
| 操作方法 | ノードを配置→接続→Queue Prompt | テキスト入力→送信 |
| 出力 | 動画・画像ファイル | テキスト |
| カスタマイズ | ワークフローを自由に組み替え可能 | パラメータ調整のみ |

---

## 基本操作

### ワークフローのロード

1. WebUI画面で `Load` ボタンをクリック
2. `.json` ワークフローファイルを選択
3. ノードグラフが表示される

### 動画生成の実行

1. プロンプトノードにテキストを入力（例: `A cat walking on a sunny street`）
2. `Queue Prompt` ボタンをクリック
3. 進捗バーが表示され、生成が開始
4. 完了後、出力ノードにプレビューが表示される
5. 生成ファイルは `ComfyUI/output/` に保存される

### パラメータの変更

ノード内のパラメータを直接クリックして変更できます。

| パラメータ | 説明 | 推奨値 |
|---|---|---|
| `prompt` | 生成したい動画の説明テキスト | 英語推奨 |
| `negative_prompt` | 避けたい要素 | `blurry, low quality, distorted` |
| `steps` | 生成ステップ数（多いほど高品質・遅い） | 20-30 |
| `cfg` | プロンプトへの忠実度（高いほど忠実） | 7.0-7.5 |
| `width` / `height` | 解像度 | モデルにより異なる |
| `num_frames` | フレーム数 | 24-48 |
| `seed` | 再現性のためのシード値 | 任意の整数 |

---

## モデル別の操作

### LTX-Video（最速）

- 解像度: 512x512 または 768x512
- ステップ: 20で十分
- 生成時間: 5秒動画を約4秒

### Wan 2.2 14B（最高品質）

- 解像度: 最大720p（720x480）
- ステップ: 30推奨
- 生成時間: 4-15分/クリップ
- VRAM: ~16GB

### Wan 2.1 1.3B（軽量版）

- 解像度: 512x512
- ステップ: 25
- 生成時間: 中程度
- VRAM: ~8GB

### HunyuanVideo 1.5（人物特化）

- カスタムノードのインストールが必要
- 解像度: 最大720p
- ステップ: 30推奨
- 生成時間: 4-15分/クリップ
- 人物の顔が最も自然に生成される

---

## カスタムノードの管理

ComfyUI Managerを使うと、カスタムノード（HunyuanVideo等）の追加・更新が簡単にできます。

```bash
# ComfyUI Manager のインストール（初回のみ）
cd ComfyUI/custom_nodes/
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

インストール後、WebUI右上の `Manager` ボタンからカスタムノードの検索・インストールが可能です。

---

## トラブルシューティング

| 問題 | 原因・対策 |
|---|---|
| ページが開かない | ComfyUIコンテナが起動しているか `docker ps` で確認 |
| ノードが赤くなる | 必要なカスタムノードが未インストール。ComfyUI Managerで追加 |
| 「CUDA out of memory」 | VRAM不足。解像度を下げるか、より小さいモデル（LTX-Video, Wan 1.3B）を使用 |
| 生成が終わらない | 14Bモデルは4-15分かかる。進捗バーで確認 |
| 出力ファイルが見つからない | `ComfyUI/output/` ディレクトリを確認 |

---

[セットアップ手順](01_setup_guide.md) | [利用可能モデル一覧](02_available_models.md) | [動画生成トップ](README.md)

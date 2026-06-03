# Partner Basecamp · セッション教材（日本語版）

> このディレクトリは、リポジトリ直下の英語版教材を `day1` / `day2` の階層そのままにミラーした **日本語版（i18n: `ja/`）** です。シナリオ・固有名詞・コードは原典に忠実なまま、解説文・コメント・教材テキストのみを日本語化しています。日本の製品開発に合わせて適応する際の土台としてご利用ください。

このリポジトリには、Partner Basecamp セッションで使用するすべてのノートブックと関連ファイルが含まれています。教材は実施順に、日（day）とセッションごとに整理されています。

---

## ダウンロード方法

### 方法A — ZIP でダウンロード（Git 不要）
1. このページ右上の緑色の **Code** ボタンをクリックします。
2. **Download ZIP** を選択します。
3. ダウンロードしたファイルをコンピューター上で解凍すると、すべてが入った `Basecamp-Exercises-main` フォルダが得られます。

### 方法B — Git でクローン
```bash
git clone https://github.com/victorsteeb/Basecamp-Exercises.git
```

---

## 収録内容

### Day 1
| フォルダ | セッション | 種別 |
|--------|---------|------|
| `day1/01_claude-code-workshop` | Claude Code Workshop | オフラインガイド |
| `day1/02_developer-platform` | Developer Platform | ビルドアロング |
| `day1/03_prompt-rescue` | Prompt Rescue | ビルドアロング |
| `day1/04_diagnosing-ai-problems` | Diagnosing AI Problems | セッション教材 |

### Day 2
| フォルダ | セッション | 種別 |
|--------|---------|------|
| `day2/01_evals` | Evals | ビルドアロング |
| `day2/02_inference-optimization` | Inference Optimization | ビルドアロング |

各フォルダには、演習の説明とステップごとの実行手順を記載した独自の README があります。

---

## API キー
すべてのビルドアロング・セッションには Anthropic の API キーが必要です。各ノートブックの上部付近に、キーを貼り付けるためのセルがあります。

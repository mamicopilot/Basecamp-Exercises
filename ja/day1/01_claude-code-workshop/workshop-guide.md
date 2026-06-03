> 原典は workshop-guide.pdf（PDF）。本ファイルはその日本語訳です。

# ワークショップ ガイド

フルスタック在庫管理アプリケーションを使ったステップバイステップ Claude Code ガイド

## 前提条件

- Claude Code のインストールとセットアップ済み（docs.anthropic.com）
- ターミナル / Windows PowerShell または コードエディタ（VS Code 推奨）を起動済み

> **プロヒント: 権限設定について**
>
> Claude Code は次のような操作が必要になると、その都度許可を求めます。
> **設定と権限:** エージェントのスコープを絞る細かい権限制御をサポートしています。
>
> - プロジェクト内のファイルを変更する
> - bash コマンドを実行する
> - 新しいツールをインストールする（ステップ 9 の Playwright MCP など）
>
> 各アクションの許可を求めるプロンプトが表示されたら Enter を押して承認するか、代わりに行う内容を Claude に伝えてください。（上級ユーザーは `.claude/settings.json` で自動承認を設定できます）
>
> これにより、コードベースで何が起きるかを常に把握できます。

ワークショップへようこそ！各ステップを展開して手順を進め、終わったらライブサイトの「I'm done」ボタンをクリックして得点を獲得し、リーダーボードを上りましょう。

---

## トラブルシューティング & キーボードショートカット

### トラブルシューティング

- **何かが壊れて詰まったとき** — エラーメッセージ全体をコピーして Claude Code に貼り付ける
- **Claude が画面の内容を見られないとき** — スクリーンショットを撮って貼り付ける（Ctrl+V / Cmd+V）
- **Claude の返答が機能しないとき** — 反復する: 何がうまくいかなかったか、期待していた結果を説明する
- **Claude が複雑さに苦戦しているとき** — `think harder` または `ultrathink` を試して拡張思考をトリガーする
- **会話全体を確認したいとき** — `Ctrl+O` を押してトランスクリプト ビューアを開く
- **サーバーが起動しないとき** — `/start` を実行するか、手動でポートを解放する: `lsof -ti:3000,8001 | xargs kill`

### キーボードショートカット

| キー | 動作 |
|---|---|
| `Enter` | ツールアクションを承認する |
| `Escape` | 拒否 / キャンセル |
| `Shift+Tab` | プランモードの切り替え |
| `!` | Bash モードに入る（シェルコマンドを実行） |
| `#` | メモリモードに入る |
| `@` | ファイルを参照する |
| `Ctrl+O` | トランスクリプト ビューアを開く |
| `Ctrl+C` | Claude を中断する |

### リソース

- Claude Code ドキュメント
- Claude Code ビデオコース
- Claude Code ベストプラクティス

---

## 12 のコアステップ（230 pts）

---

## ステップ 1: リポジトリをフォーク & クローンする

**1** **10 pts**

上流リポジトリを自分の GitHub アカウントにフォークし、フォークをクローンする

まず、自分専用のコピーを GitHub 上に作成するために在庫管理デモアプリをフォークし、クローンしてワーキングブランチを作成します。

### オプション 1 — フォーク + Git（推奨）

https://github.com/beck-source/inventory-management にアクセスし、右上の **Fork** をクリックします。

フォークをクローンします。

```
git clone git@github.com:YOUR_USERNAME/inventory-management.git
```

ディレクトリに移動してワーキングブランチを作成します。

```
cd inventory-management && git checkout -b new_features
```

### オプション 2 — ZIP をダウンロードする（フォークをスキップ）

GitHub リポジトリのページから ZIP をダウンロードし、解凍してそのディレクトリに `cd` します。その後ブランチを初期化します。

```
git init && git add -A && git commit -m "initial commit"
git checkout -b new_features
```

> オプション 2 はフォークのステップをスキップします。GitHub へのプッシュや後のステップでの GitHub App 連携は使用できません。

---

## ステップ 2: Claude Code を起動する

**2** **10 pts**

プロジェクトディレクトリ内のターミナルを開き、Claude Code を起動します。

```
claude
```

Claude Code が起動したら、使用するモデルを選択します。

```
/model
```

一覧からモデルを選択します。このワークショップではどのモデルでも問題なく動作します。

---

## ステップ 3: 在庫管理アプリをローカルで起動する

**3** **15 pts**

次のプロンプトを Claude Code に貼り付けます。

```
Install dependencies and start the development servers and open up the
frontend and backend in my respective browser windows.
```

Claude は以下を実行します。

- Vue 3 フロントエンドの npm 依存関係をインストールする（`cd client && npm install`）
- FastAPI バックエンドの Python 依存関係をインストールする（`cd server && uv sync`）
- バックエンドサーバーをポート `8001` で起動する
- フロントエンドの開発サーバーをポート `3000` で起動する

両サーバーが起動したら、ブラウザで `http://localhost:3000` を開き、アプリを確認します。

数分かけてアプリを探索します。各ページをクリックして内容を把握しましょう。

- **Dashboard** — KPI カード、売上グラフ、注文サマリー
- **Inventory** — 倉庫ごとの在庫水準
- **Orders** — ステータスフィルター付きの注文トラッキング
- **Spending** — 支出分析とその内訳
- **Demand** — トレンド付きの需要予測
- **Backlog** — バックログ監視

> 注意: このアプリには意図的にバグが仕込まれています :)

---

## ステップ 4: CLAUDE.md ファイルを編集する

**4** **15 pts**

Catalyst Components プロジェクトには、コーディング規約・システムアーキテクチャ・技術スタック・従うべきルールについて Claude に継続的な指示を与える `CLAUDE.md` ファイルが必要です。このリポジトリにはすでに含まれています。

> `CLAUDE.md` のない新規プロジェクトを始める場合は、`/init` を実行すると自動で生成されます。

### @ファイルメンションの使い方

プロンプト内で `@` を使って任意のファイルを参照できます。試してみましょう。

```
Print out exactly what is in @CLAUDE.md
```

Claude はファイルを読み込み、その内容を出力します。`@` 構文はプロジェクト内の任意のファイルで使用できます。

### CLAUDE.md ファイルを編集する 3 つの方法

#### 方法 1 — # メモリモードを使う（推奨）

プロンプトで `#` を押してメモリモードに入ります。これにより、トークンを消費せずに `CLAUDE.md` に直接書き込めます（Claude がリクエストを処理する必要がないため）。

```
# Always document non-obvious logic changes with comments
```

#### 方法 2 — エディタで直接編集する

`CLAUDE.md` をテキストエディタ（VSCode、vim など）で開いて変更します。こちらもトークンのコストはゼロです。

#### 方法 3 — Claude に編集を依頼する

```
Edit my CLAUDE.md file to add "Always document non-obvious logic changes
with comments"
```

Claude はファイルを開き、指示を追加して保存します。

> 方法 1 と方法 2 は無料（トークン消費なし）。方法 3 は Claude がリクエストを処理して編集を行うためトークンを使用します。指示の整理や言葉の選び方を Claude に任せたい場合は方法 3 を使います。

### 永続メモリシステム

Claude には 2 つの永続メモリシステムがありますが、最終的にはどちらも同じ場所（個人用の `./.claude/CLAUDE.md`）に記録されます。

自動的に読み込まれる永続指示を含む Markdown ファイル: `/CLAUDE.md`

| ファイル | スコープ |
|---|---|
| `./CLAUDE.md` | プロジェクト（git 経由で共有） |
| `./.claude/rules/*.md` | トピック別ルール |
| `./.claude/CLAUDE.md` | 個人用、全プロジェクト共通 |
| `./CLAUDE.local.md` | 個人用、このプロジェクト専用 |

`/memory` コマンドは個人用の `./.claude/CLAUDE.md` に書き込み、設定のオンザフライな記録に便利です。

---

## ステップ 5: コードベースを探索する

**5** **20 pts**

Claude にプロジェクトを調査させてアーキテクチャ概要を生成するよう依頼します。

```
I want to understand this codebase. Investigate the project and create a
simple, professional HTML-based architecture page showing the system
architecture, tech stack, and data flow. Then open the file in a browser
window.
```

Claude は以下を実行します。

- ディレクトリ構造を探索する
- 主要ファイルを読み込んでアーキテクチャを把握する
- Vue 3 フロントエンド、FastAPI バックエンド、JSON データフローを示す視覚的なダイアグラム付き HTML ページを生成する
- ブラウザでファイルを開く

これにより、Claude Code が初めて見るコードベースに素早くオンボーディングできることが体験できます。

---

## ステップ 6: 機能を構築する

**6** **30 pts**

これがワークショップのコアです。プランモードを使って Claude に機能を実装前に設計させ、その後結果を反復改善します。

### プランモードに入る

`Shift+Tab` を押して Claude をプランモードに切り替えます。プランモードでは、Claude はコードを一切書く前に計画を提示し、承認を待ちます。

以下の 2 つの機能オプションから 1 つを選択します。

---

### オプション A: 予算ベースの補充ツール

需要予測データを使って、予算に基づいて補充すべき商品を推奨する新しいタブを構築します。次のプロンプトを貼り付けます。

```
Build a new "Restocking" tab in the app. It should have:
1. A budget slider that lets the user set their available budget
2. Based on the budget, recommend items from the demand forecast to restock
3. A "Place Order" button that submits the restocking order
4. The submitted order should appear in the existing Orders tab with a new
"Submitted Orders" section showing delivery lead time
```

> AskUserQuestion ツールを活用してください！

Claude が計画を提示します。内容を確認し、問題なければ計画を承認して実装させます。Claude は AskUserQuestion ツールを使って確認事項を質問してくることがあります（例: 「予算スライダーの範囲は $0〜$50,000 にしますか？それともデータから範囲を決定しますか？」）。質問が来たらその都度回答してください。

Claude が完了したらブラウザで機能をテストします。完璧でない部分があるかもしれません。その後は反復: 次に何を改善したいかを選択します。

> **プロヒント:** Claude はインテリジェントな思考パートナーです。SDLC 全体にわたる計画・発見・アイデア出し・設計を支援し、バイアスや抜け漏れの特定と批判的思考のサポートができます。レビュー・ドキュメント・アーキテクチャ設計・視覚ダイアグラムの作成も可能です。スクリーンショットを会話に貼り付けて（Ctrl+V）確認させることもできます。

---

### オプション B: SaaS スタイルの UI リデザイン

再利用可能な Claude Code スキルを使って、アプリのインターフェースをシンプルなレイアウトから洗練されたモダンな SaaS スタイルのデザインに変換します。

#### パート 1 — スキルを作成する

```
I want to build a skill that redesigns a Vue 3 application's UI into a
modern
SaaS-style interface with a vertical navigation sidebar on the left instead
of
a top nav bar, consistent spacing, and a polished professional look.
```

Claude がスキルの動作を形作るためのフォローアップ質問をします。回答してスキルの挙動を定義します。

#### パート 2 — スキルを適用する

```
Use the frontend-design skill to redesign this inventory management app
into a
modern SaaS-style interface with:
1. Vertical navigation bar on the left side instead of the top
2. Clean, modern card layouts
3. Professional SaaS aesthetic
```

> AskUserQuestion ツールを活用してください！

```
Add a collapsible sidebar with icons-only mode for smaller screens.
```

Claude が計画を提示します。承認して実装完了を待ちます。その後 `http://localhost:3000` でブラウザ上の変更をテストします。

---

## ステップ 7: コンテキスト管理

**7** **10 pts**

機能を構築した後、コンテキストウィンドウがいっぱいになってきている可能性があります。Claude Code はこれを管理するツールを提供しています。

コンテキスト使用量を確認します。

```
/context
```

会話・ファイル・ツールで使用中のコンテキスト量の内訳が表示されます。

コンテキストを圧縮します。

```
/compact
```

これまでの会話を要約して古いコンテキストを解放し、新しい作業のためのスペースを確保します。Claude は重要な情報を保持します。

`/compact` に指示を付けて、要約時に優先すべき内容を Claude に伝えることもできます。

```
/compact keep the details of the restocking feature
```

これにより、アクティブに構築中の機能など重要なコンテキストが圧縮後も保持されます。

---

## ステップ 8: Playwright MCP を追加する

**8** **15 pts**

MCP サーバーは、ブラウザ自動操作・データベースアクセス・API 連携など、外部ツールへの接続能力を Claude に与えます。ローカルマシンの枠を超えて Claude にできることを拡張するコネクタープロトコルと考えてください。（MCP についてさらに詳しく）

`!` を押して Bash モードに入り、次を実行します。

```
! claude mcp add playwright npx @playwright/mcp@latest
```

これにより Playwright MCP サーバーがインストールされ、Claude がブラウザを制御できるようになります。

---

## ステップ 9: Playwright MCP を使ってテストする

**9** **20 pts**

Claude Code を再起動して MCP の設定を読み込みます。

```
/exit
claude
```

コンテキストへの影響を確認します。

```
/context
```

MCP サーバーがツール定義のためにコンテキスト予算を消費していることに注意してください。複数の MCP サーバーを使う際に把握しておくべき重要な点です。

> このリポジトリには `.mcp.json` に Playwright の設定が既に含まれていますが、自分のプロジェクトに MCP サーバーを追加する方法を習得するためにインストール手順を解説しています。

MCP サーバーが読み込まれていることを確認します。

```
/mcp
```

`playwright` が一覧に表示されているはずです。

次のプロンプトを Claude Code に貼り付けて、Playwright を使ってアプリをテストします。

```
Use Playwright MCP to test the app:
1. Start the development servers
2. Navigate to localhost:3000
3. Take a screenshot of the dashboard
4. Click through the main navigation tabs and verify each page loads
```

Claude はブラウザを起動し、アプリをナビゲートし、スクリーンショットを撮って、確認した内容を報告します。何か問題があればそのまま反復し続けます。

> **プロヒント:** Claude は素晴らしい先生であり、ほとんどの技術的な問題を解決するのに役立ちます。パッケージ依存関係のインストール・管理・処理、エラーのトラブルシューティングとアプリのデバッグ、bash コマンドや git によるソース管理の実行、CI/CD との統合も対応しています。

その後は反復: 次に何を改善したいかを選択します。

---

## ステップ 10: Claude Code を GitHub に接続する

**10** **15 pts**

GitHub App は Claude Code を GitHub アカウントに接続し、Claude がプルリクエストの読み書き・コードレビュー・クラウドからのトリガー実行を行えるようにします。次のステップで PR を開く前に今すぐインストールしておきましょう。

### 1. インストールコマンドを実行する

Claude Code 内で実行します。

```
/install-github-app
```

Claude がインストールする GitHub ワークフローの選択を求めます。両方を有効にします。

- **@Claude Code** — `@claude` をイシューや PR コメントでタグ付けして Claude のサポートを受ける
- **Claude Code Review** — すべての新規 PR に対して自動コードレビューを実行する

ブラウザのフローに従って、フォークした `inventory-management` リポジトリで GitHub App を承認します。

### 2. @claude PR をマージする

コマンド完了後、Claude は GitHub Actions のワークフローファイルをリポジトリに追加する事前入力済み PR を作成します。ブラウザでその PR を開いてマージします。

マージ後、フォークで Claude が有効になります。

- **Claude Code Review を有効にした場合** — 新しい PR ごとに自動コードレビューコメントがトリガーされます
- **@Claude Code を有効にした場合** — イシューや PR コメントで `@claude` をタグ付けするとオンデマンドで Claude を呼び出せます

> ステップ 1 でリポジトリをフォークしたことを確認してください。GitHub App は上流リポジトリではなく、自分のフォークで承認される必要があります。

---

## ステップ 11: コミット、プッシュ、PR を開く

**11** **20 pts**

機能の作業をコミットし、ブランチをプッシュしてプルリクエストを開きます。前のステップでワークフローをマージしたため、Claude が PR を自動的にレビューします。

```
Commit the changes you've made in this branch, push the branch to GitHub,
and open a pull request.
```

Claude は変更をステージし、説明的なコミットメッセージを書き、ブランチをフォークにプッシュして PR を開きます。

ブラウザで PR を開きます。1 分以内に Claude が自動コードレビューコメントを投稿するはずです。

PR コメントで `@claude` をタグ付けしてフォローアップ質問をしたり、特定の変更を依頼したりすることもできます。

次のステップに進む前に PR をマージしてください。

---

## ステップ 12: 高度なワークフロー

**12** **25 pts**

上記のステップはコアチュートリアルをカバーしています。以下は残り時間で探索できる 5 つの強力な Claude Code 機能です。

---

### スキル — 再利用可能な指示セット

スキルは、特定のドメイン向けのプレイブックのように、Claude に専門的なタスクを教える再利用可能な指示セットです。

**使いどころ:**
- チームワークフローの標準化
- 繰り返し可能なプロセスの作成
- ドメイン固有のコード生成

**試してみる**

Vue コンポーネント分析スキルを作成します。

```
I want to build a skill that analyzes Vue component structure and
suggests
optimizations for performance and code reuse
```

スキルのスコープと動作を定義するために Claude のフォローアップ質問に回答します。Claude がスキルを構築してテストします。

---

### サブエージェント — 専門化された Claude エージェント

特定のタスクにスコープを絞った専門の Claude エージェントです。複雑なサブタスクをフォーカスされた専門家に委任します。

**使いどころ:**
- コードレビューとセキュリティ監査
- デバッグとドメイン固有の分析
- フォーカスされたエージェントが有効なあらゆるタスク

**試してみる**

デバッガーサブエージェントを作成します。

```
Create a new Debugger subagent that specializes in investigating
runtime errors,
reading stack traces, and suggesting fixes. It should have access
to Read, Grep,
Glob, and Bash tools.
```

その後テストします。

```
Use the debugger agent to investigate any console errors on the
Dashboard page.
```

---

### フック — 自動イベント応答

Claude Code のイベント（ファイル編集・ツール呼び出しなど）に応じて自動実行されるシェルコマンドです。

**使いどころ:**
- 保存時の自動フォーマット
- ツール使用のロギング
- コード標準とプレコミットチェックの強制

**試してみる**

Prettier をインストールしてフォーマットフックを追加します。

```
npm install --save-dev prettier
```

`/hooks` を使ってフックを設定するか、`~/.claude/settings.json` に手動で追加します。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

テストします。

```
Add an extra function to api.js with deliberately messy formatting
```

Claude がファイルを書き込んだ後、フックが自動的に整形するはずです。

---

### プラグイン — コミュニティ製ワークフローパッケージ

スラッシュコマンド・スキル・規約をインストール可能なワークフローにまとめたコミュニティ製パッケージです。

**使いどころ:**
- チーム/組織全体のワークフロー採用
- CI/CD パターンの標準化
- ドメイン固有コマンドの追加

**試してみる**

マーケットプレイスからプラグインを参照して追加します。

```
/plugin marketplace add https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
```

特定のワークフローをインストールします。

```
/plugin install epcc-workflow
```

プラグインのワークフローを使用します。

```
/epcc-code Add a CSV export button to the inventory page
```

---

### エージェントチーム — 協調するマルチエージェントワークフロー

チームとして連携する複数の Claude Code インスタンスを調整します。1 つの親に報告するサブエージェントとは異なり、チームメイトはタスクリストを共有し、独立して調査し、互いに直接メッセージを送り合います。

**使いどころ:**
- 複数の視点からの調査とレビューを同時実行
- エージェントが競合する仮説を議論するデバッグ
- 異なるチームメイトがそれぞれ担当するクロスレイヤー作業（フロントエンド・バックエンド・テスト）

**試してみる**

まず、エージェントチームを有効にします（実験的機能）。Claude Code に次を貼り付けます。

```
/config
```

**設定の編集** を選択し、実験フラグを追加します。

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Claude Code を再起動して次を試します。

```
Create an agent team with 3 teammates to audit this inventory
management app from
different angles:
- Security Auditor: find vulnerabilities (injection, auth issues,
data exposure)
- Performance Analyst: find bottlenecks (slow queries, unnecessary
re-renders,
large payloads)
- UX Reviewer: find usability issues (accessibility, responsive
design, error
handling)

Have them investigate in parallel, share findings with each other,
and challenge
each other's severity ratings. Produce a single prioritized action
plan at the end.
```

チームメイトが連携する様子を観察します。`Shift+Down` で各エージェントを切り替えて個別の進捗を確認できます。リードエージェントが最終レポートに調査結果をまとめます。

---

### ワークツリー — 独立した並行ブランチ

現在の作業に影響を与えずに、リポジトリの別のコピーで Claude が作業できる独立した git ブランチです。

**使いどころ:**
- 並行機能開発
- 破棄する可能性がある試験的な変更
- メインの作業をクリーンに保ちながら実験を実行する

**試してみる**

現在のブランチに影響を与えずに機能をプロトタイピングするためにワークツリーを使用します。

```
Use a worktree to prototype a dark mode toggle for the app without
affecting my
current branch. Create the feature, test it, and show me the
result.
```

Claude はリポジトリの独立したコピーを作成し、そこで変更を行い、ワーキングブランチには手を加えません。

---

## ★ エキスパートチャレンジ: バグバウンティ — Reports ページを修正する

**25 pts**

**ミッション:** Reports ページには複数のバグが潜んでいます。視覚的に発見し、Claude Code を使ってすべて特定して修正してください。

### ステップ 1: バグを発見する（約 2 分）

`http://localhost:3000` でアプリを起動した状態で、Reports ページを調査します。

- 右上の言語切り替えボタンを使って言語を切り替えます。アプリのページをナビゲートします。Reports ページについて何か違いに気づきますか？
- フィルターを試します。時間帯フィルター（例: "January"）または倉庫フィルター（例: "San Francisco"）を設定します。各ページを確認します。Reports ページは反応しますか？
- ブラウザの DevTools（F12 または Cmd+Option+I）を開き、Console タブを確認します。Reports ページ周辺をクリックします。何が見えますか？

視覚的な確認だけで少なくとも 3 つの異なるカテゴリのバグが見つかるはずです。

### ステップ 2: Claude Code でバグを修正する（約 3〜5 分）

Claude Code に次のプロンプトを貼り付けます。

```
The Reports page (/reports) has multiple bugs compared to the rest of the
app.
I found that:
1. It doesn't translate to Japanese when I switch languages
2. It ignores the global filter bar
3. It spams the browser console with debug logs

Investigate the Reports page code, identify ALL the issues (there are more
than
these 3), and fix them. Look at how other pages like Dashboard and Orders
are
implemented for reference.
```

Claude は以下を実行します。

- `Reports.vue` を読み込んで `Dashboard.vue` などの正常動作するページと比較する
- すべてのバグを特定する（8 件以上あります）
- アプリの他の部分で使われているパターンに合わせてコンポーネントをリファクタリングする
- `App.vue` の「Reports」ナビタブの翻訳を修正する
- `http://localhost:3000/reports` を更新して次の点を確認する
  - 言語切り替えが機能する
  - フィルターがデータを更新する
  - `console.log` のスパムが解消された
  - コードが Composition API のパターンに従っている

---

## ストレッチゴール

Backlog ページ（`/backlog`）を修正します。同じ i18n の問題があります。すべての文字列が翻訳関数 `t()` を使わずに英語でハードコードされています。

---

## → さらに進む: 自分のものにする

**0 pts**

コードベースの探索、機能のリリース、テストの作成、PR のレビュー、GitHub との連携という Claude Code の全ワークフローを体験しました。これが基礎です。あとはスクリプトを離れて自由に進みましょう。

### 始めるためのアイデア

- **新機能を追加する** — 在庫不足アラート、検索バー、CSV エクスポートボタン、ダークモードの切り替え。Claude にエンドツーエンドで実装させます。
- **アプリをリスタイルする** — カラーパレットの変更、フォントの変更、ナビのリデザイン。試してみましょう: "Redesign the app with a dark navy and orange theme."
- **データモデルを改善する** — サプライヤー追跡、商品カテゴリ、または簡単な監査ログを追加します。Claude にマイグレーションを書かせて UI につなげます。
- **テストを拡充する** — Claude にカバレッジを増やさせ、エッジケースを追加させるか、GitHub Actions で CI ワークフローをセットアップさせます。
- **意図的に壊す** — バグを仕込んで、1 つのプロンプトで Claude がどれだけ速く見つけて修正できるか確かめます。

### 取り組み方

- 求めるものを平易な言葉で説明します。Claude はコードベースを読み込み、変更を計画して実装します。
- 結果が思い通りでなければ遠慮なく押し戻します。チームメイトと同じように反復します。
- 間違いはありません。本当のオープンエンドな問題を与えたときに Claude Code が何をできるかを感じ取ることが目標です。

> **さらに深く:** Claude Code ベストプラクティスガイドで、プロンプトパターン・CLAUDE.md の設定・エージェントワークフローなどのヒントを確認してください。

---

*出典: claude-code-workshop.netlify.app — Claude Code Workshop Guide。すべてのエクササイズを展開した状態で表示。*

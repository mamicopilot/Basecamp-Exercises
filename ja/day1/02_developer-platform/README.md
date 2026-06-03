# Developer Platform · ハンズオン

## 何を作るか
TechFlow（1日500件以上のチケットを処理するB2B SaaS企業）向けのマルチツール対応サポートチケットエージェントです。エージェントはチケットの詳細を読み取り、ナレッジベースを検索し、構造化された解決策を生成します。フレームワークを使わず、Claude APIを直接使用します。

## 主な学習内容
Claude APIを使ってツール呼び出しを含むエージェントループを構築する方法。ツールスキーマの定義、複数ステップのツール呼び出しの処理、そしてClaude Sonnet 4.6のアダプティブ思考を活用してモデルが複雑なチケットのトリアージを自動的に推論できるようにする方法を学びます。

---

## 実行方法

### オプション1 — GitHub Codespaces（ローカルインストール不要）

1. GitHub上のリポジトリにアクセスし、緑色の **Code** ボタンをクリックする。
2. **Codespaces** タブを選択し、**Create codespace on main** をクリックする。
3. 環境が読み込まれるまで待つ（約1分かかります）。
4. `day1/02_developer-platform/Developer_Platform.ipynb` を開く。
5. カーネルの選択を求められたら **Python 3** を選択する。
6. APIキーのセルに、引用符の間にキーを貼り付ける。
7. **Shift+Enter** でセルを実行するか、上部メニューの **Run All** を使用する。

---

### オプション2 — VS Code（ローカル）

1. VS Codeを開き、**ファイル → フォルダーを開く** でこのフォルダーを選択する。
2. 求められた場合は **Python** と **Jupyter** 拡張機能をインストールする（拡張機能パネルで「Jupyter」を検索）。
3. `Developer_Platform.ipynb` を開き、求められたらPython環境をカーネルとして選択する。
4. VS Codeでターミナルを開き（**ターミナル → 新しいターミナル**）、APIキーを設定する:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
5. **Shift+Enter** でセルを実行するか、ノートブック上部の **Run All** をクリックする。

---

### オプション3 — Jupyter（ローカル）

1. 必要に応じてJupyterをインストールする: `pip install notebook`
2. ターミナルを開き、このフォルダーに移動してAPIキーを設定する:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   cd path/to/day1/02_developer-platform
   jupyter notebook Developer_Platform.ipynb
   ```
3. 開いたブラウザタブで、**Shift+Enter** でセルを実行するか、**セル → すべて実行** を使用する。

# Evals · ビルド演習

## 作るもの
`boutique`（商品価格を調べて計算を行うシンプルな AI ショッピングアシスタント）向けの eval スイートです。エージェントはおおむね動いています。あなたの仕事は、どこで・なぜ壊れるかを正確に突き止め、体系的な eval 駆動のアプローチで修正することです。

## 主な学習内容
AI エージェント向け eval の構築方法：テストタスクの定義、grader の記述、ハーネスの実行、そして結果を使った的を絞った改善。「試して様子を見る」から、顧客にリリースする前に数値で示せる再現可能なフィードバックループへと移行します。

---

## 実行方法

### オプション 1 — GitHub Codespaces（ローカルインストール不要）

1. GitHub でリポジトリを開き、緑色の **Code** ボタンをクリックします。
2. **Codespaces** タブを選択し、**Create codespace on main** をクリックします。
3. 環境の読み込みを待ちます（約1分かかります）。
4. `day2/01_evals/Building_an_Eval.ipynb` を開きます。
5. カーネルの選択を求められたら **Python 3** を選択します。
6. API キーセルに、引用符の間にキーを貼り付けます。
7. **Shift+Enter** でセルを実行するか、上部メニューの **Run All** を使用します。

---

### オプション 2 — VS Code（ローカル）

1. VS Code を開き、**File → Open Folder** からこのフォルダを選択します。
2. 促されたら **Python** および **Jupyter** 拡張機能をインストールします（Extensions パネルで「Jupyter」を検索）。
3. `Building_an_Eval.ipynb` を開き、促されたら Python 環境をカーネルとして選択します。
4. VS Code でターミナルを開き（**Terminal → New Terminal**）、API キーを設定します：
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
5. **Shift+Enter** でセルを実行するか、ノートブック上部の **Run All** をクリックします。

---

### オプション 3 — Jupyter（ローカル）

1. 必要であれば Jupyter をインストールします：`pip install notebook`
2. ターミナルを開き、このフォルダに移動して API キーを設定します：
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   cd path/to/day2/01_evals
   jupyter notebook Building_an_Eval.ipynb
   ```
3. 開いたブラウザタブで、**Shift+Enter** でセルを実行するか、**Cell → Run All** を使用します。

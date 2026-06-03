# Prompt Rescue · Build-Along

## 何をするか
あなたは TechSupport Corp の技術コンサルタントとして呼ばれました。彼らはサポートチケットを処理する本番プロンプトを持っています — 優先度の分類、エンティティの抽出、回答のドラフト作成を行います。クリーンな入力ではうまく動作しますが、現実世界の雑然としたチケットではひどく失敗します。更新ミーティングは48時間後です。あなたの仕事: プロンプトを救済することです。

## 主な学習内容
壊れたプロンプトを体系的に診断して修正する方法。失敗ケースを調べ、根本原因（誤った優先度分類、幻覚エンティティ、壊れたJSON出力）を特定し、実世界のテストケースセットに対してスコアリングする組み込みの評価ハーネスを使いながら改善を繰り返します。

---

## 実行方法

### オプション1 — GitHub Codespaces（ローカルインストール不要）

1. GitHub でリポジトリに移動し、緑色の **Code** ボタンをクリックします。
2. **Codespaces** タブを選択し、**Create codespace on main** をクリックします。
3. 環境が読み込まれるまで待ちます（約1分かかります）。
4. `day1/03_prompt-rescue/Prompt_Rescue_solo.ipynb` を開きます。
5. カーネルの選択を求められたら、**Python 3** を選択します。
6. APIキーのセルで、引用符の間にキーを貼り付けます。
7. **Shift+Enter** でセルを実行するか、上部メニューの **Run All** を使用します。

---

### オプション2 — VS Code（ローカル）

1. VS Code を開き、**File → Open Folder** でこのフォルダーを選択します。
2. 求められたら **Python** と **Jupyter** 拡張機能をインストールします（拡張機能パネルで「Jupyter」を検索）。
3. `Prompt_Rescue_solo.ipynb` を開き、求められたらカーネルとして Python 環境を選択します。
4. VS Code でターミナルを開き（**Terminal → New Terminal**）、APIキーを設定します:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
5. **Shift+Enter** でセルを実行するか、ノートブック上部の **Run All** をクリックします。

---

### オプション3 — Jupyter（ローカル）

1. 必要に応じて Jupyter をインストールします: `pip install notebook`
2. ターミナルを開き、このフォルダーに移動してAPIキーを設定します:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   cd path/to/day1/03_prompt-rescue
   jupyter notebook Prompt_Rescue_solo.ipynb
   ```
3. 開いたブラウザタブで、**Shift+Enter** でセルを実行するか、**Cell → Run All** を使用します。

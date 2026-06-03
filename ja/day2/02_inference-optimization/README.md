# 推論最適化 · ハンズオン演習

## やること
本番環境で重要な主要指標を対象に、Claude モデルをベンチマークするハンズオン形式のラボです。最初のトークンまでの時間（TTFT）、完了までの時間（TTC）、1秒あたりの出力トークン数（OTPS）、そしてコストを計測します。続いて、プロンプトキャッシュとツール使用がそれらの数値にどう影響するかを探ります。

## 主な学習内容
実際のデプロイ向けに推論を計測・最適化する方法。Haiku・Sonnet・Opus の速度とコストを比較し、プロンプトキャッシュがレイテンシとコストに与える影響を確認し、エージェントループを計測して時間が実際どこで使われているかを把握します。

---

## 実行方法

### オプション 1 — GitHub Codespaces（ローカルインストール不要）

1. GitHub のリポジトリページを開き、緑色の **Code** ボタンをクリックする。
2. **Codespaces** タブを選択し、**Create codespace on main** をクリックする。
3. 環境の読み込みが完了するまで待つ（約1分）。
4. `day2/02_inference-optimization/Inference_Optimization.ipynb` を開く。
5. カーネル選択を求められたら **Python 3** を選択する。
6. API キーセルに自分のキーを引用符の間に貼り付ける。
7. **Shift+Enter** でセルを実行するか、上部メニューの **Run All** を使う。

---

### オプション 2 — VS Code（ローカル）

1. VS Code を開き、**File → Open Folder** からこのフォルダーを選択する。
2. 求められた場合は **Python** および **Jupyter** 拡張機能をインストールする（拡張機能パネルで "Jupyter" を検索）。
3. `Inference_Optimization.ipynb` を開き、求められたらカーネルとして Python 環境を選択する。
4. VS Code でターミナルを開き（**Terminal → New Terminal**）、API キーを設定する:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```
5. **Shift+Enter** でセルを実行するか、ノートブック上部の **Run All** をクリックする。

---

### オプション 3 — Jupyter（ローカル）

1. 必要であれば Jupyter をインストールする: `pip install notebook`
2. ターミナルを開き、このフォルダーに移動して API キーを設定する:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   cd path/to/day2/02_inference-optimization
   jupyter notebook Inference_Optimization.ipynb
   ```
3. ブラウザで開いたタブで **Shift+Enter** でセルを実行するか、**Cell → Run All** を使う。

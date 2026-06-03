# ── インストール & インポート ──
%pip install -q anthropic

import anthropic
import json
import time
import os
from IPython.display import display, Markdown

# ── APIキー設定 ──
# オプション1: Colabシークレット（推奨 — 左サイドバーの🔑アイコンをクリック）
try:
    from google.colab import userdata
    os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
    print("✅ ColabシークレットからAPIキーを読み込みました")
except Exception:
    pass

# オプション2: 直接貼り付け（コメントを外して置き換えてください）
# os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

client = anthropic.Anthropic(timeout=900.0)  # タイムアウトを延長: ストリーミング非使用時にmax_tokens>21333で必要
MODEL = "claude-sonnet-4-6"

# ── 事前チェック ──
errors = []
if not os.environ.get("ANTHROPIC_API_KEY"):
    errors.append("❌ ANTHROPIC_API_KEY が設定されていません。Colabシークレット（🔑サイドバー）を使用するか、上に貼り付けてください。")

sdk_version = anthropic.__version__
print(f"SDKバージョン: {sdk_version}")

if not errors:
    try:
        test = client.messages.create(
            model=MODEL, max_tokens=1024,
            messages=[{"role": "user", "content": "Reply with only: ready"}],
            thinking={"type": "adaptive"},
        )
        text = "".join(b.text for b in test.content if b.type == "text").strip()
        print(f"✅ モデル: {MODEL}")
        print(f"✅ API接続確認 — テストレスポンス: {text}")
    except anthropic.AuthenticationError:
        errors.append("❌ APIキーが無効です。キーを確認して再試行してください。")
    except anthropic.BadRequestError as e:
        errors.append(f"❌ APIエラー: {e}。SDKの更新が必要な場合があります: %pip install -q --upgrade anthropic")
    except Exception as e:
        errors.append(f"❌ 接続エラー: {e}")

if errors:
    print("\n⚠️  セットアップの問題が検出されました:")
    for err in errors:
        print(f"   {err}")
    print("\n上記の問題を修正してこのセルを再実行してください。")
else:
    print("\n🚀 構築を始めましょう!")

# ── サンプルチケットデータ ──

TICKETS = {
    "TKT-1042": {
        "id": "TKT-1042", "customer": "Acme Corp", "priority": "high",
        "product_area": "billing",
        "description": "We were charged twice for our March invoice. Invoice #INV-2024-0342 shows $4,500 but our bank shows two identical charges on March 3rd. Need immediate refund of the duplicate charge.",
        "status": "open"
    },
    "TKT-1043": {
        "id": "TKT-1043", "customer": "DataFlow Inc", "priority": "medium",
        "product_area": "api",
        "description": "Our webhook endpoint stopped receiving events after we rotated API keys yesterday. We've verified the new key works for REST calls but webhooks are still failing. Getting 401 errors in the webhook logs.",
        "status": "open"
    },
    "TKT-1044": {
        "id": "TKT-1044", "customer": "CloudScale Ltd", "priority": "low",
        "product_area": "feature_request",
        "description": "Would love to see bulk export functionality in the dashboard. Currently we have to export reports one at a time which is painful when we need quarterly summaries across 50+ projects.",
        "status": "open"
    },
    "TKT-1045": {
        "id": "TKT-1045", "customer": "SecureNet Systems", "priority": "critical",
        "product_area": "account",
        "description": "Our admin account (admin@securenet.io) is locked out after failed MFA attempts. We have 47 team members who can't access the platform because SSO is tied to this admin account. This is blocking all work.",
        "status": "open"
    },
    "TKT-1046": {
        "id": "TKT-1046", "customer": "MedTech Solutions", "priority": "high",
        "product_area": "api",
        "description": "Our production integration started returning intermittent 500 errors around 2am last night. About 15% of API calls are failing. We haven't changed anything on our end. Errors seem random - sometimes the same request works on retry. Our team in Singapore is blocked and we need this resolved ASAP.",
        "status": "open"
    },
}

KB_ARTICLES = {
    "KB-001": {"title": "Processing Duplicate Payment Refunds", "content": "For duplicate charges: 1) Verify the duplicate in the billing system, 2) Issue refund through the payment processor (takes 3-5 business days), 3) Send confirmation email with refund reference number. Escalate if amount exceeds $10,000."},
    "KB-002": {"title": "Webhook Authentication After Key Rotation", "content": "When API keys are rotated, webhook signing secrets must also be updated. Go to Settings > Webhooks > Edit endpoint, and regenerate the signing secret. The old secret is invalidated immediately on key rotation. Common mistake: rotating the API key but not the webhook signing secret."},
    "KB-003": {"title": "Bulk Export Feature (Roadmap)", "content": "Bulk export is on the Q3 roadmap. Workaround: Use the REST API's /reports/export endpoint with date range parameters to programmatically export multiple reports. See API docs for batch export examples."},
    "KB-004": {"title": "Admin Account Lockout Recovery", "content": "For locked admin accounts: 1) Verify identity through the secondary email on file, 2) Reset MFA through the admin recovery flow at /admin/recover, 3) Temporary access can be granted through support-level override (requires manager approval). Critical: If SSO is blocked, enable the bypass login at /login/direct for affected users."},
    "KB-005": {"title": "API Rate Limiting Best Practices", "content": "Default rate limits: 100 requests/minute for standard plans, 1000/minute for enterprise. Use exponential backoff with jitter for retries. Monitor usage via the X-RateLimit headers in responses."},
    "KB-006": {"title": "Invoice Discrepancy Resolution", "content": "For billing discrepancies: Check the billing audit log for the account, compare with payment processor records, and verify no pending transactions. Contact finance team for adjustments over $5,000."},
    "KB-007": {"title": "Intermittent 500 Errors Troubleshooting", "content": "For intermittent server errors: 1) Check the status page for known outages, 2) Review rate limit headers - 429s can masquerade as 500s behind load balancers, 3) Check if errors correlate with payload size or specific endpoints, 4) Enable request ID logging and contact support with specific request IDs for investigation. If >10% error rate persists for >1 hour, escalate to engineering."},
}

def get_ticket(ticket_id: str) -> str:
    ticket = TICKETS.get(ticket_id)
    if ticket:
        return json.dumps(ticket)
    return json.dumps({"error": f"Ticket {ticket_id} not found"})

def search_kb(query: str) -> str:
    query_lower = query.lower()
    results = []
    for article_id, article in KB_ARTICLES.items():
        if any(word in article["title"].lower() or word in article["content"].lower()
               for word in query_lower.split() if len(word) > 2):
            results.append({"id": article_id, **article})
    if not results:
        results = [{"id": "KB-000", "title": "No matches found", "content": "No relevant articles found. Consider escalating to Tier 2 support."}]
    return json.dumps(results[:3])

def resolve_ticket(ticket_id: str, resolution: str, status: str = "resolved") -> str:
    ticket = TICKETS.get(ticket_id)
    if ticket:
        ticket["status"] = status
        ticket["resolution"] = resolution
        return json.dumps({"success": True, "ticket_id": ticket_id, "new_status": status})
    return json.dumps({"error": f"Ticket {ticket_id} not found"})

TOOL_FUNCTIONS = {"get_ticket": get_ticket, "search_kb": search_kb, "resolve_ticket": resolve_ticket}

def execute_tool(name: str, input_data: dict) -> str:
    func = TOOL_FUNCTIONS.get(name)
    if func:
        return func(**input_data)
    return json.dumps({"error": f"Unknown tool: {name}"})

print("モックツールとサンプルデータを読み込みました!")
print(f"   利用可能なチケット: {', '.join(TICKETS.keys())}")
print(f"   ナレッジベース記事数: {len(KB_ARTICLES)}")

# TODO: get_ticket、search_kb、resolve_ticket のツールスキーマを定義する
# 各ツールに必要なもの: name（名前）、description（説明）、input_schema（propertiesとrequiredを含む）
# ヒント: resolve_ticket の status はenumにすること: ["resolved", "escalated", "pending_customer"]

tools = [
    # ここにツールスキーマを記述する
]

print(f"定義されたツールスキーマ数: {len(tools)}: {[t['name'] for t in tools]}")

SYSTEM_PROMPT = """あなたはTechFlowのTier 1サポートエージェントです。TechFlowはミドルマーケット企業向けにプロジェクト管理とチームコラボレーションツールを提供するB2B SaaSプラットフォームです。

## あなたの役割
受信したサポートチケットを調査し、ナレッジベースでソリューションを見つけ、具体的で実行可能なガイダンスとともにチケットを解決します。

## プロセス
1. まず必ず チケットを検索して全体のコンテキストを把握する
2. 関連するソリューションと手順をナレッジベースで検索する
3. 具体的な次のステップを含む詳細な解決策でチケットを解決する

## ガイドライン
- 徹底的に: 問題が単純に見えても、解決前に必ずKBを検索する
- 具体的に: 解決策には正確な手順、リンク、タイムフレームを含める
- 必要に応じてエスカレーション: 確信が低い場合や特権アクセスが必要な問題はエスカレーションとしてマークする
- 正確に分類: billing（請求）、technical（技術）、account（アカウント）、feature_request（機能要望）

## エスカレーション基準
- $10,000を超える金融問題
- セキュリティ関連のアカウント侵害
- エンジニアリングの介入が必要な問題
- Enterprise SLA（1時間以内の応答）の顧客

## TechFlowの製品プラン
- Starter ($29/ユーザー/月): 基本的なプロジェクト管理、5GBストレージ、メールサポート、最大5プロジェクト、コミュニティフォーラム
- Professional ($79/ユーザー/月): 高度なアナリティクス、100GBストレージ、優先サポート、APIアクセス、無制限プロジェクト、カスタムフィールド、ガントチャート、タイムトラッキング
- Enterprise (カスタム価格): SSO/SAML、無制限ストレージ、専任CSM、カスタムインテグレーション、SLA保証、監査ログ、高度なセキュリティ、カスタムブランディング、優先APIレート制限

## 一般的な問題カテゴリとルーティング
- Billing（請求）: 請求書の相違、支払い失敗、プラン変更、返金依頼、サブスクリプションのキャンセル、日割り計算の質問
- Technical（技術）: APIエラー、インテグレーションの問題、Webhookの障害、パフォーマンスの問題、データエクスポートの問題、ブラウザの互換性
- Account（アカウント）: ログインの問題、MFAの問題、SSO設定、権限の変更、チーム管理、ユーザープロビジョニング
- Feature Requests（機能要望）: 製品フィードバック、ロードマップの問い合わせ、回避策の依頼、ベータアクセスのリクエスト

## 応答テンプレート
請求の問題を解決する際は必ず含める: トランザクションID、返金タイムライン、確認メールの詳細。
技術的な問題を解決する際は必ず含める: 再現手順、利用可能な場合の回避策、エスカレーション時のエンジニアリングチケット番号。
アカウントの問題を解決する際は必ず含める: 実施したセキュリティ確認手順と付与した一時アクセス。

## SLA要件
- Starter: 24時間応答時間、営業時間のみ
- Professional: 4時間応答時間、拡張時間帯（午前6時〜午後10時）
- Enterprise: 1時間応答時間、24時間365日サポート、専用Slackチャンネル

## トーン
プロフェッショナルで、共感的で、ソリューション志向であること。解決策に入る前に顧客の不満を認める。利用可能な場合は顧客名を使用する。関連するガイダンスには特定の製品プランを参照する。"""


# TODO: run_agent(user_message) を実装する
# 1. ユーザーメッセージを含むメッセージリストを作成する
# 2. client.messages.create() を以下のパラメータで呼び出す:
#    - model=MODEL, max_tokens=32000, system=SYSTEM_PROMPT, tools=tools
#    - thinking={"type": "adaptive"}
#    - messages=messages
# 3. response.stop_reason == "tool_use" の間ループ:
#    a. response.content をループして tool_use ブロックを探す
#    b. execute_tool(block.name, block.input) で各ツールを実行する
#    c. tool_use_id とコンテンツを含む tool_result 辞書を構築する
#    d. アシスタントの応答 + ツール結果をメッセージに追加する
#       （思考ブロックを含む全コンテンツブロックを返すこと！）
#    e. APIを再度呼び出す
# 4. 最終的な応答を返す

def run_agent(user_message: str):
    """サポートチケットエージェントを実行する。"""
    pass  # ここに実装を記述する


# テスト実行!
# response = run_agent("Resolve ticket TKT-1042")
# for block in response.content:
#     if block.type == "text" and block.text.strip():
#         print(f"\n 最終応答:\n{block.text}")

# TODO: RESOLUTION_SCHEMA と run_agent_structured() を定義する
# 1. 以下を含む type json_schema で RESOLUTION_SCHEMA を定義する:
#    - diagnosis（文字列）、solution_steps（文字列の配列）、
#    - confidence（enum: high/medium/low）、escalation_needed（ブール値）、
#    - category（enum: billing/technical/account/feature_request）
# 2. run_agent をコピー — output_config.format なしでツールループを実行する
#    （formatは全テキスト出力を制約するため、ツールはそれと一緒に動作しない）
# 3. ツールループ終了後、最終呼び出しを以下で行う:
#    - output_config={"format": RESOLUTION_SCHEMA}
#    - tool_choice={"type": "none"}  （さらなるツール呼び出しを防ぐ）
#    - "構造化された解決策をJSONで提供してください。" のようなユーザーメッセージを追加する
# 4. 最終応答を get_structured_result() ヘルパーで解析する
# ヒント: thinking={"type": "adaptive"} は各呼び出しでアダプティブ思考を有効にする

RESOLUTION_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "diagnosis": {"type": "string", "description": "Root cause analysis of the issue"},
            "solution_steps": {"type": "array", "items": {"type": "string"}, "description": "Ordered steps to resolve"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "escalation_needed": {"type": "boolean"},
            "category": {"type": "string", "enum": ["billing", "technical", "account", "feature_request"]}
        },
        "required": ["diagnosis", "solution_steps", "confidence", "escalation_needed", "category"],
        "additionalProperties": False
    }
}


def get_structured_result(response) -> dict:
    """応答の最後のテキストブロックから構造化JSONを抽出する。"""
    # アダプティブ思考では、コンテンツが [thinking, text] になる場合がある — JSONは最後のテキストブロックにある
    text_blocks = [b for b in response.content if b.type == "text" and b.text.strip()]
    if text_blocks:
        return json.loads(text_blocks[-1].text)
    return None


def run_agent_structured(user_message: str) -> dict:
    """構造化JSON出力でエージェントを実行する。"""
    pass  # ここに実装を記述する


# result = run_agent_structured("Resolve ticket TKT-1042")
# print(json.dumps(result, indent=2))

# TODO: エージェントにエフォートレベルの思考制御を追加する
# 1. run_agent をコピー — thinking={"type": "adaptive"} と
#    output_config={"effort": effort} でツールループを実行する（format は含めない — 最終呼び出しまで取っておく）
# 2. ループ内で思考ブロックを表示する: block.type == "thinking"
# 3. ツールループ終了後、最終呼び出しを以下で行う:
#    - output_config={"effort": effort, "format": RESOLUTION_SCHEMA}
#    - tool_choice={"type": "none"}
#    - "構造化された解決策をJSONで提供してください。" のようなユーザーメッセージを追加する
# 4. get_structured_result() を使って最終応答を解析する

def run_agent_thinking(user_message: str, effort: str = "high") -> dict:
    """エフォート制御されたアダプティブ思考でエージェントを実行する。"""
    pass  # ここに実装を記述する

# 高エフォートで曖昧なチケットを実行 — 思考トレースを観察する
print("=== TKT-1046: 断続的なAPIエラー（曖昧なケース） ===\n")
result = run_agent_thinking("Resolve ticket TKT-1046", effort="high")
print(f"\n解決策:")
print(json.dumps(result, indent=2))

# 比較: 同じチケット、低エフォート
print(f"\n\n{'='*50}")
print("=== 同じチケット、低エフォート ===")
print(f"{'='*50}\n")

for effort in ["high", "low"]:
    start = time.time()
    result = run_agent_thinking("Resolve ticket TKT-1046", effort=effort)
    elapsed = time.time() - start
    print(f"\n[effort={effort}] 確信度: {result['confidence']} | ステップ数: {len(result['solution_steps'])} | エスカレーション: {result['escalation_needed']} | 時間: {elapsed:.1f}s")

# TODO: ストリーミングエージェントループを構築する
# 1. create() をコンテキストマネージャーを使った stream() に置き換える (with ... as stream:)
#    ツールループ中は output_config={"effort": effort} を使用する（format制約なし）
# 2. ストリームイベントを反復処理し、以下を処理する:
#    - content_block_start: content_block.type を確認する（thinking/tool_use/text）
#    - content_block_delta: thinking_delta、text_delta、input_json_delta を処理する
# 3. ストリーミング後、完全な応答を取得するために stream.get_final_message() を使用する
# 4. stop_reason が tool_use の場合、ツールを実行してループを継続する
# 5. ツールループ終了後、最終ストリーミング呼び出しを以下で行う:
#    - output_config={"effort": effort, "format": RESOLUTION_SCHEMA}
#    - tool_choice={"type": "none"}
# 6. 最終JSONに get_structured_result() を使用する
# 注意: stream() に thinking={"type": "adaptive"} を渡すこと

def run_agent_streaming(user_message: str, effort: str = "high") -> dict:
    """ストリーミング出力でエージェントを実行する。"""
    pass  # ここに実装を記述する

print("フルエージェントデモ: TKT-1045（アカウントロックアウト）の解決")
print("   ストリーミング + アダプティブ思考 + ツール + 構造化出力")
print("=" * 60)

start = time.time()
result = run_agent_streaming("Resolve ticket TKT-1045")
elapsed = time.time() - start

print(f"\n\n{'=' * 60}")
print(f"合計時間: {elapsed:.1f}s")
print(f"\n構造化された解決策:")
print(json.dumps(result, indent=2))

!pip install -q anthropic

import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-... "

import math
from anthropic import Anthropic
from anthropic.types import ToolUseBlock, TextBlock

# ── 設定 ──────────────────────────────────────────────────────────────────────

MODEL = "claude-haiku-4-5-20251001"
SYSTEM_PROMPT = "You are a helpful assistant."

client = Anthropic()

# ── ツール実装 ─────────────────────────────────────────────────────────────────

def get_product(product: str):
    catalog = {
        "jeans": 49.99,
        "shirt": 29.99,
        "dress": 59.99,
        "jacket": 89.99,
        "sneakers": 74.99,
        "hat": 19.99,
        "socks": 9.99,
        "hoodie": 44.99,
        "shorts": 34.99,
        "t-shirt": 24.99,
        "sweater": 54.99,
        "belt": 24.99,
    }
    return catalog[product]


def calculate(op: str, input1: float, input2: float):
    match op:
        case "+": return input1 + input2
        case "-": return input1 - input2
        case "*": return input1 * input2
        case "/": return input1 / input2
        case "**": return input1 ** input2

TOOL_REGISTRY = {
    "get_product": get_product,
    "calculate": calculate,
}

# ── ツール仕様（Claude に送信する内容）──────────────────────────────────────────

GET_PRODUCT_SPEC = {
    "name": "get_product",
    "description": "get_product",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {
                "type": "string",
                "description": "product",
            },
        },
        "required": ["product"],
    },
}

CALCULATE_SPEC = {
    "name": "calculate",
    "description": "calculator",
    "input_schema": {
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "operator",
            },
            "input1": {
                "type": "number",
                "description": "input1",
            },
            "input2": {
                "type": "number",
                "description": "input2",
            },
        },
        "required": ["op", "input1", "input2"],
    },
}

ALL_TOOL_SPECS = [GET_PRODUCT_SPEC, CALCULATE_SPEC]

# ── エージェント ───────────────────────────────────────────────────────────────

def call_claude(messages, tools, model=None):
    return client.messages.create(
        model=model or MODEL,
        system=SYSTEM_PROMPT,
        max_tokens = 1024,
        tools=tools,
        messages=messages,
    )


def execute_tool(name, inputs):
    try:
        return str(TOOL_REGISTRY[name](**inputs))
    except Exception as e:
        return f"Error: {e}"


def run_agent(prompt, eval_mode=False, model=None):
    messages = [{"role": "user", "content": prompt}]
    total_input_tokens = 0
    total_output_tokens = 0

    while True:
        response = call_claude(messages, tools=ALL_TOOL_SPECS, model=model)
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        tool_calls = [block for block in response.content if isinstance(block, ToolUseBlock)]

        tool_results = []
        for tool_call in tool_calls:
            result = execute_tool(tool_call.name, tool_call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    if eval_mode:
        return {
            "messages": messages,
            "usage": {"input_tokens": total_input_tokens, "output_tokens": total_output_tokens},
        }

    return "\n".join(block.text for block in response.content if isinstance(block, TextBlock))


print("boutique agent ready.")

while True:
    query = input("\nYou: ")
    if not query.strip() or query.strip().lower() in ("quit", "exit", "q"):
        print("セッションを終了します。")
        break
    print(f"\nBoutique: {run_agent(query)}")

# ── Grader（このセルをそのまま実行する）──────────────────────────────────────────

import re

def grade_response_contains(result, check, context=None):
    text = result["final_text"].lower()
    target = check.lower()
    if target in text:
        return {"score": 1.0, "reason": f"レスポンスに '{check}' が見つかりました"}
    return {"score": 0.0, "reason": f"レスポンスに '{check}' が見つかりません: {result['final_text'][:200]}"}


def grade_response_numeric(result, check, context=None):
    if isinstance(check, (int, float)):
        value, tolerance = float(check), 0.01
    else:
        value = float(check["value"])
        tolerance = float(check.get("tolerance", 0.01))

    numbers = re.findall(r"-?[\d,]+\.?\d*", result["final_text"])
    for num_str in numbers:
        try:
            num = float(num_str.replace(",", ""))
            if abs(num - value) <= tolerance:
                return {"score": 1.0, "reason": f"{num} が見つかりました（期待値: {value} +/- {tolerance}）"}
        except ValueError:
            continue
    return {"score": 0.0, "reason": f"期待値 {value}（+/- {tolerance}）、実際の数値: {numbers[:10]}"}


def grade_tool_use(result, check, context=None):
    tool_name = check["tool_name"]
    expected_args = check.get("arguments", None)

    for call in result["tool_calls"]:
        if call["name"] != tool_name:
            continue
        if expected_args is None:
            return {"score": 1.0, "reason": f"ツール '{tool_name}' が呼び出されました"}

        # 部分一致: 指定されたキーのみ確認する
        actual_args = call.get("arguments", {})
        match = all(
            (isinstance(v, str) and isinstance(actual_args.get(k), str) and v.lower() == actual_args[k].lower())
            or actual_args.get(k) == v
            for k, v in expected_args.items()
        )
        if match:
            return {"score": 1.0, "reason": f"ツール '{tool_name}' が一致する引数で呼び出されました: {expected_args}"}

    actual = [{"name": c["name"], "args": c.get("arguments", {})} for c in result["tool_calls"]]
    if expected_args:
        return {"score": 0.0, "reason": f"'{tool_name}' が {expected_args} で呼び出されませんでした。実際: {actual}"}
    return {"score": 0.0, "reason": f"'{tool_name}' は一度も呼び出されませんでした。実際: {[c['name'] for c in result['tool_calls']]}"}


GRADER_REGISTRY = {
    "response_contains": grade_response_contains,
    "response_numeric": grade_response_numeric,
    "tool_use": grade_tool_use,
}

print(f"Grader が読み込まれました: {list(GRADER_REGISTRY.keys())}")

# ── Eval ランナー（このセルをそのまま実行する）────────────────────────────────────

import json, os, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_transcript(messages):
    """エージェントのトランスクリプトから final_text と tool_calls を抽出する。"""
    final_text, tool_calls = "", []
    for msg in messages:
        if msg["role"] != "assistant":
            continue
        for block in msg["content"]:
            if isinstance(block, TextBlock):
                final_text = block.text
            elif isinstance(block, ToolUseBlock):
                tool_calls.append({"name": block.name, "arguments": block.input, "id": block.id})
    # ツール結果を呼び出しに紐付ける
    for msg in messages:
        if msg["role"] != "user" or not isinstance(msg["content"], list):
            continue
        for item in msg["content"]:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                for call in tool_calls:
                    if call["id"] == item["tool_use_id"]:
                        call["result"] = item.get("content", "")
                        break
    return {"final_text": final_text, "tool_calls": tool_calls, "messages": messages}


def run_single_task(agent_fn, task, model=None):
    """1 タスクを実行し、grader を適用して、グレードとメトリクスを含む結果を返す。"""
    start = time.time()
    try:
        raw = agent_fn(task["query"], eval_mode=True, model=model)
    except Exception:
        return {
            "task_id": task["id"], "task_description": task.get("description", ""),
            "query": task["query"], "category": task.get("category", ""),
            "error": traceback.format_exc(), "passed": False, "grades": [],
            "metrics": {"time": time.time() - start},
        }

    elapsed = time.time() - start
    result = parse_transcript(raw["messages"])
    usage = raw.get("usage", {})
    turns = sum(1 for m in raw["messages"] if m["role"] == "assistant")
    metrics = {
        "time": round(elapsed, 3), "tool_calls": len(result["tool_calls"]),
        "turns": turns, "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }

    grades = []
    context = {"query": task["query"], "task_id": task["id"], "model": model}
    for grader in task.get("graders", []):
        grader_fn = GRADER_REGISTRY.get(grader["type"])
        if grader_fn is None:
            grades.append({"type": grader["type"], "check": None, "score": 0.0, "reason": f"不明な grader: {grader['type']}"})
            continue
        for check in grader.get("checks", []):
            grade = grader_fn(result, check, context)
            grades.append({"type": grader["type"], "check": check, "score": grade["score"], "reason": grade["reason"]})

    passed = all(g["score"] == 1.0 for g in grades) if grades else False

    return {
        "task_id": task["id"], "task_description": task.get("description", ""),
        "query": task["query"], "category": task.get("category", ""),
        "passed": passed, "grades": grades, "metrics": metrics,
        "final_text": result["final_text"],
        "transcript": [
            block.model_dump() if hasattr(block, "model_dump") else block
            for msg in raw["messages"]
            for block in (msg["content"] if isinstance(msg["content"], list) else [msg["content"]])
        ],
    }


def run_eval(agent_fn, tasks, model=None, num_runs=1, max_workers=5):
    """eval スイート全体を実行する。構造化された結果を返す。"""
    all_runs = []
    for _ in range(num_runs):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(run_single_task, agent_fn, t, model): t for t in tasks}
            run_results = [f.result() for f in as_completed(futures)]
        task_order = {t["id"]: i for i, t in enumerate(tasks)}
        run_results.sort(key=lambda r: task_order.get(r["task_id"], 999))
        all_runs.append(run_results)
    return {"runs": all_runs, "config": {"model": model, "num_runs": num_runs, "num_tasks": len(tasks)}}


def save_results(results, directory="eval_results"):
    """eval 結果を JSON ファイルに保存する。"""
    os.makedirs(directory, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    model_name = results["config"].get("model") or "default"
    model_short = model_name.split("-")[1] if "-" in str(model_name) else model_name
    filename = f"{directory}/eval_{model_short}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"結果を保存しました: {filename}")
    return filename


def print_summary(results):
    """eval 結果をフォーマットして出力する。"""
    config = results["config"]
    print(f"{'=' * 60}")
    print(f"EVAL 結果: {config['num_tasks']} タスク, {config['num_runs']} 実行")
    if config.get("model"): print(f"モデル: {config['model']}")
    print(f"{'=' * 60}\n")

    for run_idx, run in enumerate(results["runs"]):
        if config["num_runs"] > 1: print(f"--- 実行 {run_idx + 1} ---")
        passed = sum(1 for r in run if r["passed"])
        total = len(run)
        print(f"総合: {passed}/{total} 合格 ({passed/total*100:.0f}%)\n")

        # カテゴリ別の内訳
        categories = {}
        for r in run:
            cat = r.get("category", "uncategorized")
            categories.setdefault(cat, {"passed": 0, "total": 0})
            categories[cat]["total"] += 1
            if r["passed"]: categories[cat]["passed"] += 1
        if len(categories) > 1:
            print("カテゴリ別:")
            for cat, c in sorted(categories.items()):
                print(f"  {cat}: {c['passed']}/{c['total']} ({c['passed']/c['total']*100:.0f}%)")
            print()

        # タスク詳細
        print("タスク:")
        for r in run:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"  [{mark}] {r['task_id']}: {r['task_description']}")
            for g in r.get("grades", []):
                print(f"    {'+' if g['score'] == 1.0 else '-'} {g['type']}: {g['reason'][:120]}")
            if r.get("error"): print(f"    エラー: {r['error'][:200]}")

        # 集計メトリクス
        ok = [r for r in run if not r.get("error")]
        if ok:
            print(f"\nメトリクス（平均）: {sum(r['metrics']['time'] for r in ok)/len(ok):.2f}秒, "
                  f"{sum(r['metrics']['tool_calls'] for r in ok)/len(ok):.1f} ツール呼び出し, "
                  f"{sum(r['metrics']['turns'] for r in ok)/len(ok):.1f} ターン")
            print(f"トークン: {sum(r['metrics']['input_tokens'] for r in ok):,} 入力, "
                  f"{sum(r['metrics']['output_tokens'] for r in ok):,} 出力")
        print()


def inspect_task(results, task_id, run_index=0):
    """特定タスクの詳細結果（トランスクリプトを含む）を出力する。"""
    run = results["runs"][run_index]
    r = next((r for r in run if r["task_id"] == task_id), None)
    if r is None:
        print(f"タスク '{task_id}' が見つかりません"); return

    print(f"[{'PASS' if r['passed'] else 'FAIL'}] {r['task_id']}: {r['task_description']}")
    print(f"クエリ: {r['query']}")
    print(f"レスポンス: {r.get('final_text', 'N/A')}\n")
    if r.get("error"): print(f"エラー:\n{r['error']}"); return

    print("グレード:")
    for g in r["grades"]:
        print(f"  {'+' if g['score'] == 1.0 else '-'} {g['type']}: {g['reason']}")
    print(f"\nメトリクス: {r['metrics']}")

    print("\nトランスクリプト:")
    for item in r.get("transcript", []):
        if isinstance(item, dict):
            t = item.get("type", "?")
            if t == "text": print(f"  [text] {item.get('text', '')[:300]}")
            elif t == "tool_use": print(f"  [tool_use] {item.get('name', '?')}({item.get('input', {})})")
            elif t == "tool_result": print(f"  [tool_result] {str(item.get('content', ''))[:200]}")
            else: print(f"  [{t}] {str(item)[:200]}")
        else: print(f"  {str(item)[:200]}")


print("Eval フレームワークの準備が完了しました。")

tasks = [
    # ── リファレンスタスク ───────────────────────────────────────────────────────
    {
        "id": "price_jeans",
        "description": "Direct price lookup for jeans",
        "query": "How much do jeans cost?",
        "category": "product_lookup",
        "graders": [
            {"type": "response_contains", "checks": ["49.99"]},
            {"type": "tool_use", "checks": [{"tool_name": "get_product", "arguments": {"product": "jeans"}}]},
        ],
    },

    # ── 以下のクエリ用にタスクを作成する ──────────────────────────────────────

    # 1. "Price of a t-shirt?"

    # 2. "How much for shoes?"

    # 3. "3 shirts and 2 belts, what's my total?"

    # 4. "What's 20% off a jacket?"

    # 5. "What do you sell?"

]

results = run_eval(run_agent, tasks)
print_summary(results)
save_results(results)

# 検査したいタスク ID に置き換える
inspect_task(results, "price_jeans")

baseline = run_eval(run_agent, tasks, num_runs=5)
print_summary(baseline)

# LLM-as-judge grader を実装する

def grade_llm_judge(result, check, context=None):
    # TODO: この grader を実装する
    #
    # ステップ 1: judge プロンプトを作成する
    #   - 含める内容: context["query"]、result["final_text"]、評価基準（check）
    #   - judge に対して、1行目に PASS または FAIL、次の行に理由を答えるよう指示する
    #
    # ステップ 2: Claude を呼び出す
    #   - response = client.messages.create(model="claude-haiku-4-5-20241022", ...)
    #
    # ステップ 3: レスポンスを解析する
    #   - 1行目に "PASS" または "FAIL" が含まれているか確認する
    #   - {"score": 1.0, "reason": "..."} または {"score": 0.0, "reason": "..."} を返す
    pass


# ランナーが使用できるよう登録する
GRADER_REGISTRY["llm_judge"] = grade_llm_judge

# LLM-as-judge grader を使うタスクを追加する

llm_judge_tasks = [
    # {
    #     "id": "capabilities",
    #     "description": "Agent describes its capabilities",
    #     "query": "What can you help me with?",
    #     "category": "capabilities",
    #     "graders": [
    #         {"type": "llm_judge", "checks": [
    #             "Response mentions the ability to look up product prices",
    #             "Response mentions the ability to perform calculations",
    #         ]},
    #     ],
    # },
]

# 両方のタスクセットで eval を実行する
# all_tasks = tasks + llm_judge_tasks
# results = run_eval(run_agent, all_tasks)
# print_summary(results)

# ── ファシリテーター参照: タスク（パート 3）────────────────────────────────────
# パート 3 の 5 つのクエリすべてのリファレンスタスクと、LLM-as-judge タスク 1 件。

reference_tasks = [
    # ── 1. 直接検索（作業例として提供）───────────────────────────────────────
    {
        "id": "price_jeans",
        "description": "Direct price lookup for jeans",
        "query": "How much do jeans cost?",
        "category": "product_lookup",
        "graders": [
            {"type": "response_contains", "checks": ["49.99"]},
            {"type": "tool_use", "checks": [{"tool_name": "get_product", "arguments": {"product": "jeans"}}]},
        ],
    },

    # ── 2. ハイフンのエッジケース ─────────────────────────────────────────────
    # カタログには "t-shirt" がハイフン付きキーで登録されている。エージェントが
    # "t-shirt"（正解）を渡すか、"tshirt" / "t shirt"（KeyError）を渡すかが問われる。
    # 不十分なツール仕様では、エージェントは正確なフォーマットを知るすべがない。
    # arguments 付きの tool_use チェックでエージェントがキーを正しく取得したか検証する。
    {
        "id": "price_tshirt",
        "description": "Price lookup with hyphenated product name",
        "query": "Price of a t-shirt?",
        "category": "product_lookup",
        "graders": [
            {"type": "response_contains", "checks": ["24.99"]},
            {"type": "tool_use", "checks": [{"tool_name": "get_product", "arguments": {"product": "t-shirt"}}]},
        ],
    },

    # ── 3. 同義語 / カタログ外 ───────────────────────────────────────────────
    # "shoes" はカタログにない。"sneakers" はある（74.99）。このタスクは改善前の
    # エージェントでは FAIL になるよう設計されている。2 つの有効な採点アプローチ:
    #
    # Option A（改善前）: ツールが呼ばれたことだけ確認する。エージェントは KeyError を
    #   受け取るが、価格をハルシネーションせずに少なくともツールを使ったかを検証する。
    #
    # Option B（改善後）: ツール仕様を改善して有効な商品を列挙した後、エージェントが
    #   代替として "sneakers" を提案するかを確認する。
    #
    {
        "id": "price_shoes_synonym",
        "description": "Synonym query: 'shoes' is not in catalog ('sneakers' is)",
        "query": "How much for shoes?",
        "category": "product_lookup",
        "graders": [
            {"type": "tool_use", "checks": [{"tool_name": "get_product"}]},
            {"type": "response_contains", "checks": ["sneakers"]},
        ],
    },

    # ── 4. マルチツール: 検索 + 計算 ─────────────────────────────────────────
    # shirt = 29.99, belt = 24.99
    # 3 * 29.99 = 89.97, 2 * 24.99 = 49.98, 合計 = 139.95
    #
    # 数値結果と、ツールが使われたことを両方チェックする（もちろん改善の余地はある）
    {
        "id": "total_shirts_belts",
        "description": "Multi-item total requiring product lookups + calculation",
        "query": "3 shirts and 2 belts, what's my total?",
        "category": "multi_tool",
        "graders": [
            {"type": "response_numeric", "checks": [{"value": 139.95, "tolerance": 0.10}]},
            {"type": "tool_use", "checks": [
                {"tool_name": "get_product"},
                {"tool_name": "calculate", "arguments": {"op": "*"}},
                {"tool_name": "calculate", "arguments": {"op": "+"}},
            ]},
        ],
    },

    # ── 5. 計算: パーセント割引 ──────────────────────────────────────────────
    # jacket = 89.99, 20% off = 89.99 * 0.80 = 71.992
    #
    # エージェントは "20% off" を次のどちらかで解釈する可能性がある:
    #   - 割引後価格: 71.99（ほとんどのユーザーが意図する値）
    #   - 割引額: 18.00
    # 割引後価格をチェックする。tolerance は丸め誤差を吸収する
    # （71.99 vs 71.992 vs 72.00）。
    {
        "id": "discount_jacket",
        "description": "Calculate 20% off a jacket (lookup + percentage math)",
        "query": "What's 20% off a jacket?",
        "category": "calculation",
        "graders": [
            {"type": "response_numeric", "checks": [{"value": 71.99, "tolerance": 0.10}]},
            {"type": "tool_use", "checks": [
                {"tool_name": "get_product"},
                {"tool_name": "calculate"},
            ]},
        ],
    },

    # ── 6. オープンエンド（LLM-as-judge が必要）──────────────────────────────
    # 決定論的なチェックでは採点できない。カタログの説明方法は多数ある。
    # 各評価基準が独立した LLM judge 呼び出しを受けるよう、2 つの基準に分割している。
    {
        "id": "what_do_you_sell",
        "description": "Open-ended: agent describes available products",
        "query": "What do you sell?",
        "category": "capabilities",
        "graders": [
            {"type": "llm_judge", "checks": [
                "Response describes or lists some of the available products in the catalog",
                "Response is helpful and relevant to a shopping context (not dismissive or off-topic)",
            ]},
        ],
    },
]

print(f"リファレンスタスクを読み込みました: {len(reference_tasks)} タスク")
for t in reference_tasks:
    grader_types = [g["type"] for g in t["graders"]]
    print(f"  {t['id']:25s} [{t['category']}] grader: {grader_types}")

# ── ファシリテーター参照: LLM-as-Judge Grader（パート 6）──────────────────────

JUDGE_SYSTEM_PROMPT = """You are an eval grader. You will receive:
- The original user query
- An AI agent's response to that query
- A criterion to evaluate

Judge whether the agent's response meets the criterion. Focus only on the
specific criterion provided, not on overall response quality.

Respond with exactly one of these on the first line:
PASS - if the criterion is clearly met
FAIL - if the criterion is not met or only partially met

Then on the next line, give a brief reason (one sentence)."""


def grade_llm_judge(result, check, context=None):
    query = context["query"] if context else "Unknown query"
    response_text = result["final_text"]

    judge_prompt = f"""Original query: {query}

Agent's response: {response_text}

Criterion: {check}"""

    try:
        judge_response = client.messages.create(
            model="claude-haiku-4-5-20241022",
            max_tokens=150,
            temperature=0.0,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": judge_prompt}],
        )
        judge_text = judge_response.content[0].text.strip()
        first_line = judge_text.split("\n")[0].strip().upper()
        reason = judge_text.split("\n", 1)[1].strip() if "\n" in judge_text else judge_text

        if "PASS" in first_line:
            return {"score": 1.0, "reason": f"LLM judge: {reason}"}
        elif "FAIL" in first_line:
            return {"score": 0.0, "reason": f"LLM judge: {reason}"}
        else:
            return {"score": 0.0, "reason": f"LLM judge が解析不能なレスポンスを返しました: {judge_text[:200]}"}

    except Exception as e:
        return {"score": 0.0, "reason": f"LLM judge エラー: {e}"}


# 登録する
GRADER_REGISTRY["llm_judge"] = grade_llm_judge
print(f"利用可能な grader: {list(GRADER_REGISTRY.keys())}")

# ── ファシリテーター参照: 改善済みエージェント（パート 5）───────────────────────
# この eval では、以下の 3 つの変更でエージェントの合格率を ~50% から ~100% に引き上げられるはず。
# eval の失敗を通じて受講者が自分で発見するよう誘導する。選択的に提示すること。

# ── 修正 1: より良いシステムプロンプト ─────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are Boutique, a shopping assistant. You help customers find products, "
    "check prices, and calculate totals. Always use your tools to look up prices "
    "rather than guessing. If a product isn't found, suggest similar items from "
    "the catalog. Never do mental math, always use your calculate tool for any calculations."
)

# ── 修正 2: より良いツール仕様 ───────────────────────────────────────────────
# 元の仕様は "get_product" と "product" とだけ記載されており、コンテキストがない。
# Claude はどんな商品があるか、フォーマット、エラー時の挙動を知るすべがない。
# これらの仕様でその問題を修正する。

GET_PRODUCT_SPEC = {
    "name": "get_product",
    "description": "Look up the price of a product from the store catalog. Returns the price as a number. Raises a KeyError if the product is not found.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {
                "type": "string",
                "description": "Product name, lowercase. Available products: jeans, shirt, dress, jacket, sneakers, hat, socks, hoodie, shorts, t-shirt, sweater, belt",
            },
        },
        "required": ["product"],
    },
}

CALCULATE_SPEC = {
    "name": "calculate",
    "description": "Perform a math operation on two numbers. Use this for any arithmetic instead of doing mental math.",
    "input_schema": {
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "The math operator to apply.",
                "enum": ["+", "-", "*", "/", "**"],
            },
            "input1": {
                "type": "number",
                "description": "The first operand.",
            },
            "input2": {
                "type": "number",
                "description": "The second operand.",
            },
        },
        "required": ["op", "input1", "input2"],
    },
}

ALL_TOOL_SPECS = [GET_PRODUCT_SPEC, CALCULATE_SPEC]

# ── 修正 3: ツール実装のエラーハンドリング改善 ───────────────────────────────────
# 元の get_product は catalog[product] を直接実行するため生の KeyError が発生する。
# このバージョンは代わりに役立つメッセージを返す。

def get_product(product: str):
    catalog = {
        "jeans": 49.99, "shirt": 29.99, "dress": 59.99, "jacket": 89.99,
        "sneakers": 74.99, "hat": 19.99, "socks": 9.99, "hoodie": 44.99,
        "shorts": 34.99, "t-shirt": 24.99, "sweater": 54.99, "belt": 24.99,
    }
    if product in catalog:
        return catalog[product]
    available = ", ".join(sorted(catalog.keys()))
    return f"Product '{product}' not found. Available products: {available}"

TOOL_REGISTRY["get_product"] = get_product

print("改善済みエージェントを読み込みました。eval を再実行して違いを確認してください。")

# ── リファレンスタスクで eval 全体を実行する ────────────────────────────────────
# results = run_eval(run_agent, reference_tasks)
# print_summary(results)
# save_results(results)

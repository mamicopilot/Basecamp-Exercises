%%capture
!pip install anthropic
!pip install claude-agent-sdk
import importlib
import tabulate
from dotenv import load_dotenv
import os

api_key = ""  # <-- ここに API キーを貼り付けてください

import anthropic

# Anthropic クライアントを初期化する
client = anthropic.Anthropic(api_key=api_key)

# ベンチマーク対象のモデル
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_OPUS = "claude-opus-4-7"

# 演習で使用するデフォルトモデル
DEFAULT_MODEL = MODEL_SONNET

# ヘルスチェック: 簡単な API 呼び出しを実行する
try:
    response = client.messages.create(model=DEFAULT_MODEL, max_tokens=5, messages=[{"role": "user", "content":"Ping"}])
    #TODO Claude Messages API の基本呼び出しでヘルスチェック
    print(f"Health check passed: {response.content[0].text}")
    print(f"Using model: {DEFAULT_MODEL}")
except anthropic.APIError as e:
    print(f"Health check failed: {e}")
    raise

from dataclasses import dataclass, field
from typing import List, Optional
from tabulate import tabulate
import statistics

@dataclass
class BenchmarkResult:
    """1回の API 呼び出しに対するタイミング・トークン・コスト。"""
    ttft: float                    # 最初のトークンまでの時間（秒）
    total_time: float              # 完了までの時間 / TTC（秒）
    tokens_per_second: float       # レガシー: output_tokens / ttc
    input_tokens: int
    output_tokens: int
    endpoint: str
    model: str
    test_name: str
    otps: Optional[float] = None   # 1秒あたりの出力トークン数
    cost: Optional[float] = None   # コスト（ドル）
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None


@dataclass
class BenchmarkSuite:
    """複数回の実行結果を収集する。"""
    results: List[BenchmarkResult] = field(default_factory=list)

    def add_result(self, result: BenchmarkResult):
        self.results.append(result)

    def clear(self):
        self.results = []

    def summary(self, group_by: str = "test_name") -> str:
        if not self.results:
            return "No results."

        groups = {}
        for r in self.results:
            key = getattr(r, group_by)
            if key not in groups:
                groups[key] = []
            groups[key].append(r)

        rows = []
        for name, group in groups.items():
            ttfts = [r.ttft * 1000 for r in group]
            ttcs = [r.total_time * 1000 for r in group]
            throughputs = [r.otps or r.tokens_per_second for r in group]
            costs = [r.cost for r in group if r.cost is not None]

            row = [
                name,
                len(group),
                f"{statistics.mean(ttfts):.0f}",
                f"{statistics.mean(ttcs):.0f}",
                f"{statistics.mean(throughputs):.1f}",
            ]
            if costs:
                row.append(f"${sum(costs)*1000:.4f}")  # 1000回呼び出しあたりのコスト
            rows.append(row)

        headers = ["Test", "Runs", "TTFT(ms)", "TTC(ms)", "OTPS"]
        if any(r.cost for r in self.results):
            headers.append("$/1K calls")
        return tabulate(rows, headers=headers, tablefmt="grid")


suite = BenchmarkSuite()
print("✓ BenchmarkSuite ready (with cost tracking)")

import time

def _stream_request(prompt, model=DEFAULT_MODEL, max_tokens=256):
    """低レベルヘルパー: リクエストをストリーミングし、生タイミングとレスポンスを返す。"""
    ttft = None
    start_time = time.perf_counter()
    with client.messages.stream(
        model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}]
    ) as stream:
        # イベントをループ — "content_block_start" を検出したら TTFT を記録する。
        for event in stream:
            if ttft is None and event.type == "content_block_start":
                ttft = time.perf_counter() - start_time
        # ループ後、stream.get_final_message() を呼んでレスポンスを取得する。
        response = stream.get_final_message()

    total_time = time.perf_counter() - start_time
    return ttft, total_time, response

print("✓ _stream_request helper ready")

ttft, total_time, response = _stream_request("What is 2 + 2? Answer in one word.")

ttft_ms = ttft * 1000
ttc_ms = total_time * 1000

print(f"Response: {response.content[0].text}")
print(f"TTFT: {ttft_ms:.0f}ms")
print(f"TTC:  {ttc_ms:.0f}ms")

def compute_otps(ttft, total_time, output_tokens):
    # TODO: OTPS と生成時間を計算し、両方を返す
    pass

ttft, total_time, response = _stream_request("What is 2 + 2? Answer in one word.")

tokens = 0  # TODO: レスポンスの usage から出力トークン数を取得する
otps, gen_time = 0, 0  # TODO: compute_otps を使って OTPS と生成時間を計算する

print(f"Response: {response.content[0].text}")
print(f"TTFT: {ttft * 1000:.0f}ms")
print(f"TTC:  {total_time * 1000:.0f}ms")
print(f"OTPS: {otps:.1f} tokens/sec ({tokens} tokens / {gen_time:.3f}s)")

PRICING = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
    "claude-opus-4-7": {"input": 5.00, "output": 25.00},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> tuple[float, float, float]:
    prices = PRICING.get(model, {"input": 3.00, "output": 15.00})
    # TODO: トークン数と価格からinput_cost、output_cost、合計コストを計算する
    pass

ttft, total_time, response = _stream_request("What is 2 + 2? Answer in one word.")

usage = response.usage
input_cost, output_cost, cost = calculate_cost(DEFAULT_MODEL, usage.input_tokens, usage.output_tokens)

print(f"Response: {response.content[0].text}")
print(f"Tokens: {usage.input_tokens} in / {usage.output_tokens} out")
print(f"Cost:   ${cost:.6f} (input: ${input_cost:.6f}, output: ${output_cost:.6f})")

def measure_streaming_latency(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 256,
    test_name: str = "streaming"
) -> BenchmarkResult:
    ttft, total_time, response = _stream_request(prompt, model, max_tokens)
    usage = response.usage
    _, _, cost = calculate_cost(model, usage.input_tokens, usage.output_tokens)
    otps, _ = compute_otps(ttft, total_time, usage.output_tokens)

    return BenchmarkResult(
        ttft=ttft,
        total_time=total_time,
        tokens_per_second=otps,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        endpoint="1p",
        model=model,
        test_name=test_name,
        otps=otps,
        cost=cost,
    )

def percentile(data, p):
    sorted_data = sorted(data)
    idx = (len(sorted_data) - 1) * p / 100
    low = int(idx)
    high = min(low + 1, len(sorted_data) - 1)
    fraction = idx - low
    return sorted_data[low] + fraction * (sorted_data[high] - sorted_data[low])

suite.clear()
PROMPT = "What is machine learning? Answer in 2 sentences."

models = [
    (MODEL_HAIKU, "haiku"),
    (MODEL_SONNET, "sonnet"),
    (MODEL_OPUS, "opus"),
]

for model_id, model_name in models:
    print(f"\nBenchmarking {model_name}...")

    for i in range(5):
        result = measure_streaming_latency(PROMPT, model=model_id, test_name=model_name)
        suite.add_result(result)

        ttft_ms = result.ttft * 1000
        ttc_ms = result.total_time * 1000

        print(f"  Run {i+1}: TTFT={ttft_ms:.0f}ms, TTC={ttc_ms:.0f}ms, OTPS={result.otps:.1f}, Cost=${result.cost:.6f}")

print("\n" + suite.summary())

import json

# TODO: ツールスキーマのプロパティを定義する
CALCULATOR_TOOL = {
    "name": "calculator",
    "description": "Performs basic arithmetic operations.",
    "input_schema": {
        "type": "object",
        "properties": {
            # TODO: "operation"（文字列 enum）と "operands"（数値の配列）
        },
        "required": ["operation", "operands"]
    }
}

print("Calculator tool:")
print(json.dumps(CALCULATOR_TOOL, indent=2))

def execute_calculator(operation: str, operands: list) -> float:
    """電卓の演算を実行する。"""
    a, b = operands[0], operands[1]

    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Unknown: {operation}")

print(f"Test: 42 * 17 = {execute_calculator('multiply', [42, 17])}")

def measure_tool_use_latency(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 256):
    """ツール使用リクエストのフルラウンドトリップレイテンシを計測する。"""

    start_time = time.perf_counter()

    # TODO: tools=[CALCULATOR_TOOL] を指定した最初の API 呼び出し
    first_response = None  # TODO

    ttft = time.perf_counter() - start_time

    # TODO: first_response.content から tool_use ブロックを見つける
    tool_use_block = None  # TODO

    if tool_use_block is None:
        # ツール使用なし - 早期リターン
        total_time = time.perf_counter() - start_time
        return ttft, total_time, "No tool used", first_response.usage.input_tokens, first_response.usage.output_tokens

    # TODO: ツールを実行し、結果を2回目の API 呼び出しで返す
    result = None  # TODO
    second_response = None  # TODO

    total_time = time.perf_counter() - start_time

    # 最終テキストを抽出する
    final_text = ""
    for block in second_response.content:
        if hasattr(block, "text"):
            final_text += block.text

    total_input = first_response.usage.input_tokens + second_response.usage.input_tokens
    total_output = first_response.usage.output_tokens + second_response.usage.output_tokens

    return ttft, total_time, final_text, total_input, total_output

# ツール使用をテストする
ttft, total, text, in_tok, out_tok = measure_tool_use_latency("What is 42 * 17? Use the calculator.")

print(f"TTFT: {ttft*1000:.0f}ms")
print("\n✓ Tool use working!")

# 比較: ツールあり vs ツールなし
suite.clear()

print("Without tool:")
for i in range(5):
    result = measure_streaming_latency(
        "What is forty-two times seventeen? Show your work.",
        test_name="no_tool"
    )
    suite.add_result(result)
    print(f"  Run {i+1}: TTFT={result.ttft*1000:.0f}ms, TTC={result.total_time*1000:.0f}ms, Cost=${result.cost:.6f}")

print("\nWith tool:")
for i in range(5):
    ttft, total_time, text, in_tok, out_tok = measure_tool_use_latency(
        "What is 42 * 17? Use the calculator."
    )
    _, _, cost = calculate_cost(DEFAULT_MODEL, in_tok, out_tok)
    otps, gen_time = compute_otps(ttft, total_time, out_tok)

    result = BenchmarkResult(
        ttft=ttft,
        total_time=total_time,
        tokens_per_second=otps,
        input_tokens=in_tok,
        output_tokens=out_tok,
        endpoint="1p",
        model=DEFAULT_MODEL,
        test_name="with_tool",
        otps=otps,
        cost=cost,
    )
    suite.add_result(result)
    print(f"  Run {i+1}: TTFT={ttft*1000:.0f}ms, TTC={total_time*1000:.0f}ms, Cost=${cost:.6f}")

print("\n" + suite.summary())

# キャッシュに十分な大きさのシステムプロンプトを構築する（>1024 トークン）
SYSTEM_PROMPT = """You are an expert API documentation assistant.
You help developers understand REST API design, authentication patterns,
security best practices, rate limiting, pagination, error handling,
versioning strategies, webhook design, and performance optimization.
Always provide concrete examples with HTTP methods and status codes.
""" * 20

# TODO: cache_control を有効にした system_block を作成する
system_block = None  # TODO

# TODO: system=system_block を使って API 呼び出しを行う
def cached_request(question):
    start = time.perf_counter()
    response = None  # TODO
    elapsed = time.perf_counter() - start
    return response, elapsed

# 呼び出し1: コールド — キャッシュを作成する
r1, time1 = cached_request("What is REST?")
print(f"Cold call: {time1 * 1000:.0f}ms")
print(f"  Cache created: {r1.usage.cache_creation_input_tokens or 0} tokens")
print(f"  Cache read:    {r1.usage.cache_read_input_tokens or 0} tokens")
print(f"  Input tokens:  {r1.usage.input_tokens}")

# 呼び出し2: ウォーム — キャッシュから読み込む（異なる質問、同じシステムプロンプト）
r2, time2 = cached_request("What is OAuth?")
print(f"\nWarm call: {time2 * 1000:.0f}ms")
print(f"  Cache created: {r2.usage.cache_creation_input_tokens or 0} tokens")
print(f"  Cache read:    {r2.usage.cache_read_input_tokens or 0} tokens")
print(f"  Input tokens:  {r2.usage.input_tokens}")

SYSTEM_PROMPT = """You are a helpful API design consultant. You specialize in REST API design,
authentication patterns, rate limiting, pagination, error handling, versioning strategies,
webhook design, and performance optimization. Always provide concrete examples with HTTP
methods, status codes, request/response schemas, and curl commands.
""" * 20

SYSTEM = [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]

# マルチターンキャッシュ: API 呼び出し前に直前のアシスタントメッセージに cache_control を付与する
# — これにより Claude に「ここまでをキャッシュする」と指示できる。
def chat(messages, new_question):
    # 古いキャッシュブレークポイントをクリアする（リストコンテンツをプレーンテキストに戻す）
    for msg in messages:
        if msg["role"] == "assistant" and isinstance(msg["content"], list):
            msg["content"] = msg["content"][0]["text"]

    # TODO: 最後のアシスタントメッセージ（あれば）に cache_control を追加する
    # ヒント: content を [{"type": "text", "text": ..., "cache_control": {"type": "ephemeral"}}] に変換する
    if messages and messages[-1]["role"] == "assistant":
        pass  # ここに cache_control を追加する

    messages.append({"role": "user", "content": new_question})

    start = time.perf_counter()
    response = client.messages.create(
        model=MODEL_SONNET,
        max_tokens=300,
        system=SYSTEM,
        messages=messages,
    )
    elapsed = time.perf_counter() - start

    answer = response.content[0].text
    messages.append({"role": "assistant", "content": answer})

    return answer, elapsed, response.usage


conversation = []
questions = [
    "Design a REST API for a todo app. Include all endpoints.",
    "Now add authentication. What changes?",
    "Add rate limiting. How should the headers look?",
    "Now add team support — users can share todo lists.",
    "Summarize the full API design so far.",
]

for i, question in enumerate(questions):
    answer, elapsed, usage = chat(conversation, question)

    cached = usage.cache_read_input_tokens or 0
    created = usage.cache_creation_input_tokens or 0

    print(f"Turn {i+1}: {elapsed * 1000:.0f}ms | cached: {cached} | created: {created}")

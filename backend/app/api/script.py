import os
import time
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

key = os.getenv("GROK_API_KEY")  # still using your existing env var name
if not key:
    print("ERROR: GROK_API_KEY not found in .env")
    exit(1)

client = Groq(api_key=key)

# ── Fetch all available models dynamically ─────────────────────────────────
print("Fetching available models from Groq...\n")
try:
    all_models = client.models.list()
    model_ids = sorted([m.id for m in all_models.data])
except Exception as e:
    print(f"Could not fetch model list: {e}")
    exit(1)

print(f"Found {len(model_ids)} models: {model_ids}\n")
print("─" * 70)

# ── Test prompt (short but realistic) ─────────────────────────────────────
PROMPT = "In exactly one sentence, explain what a neural network is."

results = []

for model_id in model_ids:
    print(f"Testing: {model_id} ...")
    try:
        t_start = time.perf_counter()

        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": PROMPT}],
            max_tokens=200,
        )

        t_end = time.perf_counter()
        elapsed = t_end - t_start

        usage = response.usage
        prompt_tokens     = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens      = usage.total_tokens
        text              = response.choices[0].message.content.strip()

        tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0

        print(f"  ✅ OK")
        print(f"     Time:              {elapsed:.2f}s")
        print(f"     Prompt tokens:     {prompt_tokens}")
        print(f"     Completion tokens: {completion_tokens}")
        print(f"     Total tokens:      {total_tokens}")
        print(f"     Speed:             {tokens_per_sec:.1f} tokens/sec")
        print(f"     Reply:             {text[:120]}")

        results.append({
            "model":             model_id,
            "status":            "ok",
            "elapsed_s":         round(elapsed, 3),
            "prompt_tokens":     prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens":      total_tokens,
            "tokens_per_sec":    round(tokens_per_sec, 1),
            "reply":             text,
        })

    except Exception as e:
        error = str(e)
        if "429" in error:
            tag = "🔴 RATE LIMITED"
        elif "404" in error:
            tag = "⚪ NOT FOUND"
        elif "403" in error:
            tag = "🟡 FORBIDDEN"
        elif "529" in error or "503" in error:
            tag = "🟠 OVERLOADED"
        else:
            tag = f"🟠 ERROR"
        print(f"  {tag} — {error[:120]}")
        results.append({
            "model":  model_id,
            "status": tag,
            "error":  error[:200],
        })

    print()
    time.sleep(1)  # light delay — Groq is generous but don't hammer it

# ── Final ranked summary ───────────────────────────────────────────────────
working = [r for r in results if r["status"] == "ok"]
failed  = [r for r in results if r["status"] != "ok"]

print("\n" + "═" * 70)
print("  RESULTS — RANKED BY SPEED (tokens/sec, highest = fastest)")
print("═" * 70)
print(f"  {'#':<3} {'Model':<40} {'Time':>6} {'Tok/s':>7} {'Comp↓':>6} {'Total':>6}")
print("  " + "─" * 66)

ranked_speed = sorted(working, key=lambda x: x["tokens_per_sec"], reverse=True)
for i, r in enumerate(ranked_speed, 1):
    print(f"  {i:<3} {r['model']:<40} {r['elapsed_s']:>5.2f}s {r['tokens_per_sec']:>6.1f} {r['completion_tokens']:>6} {r['total_tokens']:>6}")

print("\n" + "─" * 70)
print("  RANKED BY FEWEST COMPLETION TOKENS (most concise / cheapest output)")
print("─" * 70)
print(f"  {'#':<3} {'Model':<40} {'Comp↓':>6} {'Total':>6} {'Time':>7}")
print("  " + "─" * 66)

ranked_tokens = sorted(working, key=lambda x: x["completion_tokens"])
for i, r in enumerate(ranked_tokens, 1):
    print(f"  {i:<3} {r['model']:<40} {r['completion_tokens']:>6} {r['total_tokens']:>6} {r['elapsed_s']:>6.2f}s")

if failed:
    print("\n" + "─" * 70)
    print("  FAILED MODELS")
    print("─" * 70)
    for r in failed:
        print(f"  {r['status']:<25} {r['model']}")

print("\n" + "═" * 70)
print("  Paste these results back and I'll tell you the best model to use.")
print("═" * 70)
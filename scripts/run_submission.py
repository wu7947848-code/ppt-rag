"""Run benchmark on question_set.json and save submission."""
import sys, os, json, time, asyncio
sys.path.insert(0, r"C:\Users\wangl\Hacker\ppt-rag")
sys.path.insert(0, r"C:\Users\wangl\Hacker\ppt-rag\backend")

from bench.runner import run_benchmark
from config import BENCH_CONCURRENCY, RERANK_ENABLED, QUERY_EXPAND_ENABLED

QUESTION_SET = r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\json\question_set.json"
OUTPUT_PATH = r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\json\submission.json"

async def main():
    print(f"Config: concurrency={BENCH_CONCURRENCY}, rerank={RERANK_ENABLED}, "
          f"query_expand={QUERY_EXPAND_ENABLED}")
    print(f"Loading questions from: {QUESTION_SET}")
    t0 = time.time()

    result = await run_benchmark(
        question_set_path=QUESTION_SET,
        output_path=OUTPUT_PATH,
        concurrency=BENCH_CONCURRENCY,
    )

    elapsed = time.time() - t0
    print(f"\nBenchmark complete in {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"Total: {result['total']}, Success: {result['success']}, "
          f"Failed: {result['total'] - result['success']}")
    print(f"Output saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())

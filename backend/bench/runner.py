import json
import asyncio
import sys
from pathlib import Path

_BACKEND_DIR = str(Path(__file__).parent.parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


async def run_benchmark(question_set_path: str, output_path: str, concurrency: int = 8) -> dict:
    with open(question_set_path, encoding="utf-8") as f:
        qs = json.load(f)
    tasks = qs["tasks"]
    semaphore = asyncio.Semaphore(concurrency)
    results = [None] * len(tasks)

    async def process_one(idx: int, task: dict):
        async with semaphore:
            try:
                question = task["question"]
                options_raw = task.get("options", "")
                if isinstance(options_raw, list):
                    options = options_raw
                elif options_raw and isinstance(options_raw, str) and options_raw.strip().startswith("["):
                    options = json.loads(options_raw)
                else:
                    options = []

                # Offload sync retrieval + QA to a thread so the event loop stays free
                def _run_sync():
                    from retrieval.hybrid import query_for_retrieval
                    from qa.dispatcher import answer
                    pages = query_for_retrieval(question, options, top_k_final=5)
                    return answer(task, pages)

                result = await asyncio.to_thread(_run_sync)
                results[idx] = {**task, **result}

            except Exception as e:
                results[idx] = {
                    **task,
                    "modelAnswer": "",
                    "evidence": [],
                    "confidence": None,
                    "status": "failed",
                    "latencyMs": None,
                    "error": str(e),
                }

    await asyncio.gather(*[process_one(i, t) for i, t in enumerate(tasks)])

    qs["tasks"] = results
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if r and r.get("status") == "success")
    return {"total": len(tasks), "success": success}

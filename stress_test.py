"""Stress test: ingest all 10 docs, run sample questions, measure accuracy & latency."""
import json, asyncio, pathlib, time, sys, os

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8')

from backend import config
from backend.index import catalog, bm25_store
from backend.ingest import pipeline
from backend.retrieval.hybrid import query_for_retrieval
from backend.qa.dispatcher import answer as dispatch_answer

DATASET = pathlib.Path(
    r'C:/Users/wangl/xwechat_files/wxid_7puf6hwr9fx112_dfbe/msg/file/2026-05/'
    r'赛题5_PPT文档结构化检索与问答（含样例集）_16955001/'
    r'赛题5 PPT文档结构化检索与问答_样例集/赛题5 PPT文档结构化检索与问答_样例集'
)
DOCS_DIR = DATASET / 'dataset' / 'documents'
QUESTION_FILE = DATASET / 'json' / 'question_set.json'
ANSWER_FILE = DATASET / 'json' / 'answer_set.json'

# ---- Phase 1: Ingest all 10 documents ----
print('='*60)
print('PHASE 1: Ingesting all 10 documents')
print('='*60)

# Clean
for d in list(catalog.list_all()):
    try: catalog.delete(d['doc_id'])
    except: pass
for f in config.PAGES_DIR.glob('*'): f.unlink()
for f in config.RAW_DIR.glob('*'): f.unlink()
for f in config.THUMBS_DIR.glob('*'): f.unlink()
bm25_pkl = config.INDEX_DIR / 'bm25.pkl'
if bm25_pkl.exists(): bm25_pkl.unlink()

docs = sorted(DOCS_DIR.glob('*'))
ingest_times = []
for i, doc_path in enumerate(docs):
    if doc_path.suffix.lower() not in ('.pdf', '.pptx', '.ppt'):
        continue
    t0 = time.time()
    doc_id = pipeline.ingest(doc_path, original_filename=doc_path.name)
    asyncio.run(pipeline.ingest_background(doc_id, doc_path.suffix.lower(), doc_path.name))
    elapsed = time.time() - t0
    status = catalog.get(doc_id)['status'] if catalog.get(doc_id) else 'NONE'
    pages = catalog.get(doc_id).get('total_pages', 0) if catalog.get(doc_id) else 0
    ingest_times.append(elapsed)
    print(f'  [{i+1:2d}/10] {doc_path.name[:60]:60s} | {elapsed:5.1f}s | {status:8s} | {pages:3d}p')

total_pages = sum(
    d.get('total_pages', 0) for d in catalog.list_all() if d['status'] == 'indexed'
)
print(f'\n  Total: {len(ingest_times)} docs, {total_pages} pages, {sum(ingest_times):.0f}s total')
print(f'  Avg ingest: {sum(ingest_times)/len(ingest_times):.1f}s/doc')

# ---- Phase 2: Load gold answers ----
print(f'\n{"="*60}')
print('PHASE 2: Running sample questions')
print('='*60)

with open(ANSWER_FILE, encoding='utf-8') as f:
    answers_data = json.load(f)
gold_by_id = {}
for item in answers_data.get('answers', []):
    gold_by_id[str(item['id'])] = item

# ---- Phase 3: Run questions (first 30 from each type) ----
with open(QUESTION_FILE, encoding='utf-8') as f:
    question_data = json.load(f)

# Pick ~30 questions spanning all 5 types
import random
random.seed(42)
tasks = question_data['tasks']
# Group by type
by_type = {}
for t in tasks:
    qt = t['questionType']
    by_type.setdefault(qt, []).append(t)
# Take up to 6 from each type
sample_tasks = []
for qt, items in by_type.items():
    sample_tasks.extend(random.sample(items, min(6, len(items))))

print(f'\nRunning {len(sample_tasks)} questions (concurrency=4)...\n')

results = []
sem = asyncio.Semaphore(4)

async def process_one(idx, task):
    async with sem:
        qid = task['id']
        question = task['question']
        qt = task['questionType']
        options_raw = task.get('options', '')

        if isinstance(options_raw, str) and options_raw:
            try: options = json.loads(options_raw)
            except: options = []
        else:
            options = options_raw if isinstance(options_raw, list) else []

        t0 = time.time()
        try:
            pages = query_for_retrieval(question, options=options, top_k_final=5)
            result = dispatch_answer(task, pages)
        except Exception as e:
            result = {'modelAnswer': '', 'evidence': [], 'status': 'failed', 'latencyMs': 0}

        latency = int((time.time() - t0) * 1000)

        # Compare with gold
        gold = gold_by_id.get(str(qid), {})
        gold_answer = gold.get('correctAnswer', '')

        # Simple correctness check
        pred = result.get('modelAnswer', '')
        if qt == 'single_choice':
            correct = str(pred).upper() == str(gold_answer).upper()
        elif qt == 'multiple_choice':
            correct = sorted(pred) == sorted(gold_answer) if isinstance(pred, list) and isinstance(gold_answer, list) else False
        elif qt == 'true_false':
            correct = str(pred) == str(gold_answer)
        elif qt == 'short_answer':
            correct = str(pred).strip().lower() == str(gold_answer).strip().lower()
        else:
            correct = None  # open_ended needs LLM judge

        correct_str = 'OK' if correct else ('FAIL' if correct is False else '---')
        print(f'  [{qid:4d}] {qt:15s} | {latency:5d}ms | {correct_str:4s} | {str(pred)[:50]}')

        return {
            'id': qid, 'questionType': qt, 'latencyMs': latency,
            'prediction': pred, 'gold': gold_answer, 'correct': correct,
            'status': result.get('status', 'unknown'),
        }

async def run_all():
    return await asyncio.gather(*[process_one(i, t) for i, t in enumerate(sample_tasks)])

results = asyncio.run(run_all())

# ---- Summary ----
print(f'\n{"="*60}')
print('RESULTS')
print('='*60)

scored = [r for r in results if r['correct'] is not None]
correct_count = sum(1 for r in scored if r['correct'])
latencies = [r['latencyMs'] for r in results if r['latencyMs'] is not None]
failed = sum(1 for r in results if r['status'] == 'failed')

print(f'  Questions: {len(results)}')
print(f'  Scorable:  {len(scored)}')
print(f'  Correct:   {correct_count}/{len(scored)} ({100*correct_count/len(scored):.1f}%)' if scored else '')
print(f'  Failed:    {failed}')
print(f'  Latency:   avg={sum(latencies)/len(latencies):.0f}ms  min={min(latencies)}ms  max={max(latencies)}ms' if latencies else '')

# By type
print(f'\n  By question type:')
for qt in sorted(set(r['questionType'] for r in results)):
    items = [r for r in results if r['questionType'] == qt]
    scored_items = [r for r in items if r['correct'] is not None]
    lats = [r['latencyMs'] for r in items]
    acc = f'{100*sum(1 for r in scored_items if r["correct"])/len(scored_items):.0f}%' if scored_items else 'N/A'
    print(f'    {qt:15s}: {len(items):2d} qs | accuracy={acc:4s} | avg_latency={sum(lats)/len(lats):.0f}ms')

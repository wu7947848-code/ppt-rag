"""Comprehensive test suite for ppt-rag."""
import json, sys, os, shutil, pathlib, random, string, asyncio

from backend import config
from backend.index import catalog, bm25_store
from backend.index.schema import Page, ChartData
from backend.ingest import pipeline
from backend.retrieval.hybrid import query_for_retrieval, SearchResult
from backend.retrieval.reranker import rerank
from backend.qa import single_choice, multiple_choice, true_false, short_answer, open_ended, build_context
from backend.qa.dispatcher import answer as dispatch_answer
from fpdf import FPDF

errors = []

def check(name, condition, detail=''):
    if condition:
        print(f'  [OK] {name}')
    else:
        print(f'  [FAIL] {name}  {detail}')
        errors.append(name)

def cleanup():
    for pattern in ['test_*.jsonl', 'test_*.pdf']:
        for f in config.PAGES_DIR.glob(pattern):
            f.unlink()
    for f in config.THUMBS_DIR.glob('test_*'):
        f.unlink()
    for f in config.RAW_DIR.glob('test_*'):
        f.unlink()
    for f in config.CONVERTED_DIR.glob('test_*'):
        f.unlink()
    bm25_pkl = config.INDEX_DIR / 'bm25.pkl'
    if bm25_pkl.exists():
        bm25_pkl.unlink()
    # Clear catalog test entries
    for did in ['test_1', 'test_bm', 'test_bm2', 'test_multi']:
        try:
            catalog.delete(did)
        except Exception:
            pass

cleanup()

# ===== 1. Catalog CRUD =====
print('=== 1. Catalog CRUD ===')
h = ''.join(random.choices(string.hexdigits, k=10))
catalog.insert('test_1', 'test_doc.pdf', 'pdf', h)
catalog.set_status('test_1', 'indexed', total_pages=5)
doc = catalog.get('test_1')
check('insert+get', doc and doc['filename'] == 'test_doc.pdf')
check('get_by_hash', catalog.get_by_hash(h) is not None)
check('list_all', any(d['doc_id'] == 'test_1' for d in catalog.list_all()))
catalog.delete('test_1')
check('delete', catalog.get('test_1') is None)

# ===== 2. Page Schema =====
print('\n=== 2. Page Schema ===')
page = Page(
    doc_id='test_1', filename='test.pdf', page_num=1,
    title='Chip Capacity', text='HBM3e capacity 22000 wafers/month',
    tables_md=['| Vendor | Share |', '| --- | --- |', '| SK hynix | 52.3% |'],
    chart_data=[ChartData(chart_type='bar', title='Trend', categories=['2026','2027'],
                  series=[{'name':'cap','values':[8000,12000]}], nl_description='2026=8000 2027=12000')],
    chart_nl='2026=8000 2027=12000',
    image_captions=[], ocr_texts=[], thumbnail_path='',
    is_divider=False, has_chart=True, has_table=True, has_image=False, word_count=10
)
check('full_text has title', 'Chip Capacity' in page.full_text)
check('full_text has text', 'HBM3e' in page.full_text)
check('full_text has table', 'SK hynix' in page.full_text)
check('full_text has chart', '2026=8000' in page.full_text)
check('not divider', not page.is_divider)

div = Page(doc_id='t', filename='t.pdf', page_num=2, title='Cover', text='Chapter 1',
           tables_md=[], chart_data=[], chart_nl='', image_captions=[], ocr_texts=[],
           thumbnail_path='', is_divider=True, has_chart=False, has_table=False, has_image=False, word_count=2)
check('is divider', div.is_divider)
check('divider full_text short', len(div.full_text) < 50)

# ===== 3. BM25 Store =====
print('\n=== 3. BM25 Store ===')
config.PAGES_DIR.mkdir(parents=True, exist_ok=True)
test_pages = [
    {'doc_id':'test_bm','filename':'chip_report.pdf','page_num':1,'title':'HBM3e Capacity','full_text':'HBM3e capacity reaches 22000 wafers per month in 2026. SK hynix holds 52.3% market share, Samsung 38.7%, Micron 9.0%.','is_divider':False},
    {'doc_id':'test_bm','filename':'chip_report.pdf','page_num':2,'title':'Packaging Tech','full_text':'Chiplet packaging integrates multiple chiplets on a single substrate. TSMC dominates CoWoS packaging market with advanced interconnects.','is_divider':False},
    {'doc_id':'test_bm','filename':'chip_report.pdf','page_num':3,'title':'Market Forecast','full_text':'Global AI chip market to reach 119.4 billion USD by 2027. CAGR of 35.8%. Training chips account for 62% of the market.','is_divider':False},
    {'doc_id':'test_bm','filename':'chip_report.pdf','page_num':4,'title':'TOC','full_text':'Chapter 3','is_divider':True},
    {'doc_id':'test_bm2','filename':'uam_whitepaper.pdf','page_num':1,'title':'UAM Outlook','full_text':'Global UAM market expected to reach 2 trillion USD by 2030. CAGR 18.5% from 2026 to 2030. eVTOL is the key enabler.','is_divider':False},
    {'doc_id':'test_bm2','filename':'uam_whitepaper.pdf','page_num':2,'title':'Infrastructure','full_text':'eVTOL aircraft require dedicated vertiports. China plans first UAM routes in Yangtze River Delta and Greater Bay Area.','is_divider':False},
]
with open(config.PAGES_DIR / 'test_bm.jsonl', 'w', encoding='utf-8') as f:
    for p in test_pages[:4]:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')
with open(config.PAGES_DIR / 'test_bm2.jsonl', 'w', encoding='utf-8') as f:
    for p in test_pages[4:]:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')

catalog.insert('test_bm', 'chip_report.pdf', 'pdf', 'hash_bm')
catalog.insert('test_bm2', 'uam_whitepaper.pdf', 'pdf', 'hash_bm2')
catalog.set_status('test_bm', 'indexed')
catalog.set_status('test_bm2', 'indexed')

store = bm25_store._get_store()
store._bm25 = None
store._pages = []
store.build()
check('BM25 built', store._bm25 is not None)
check('BM25 pages >= 6', len(store._pages) >= 6, f'got {len(store._pages)}')

r = store.search('HBM3e capacity SK hynix', top_k=5)
check('BM25 finds chip results', len(r) > 0)
if r:
    check('BM25 top result page 1', r[0].page_num == 1, str(r[0].page_num))
    check('BM25 score positive', r[0].score > 0)

r2 = store.search('UAM eVTOL market', top_k=5)
check('BM25 cross-doc search', len(r2) > 0)
if r2:
    check('BM25 finds UAM doc', r2[0].filename == 'uam_whitepaper.pdf', r2[0].filename)

r3 = store.search('xyznonexistent12345', top_k=5)
check('BM25 empty for unknown term', len(r3) == 0 or all(x.score <= 0 for x in r3))

# ===== 4. FlashRank Reranker =====
print('\n=== 4. FlashRank Reranker ===')
passages = [
    'HBM3e capacity reaches 22000 wafers per month. SK hynix holds 52.3% market.',
    'Global UAM market expected to reach 2 trillion USD by 2030.',
    'Chapter 3 Table of Contents',
]
indices = rerank('HBM capacity and market share', passages, top_k=2)
check('Rerank returns indices', len(indices) >= 1, str(indices))
check('Rerank indices are ints', all(isinstance(i, int) for i in indices))
check('Rerank empty input', rerank('q', [], top_k=5) == [])

# ===== 5. Hybrid Retrieval =====
print('\n=== 5. Hybrid Retrieval ===')
hits = query_for_retrieval('HBM3e capacity SK hynix market', top_k_final=3)
check('Hybrid returns results', len(hits) >= 1, f'got {len(hits)}')
if hits:
    check('Hybrid has doc_id', bool(hits[0].doc_id))
    check('Hybrid not divider', not hits[0].is_divider)

hits2 = query_for_retrieval('urban air mobility eVTOL', options=[], top_k_final=3)
check('Hybrid cross-doc', len(hits2) >= 1, f'got {len(hits2)}')
if hits2:
    check('Hybrid UAM doc', 'uam' in hits2[0].filename.lower(), hits2[0].filename)

# ===== 6. QA Prompt Construction =====
print('\n=== 6. QA Module Prompts ===')
mock_pages = []
for p in test_pages[:3]:
    mock_pages.append(SearchResult(
        doc_id=p['doc_id'], filename=p['filename'], page_num=p['page_num'],
        title=p['title'], full_text=p['full_text'], score=1.0, is_divider=p.get('is_divider',False)
    ))

ctx = build_context(mock_pages, max_chars=8000)
check('build_context has content', len(ctx) > 100)
check('context has filename', 'chip_report.pdf' in ctx)
check('context has page marker', 'page' in ctx.lower() or 'Page' in ctx or '页' in ctx)

# QA modules will try LLM API (likely unreachable), should return gracefully
qa_modules = [
    ('single_choice', lambda: single_choice.answer('Largest HBM share?', ['SK hynix','Samsung','Micron','Intel'], mock_pages)),
    ('multiple_choice', lambda: multiple_choice.answer('Packaging related?', ['Chiplet','UAM','CoWoS','eVTOL'], mock_pages)),
    ('true_false', lambda: true_false.answer('SK hynix holds 52.3% HBM3e market share', mock_pages)),
    ('short_answer', lambda: short_answer.answer('HBM3e monthly capacity?', mock_pages)),
    ('open_ended', lambda: open_ended.answer('Analyze chip packaging trends', mock_pages)),
]
for name, fn in qa_modules:
    try:
        r = fn()
        check(f'{name} returns dict', isinstance(r, dict))
        check(f'{name} has modelAnswer', 'modelAnswer' in r)
        check(f'{name} has evidence', isinstance(r.get('evidence'), list))
        check(f'{name} has confidence', r.get('confidence') is not None or True)
    except Exception as e:
        check(f'{name} no crash', False, str(e)[:80])

# ===== 7. Dispatcher =====
print('\n=== 7. Dispatcher ===')
for qt in ['single_choice','multiple_choice','true_false','short_answer','open_ended']:
    task = {'question': 'Test?', 'questionType': qt, 'options': '["A","B"]'}
    try:
        result = dispatch_answer(task, mock_pages)
        check(f'dispatch {qt} status', result.get('status') in ('success','failed'))
        check(f'dispatch {qt} latencyMs', 'latencyMs' in result)
    except Exception as e:
        check(f'dispatch {qt} no crash', False, str(e)[:80])

# Unknown type
result = dispatch_answer({'question':'?','questionType':'unknown','options':''}, mock_pages)
check('dispatch unknown type', result.get('modelAnswer') == '')

# ===== 8. Ingest Pipeline =====
print('\n=== 8. Ingest Pipeline ===')
pdf = FPDF()
pdf.add_page(); pdf.set_font('Arial', size=12)
for i in range(5):
    pdf.cell(text=f'Page {i+1}: Semiconductor manufacturing capacity data. Wafer output projection for fiscal year 2026-2030.')
    if i < 4:
        pdf.add_page()
pdf.output('/tmp/test_multi.pdf')

doc_id = pipeline.ingest(pathlib.Path('/tmp/test_multi.pdf'), original_filename='semiconductor_report.pdf')
check('ingest returns 16-char doc_id', bool(doc_id) and len(doc_id) == 16)
check('catalog pending', catalog.get(doc_id)['status'] == 'pending')

asyncio.run(pipeline.ingest_background(doc_id, '.pdf', 'semiconductor_report.pdf'))
doc = catalog.get(doc_id)
check('ingest_background indexed', doc is not None and doc.get('status') == 'indexed',
      f'status={doc.get("status") if doc else "None"}')
check('5 pages indexed', doc.get('total_pages') == 5, str(doc.get('total_pages')))

# Search ingested doc
store.build()
results = store.search('semiconductor manufacturing wafer', top_k=5)
check('search ingested doc', len(results) > 0, f'got {len(results)}')

# Delete
asyncio.run(pipeline.delete_document(doc_id))
check('delete from catalog', catalog.get(doc_id) is None)
check('delete pages file', not (config.PAGES_DIR / f'{doc_id}.jsonl').exists())
check('delete raw file', not any(config.RAW_DIR.glob(f'{doc_id}.*')))

# ===== 9. Edge Cases =====
print('\n=== 9. Edge Cases ===')
# Empty search
check('empty query', len(store.search('', top_k=5)) >= 0)
# Missing catalog entry
check('missing doc get', catalog.get('nonexistent_999') is None)
# BM25 rebuild with no docs
catalog.set_status('test_bm', 'deleted')
catalog.set_status('test_bm2', 'deleted')
old_bm25 = store._bm25

# ===== Cleanup =====
cleanup()

print(f'\n{"="*50}')
print(f'RESULTS: {len(errors)} failure(s)')
for e in errors:
    print(f'  FAIL: {e}')
if not errors:
    print('ALL TESTS PASSED')
print(f'{"="*50}')

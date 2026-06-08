from pathlib import Path

DATA_DIR = Path("backend/data")
RAW_DIR = DATA_DIR / "raw"
CONVERTED_DIR = DATA_DIR / "converted"
PAGES_DIR = DATA_DIR / "pages"
THUMBS_DIR = DATA_DIR / "thumbs"
INDEX_DIR = DATA_DIR / "index"

SOFFICE_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"
SOFFICE_TIMEOUT = 180
THUMB_DPI = 96
THUMB_MAX_WIDTH = 960

BM25_TOP_K = 50

VLM_API_URL = "http://218.28.9.108:50053/v1/chat/completions"
VLM_API_KEY = "sk-ynR7W7SGyPZPbrwCUvItO3LZUf3UqCKvmmIlZPQNYhBYu5gm"
VLM_MODEL = "qwen3.6-plus"
VLM_TRIGGER_WORD_COUNT = 50  # Enable VLM for pages with <50 words and images

LLM_API_URL = "http://218.28.9.108:50053/v1/chat/completions"
LLM_API_KEY = "sk-ynR7W7SGyPZPbrwCUvItO3LZUf3UqCKvmmIlZPQNYhBYu5gm"
LLM_MODEL = "qwen2.5-32b-instruct"
# Fast with no thinking overhead. Other available models if needed:
#   "qwen3.6-plus" — with reasoning (thinking), 5-10x slower but more accurate
#   "deepseek-v4-pro" — fast, multi-task
#   "qwen3.6-max-preview" — stronger, fast

LLM_TIMEOUT = 90.0
VLM_TIMEOUT = 90.0
RERANK_TOP_K = 15  # BM25 candidates → LLM rerank → top 5
QUERY_EXPAND_ENABLED = False  # Skip LLM query expansion for speed
RERANK_ENABLED = False        # Skip LLM reranking (avoid 429 rate limits)

BENCH_CONCURRENCY = 5
BENCH_LATENCY_BEST_MS = 5000
BENCH_LATENCY_MAX_MS = 30000

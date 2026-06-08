import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BenchRequest(BaseModel):
    questionSetPath: str
    outputPath: str
    concurrency: int = 8

@router.post("/bench/run")
async def run_bench(req: BenchRequest):
    from bench.runner import run_benchmark
    result = await run_benchmark(req.questionSetPath, req.outputPath, req.concurrency)
    return result

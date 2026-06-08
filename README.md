# PPT 文档结构化检索与问答系统

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 (backend/config.py)
- 填写 `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL`
- 填写 `VLM_API_URL`, `VLM_API_KEY` (可选，用于图片描述)
- 如果 LibreOffice 不在 PATH，设置 `SOFFICE_PATH` 为绝对路径

### 3. 启动后端
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动前端
```bash
cd frontend
chainlit run app.py --port 8501
```

### 5. 运行 Benchmark
```bash
curl -X POST http://localhost:8000/bench/run \
  -H "Content-Type: application/json" \
  -d '{"questionSetPath": "/path/to/question_set.json", "outputPath": "/path/to/output.json"}'
```

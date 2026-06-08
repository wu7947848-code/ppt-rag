"""After benchmark completes: copy submission, run evaluator, show score."""
import sys, os, json, shutil, subprocess

SUBMISSION_JSON = r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\json\submission.json"
ANSWER_SET_JSON = r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\json\answer_set.json"
BENCHMARK_DIR = r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\benchmark"
SUBMIT_FOLDER = r"C:\Users\wangl\Desktop\赛题5提交材料\JSON结果文件"

def main():
    # 1. Check submission exists
    if not os.path.exists(SUBMISSION_JSON):
        print(f"ERROR: submission.json not found at {SUBMISSION_JSON}")
        sys.exit(1)

    size_kb = os.path.getsize(SUBMISSION_JSON) / 1024
    print(f"Submission found: {size_kb:.1f} KB")

    # 2. Quick stats
    with open(SUBMISSION_JSON, encoding='utf-8') as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    success = sum(1 for t in tasks if t.get('status') == 'success')
    failed = sum(1 for t in tasks if t.get('status') == 'failed')
    print(f"Tasks: {len(tasks)} total, {success} success, {failed} failed")

    # Average latency
    latencies = [t.get('latencyMs', 0) or 0 for t in tasks if t.get('latencyMs')]
    if latencies:
        avg_ms = sum(latencies) / len(latencies)
        print(f"Avg latency: {avg_ms:.0f}ms")

    # 3. Copy to submission folder
    dst = os.path.join(SUBMIT_FOLDER, "submission.json")
    shutil.copy2(SUBMISSION_JSON, dst)
    print(f"Copied to: {dst}")

    # 4. Run official evaluator
    print("\nRunning official evaluator...")
    result = subprocess.run(
        [
            sys.executable, "-m", "ppt_benchmark_evaluator.cli",
            "--gold", ANSWER_SET_JSON,
            "--submission", SUBMISSION_JSON,
            "--output", os.path.join(os.path.dirname(SUBMISSION_JSON), "report.json"),
        ],
        cwd=BENCHMARK_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])

    # 5. Read report
    report_path = os.path.join(os.path.dirname(SUBMISSION_JSON), "report.json")
    if os.path.exists(report_path):
        with open(report_path, encoding='utf-8') as f:
            report = json.load(f)
        print("\n=== SCORE REPORT ===")
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

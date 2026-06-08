import chainlit as cl
import httpx
import os
import asyncio

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

STYLE_CSS = """
<style>
  /* Constrain file list from overflowing viewport */
  .file-list-container { max-height: 240px; overflow-y: auto; padding: 4px 0; }
  .file-list-container::-webkit-scrollbar { width: 4px; }
  .file-list-container::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
  .file-item { display: flex; align-items: center; gap: 8px; padding: 4px 8px;
               font-size: 13px; color: #374151; border-radius: 4px; }
  .file-item:hover { background: #f3f4f6; }
  .file-icon { font-size: 14px; }
  .file-status { font-size: 11px; margin-left: auto; flex-shrink: 0; }
  .file-status.ok { color: #059669; }
  .file-status.fail { color: #dc2626; }
  /* Fix Chainlit native file elements horizontal overflow */
  .inline-file-container { flex-wrap: wrap !important; max-height: 200px; overflow-y: auto !important; }
  .inline-file-container::-webkit-scrollbar { width: 4px; }
  .inline-file-container::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }
  [class*=\"file-\"] { flex-shrink: 1; }
  /* Force all horizontal flex containers inside messages to wrap */
  .message-attachments, .elements-container, [class*=\"attachment\"] {
    flex-wrap: wrap !important; max-height: 160px; overflow-y: auto !important;
  }
  /* Source cards */
  .sources-box { margin-top: 8px; padding: 8px 12px;
                 background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; }
  .source-line { font-size: 12px; color: #6b7280; line-height: 1.6; }
  .meta-line { font-size: 11px; color: #9ca3af; margin-top: 4px; }
</style>
"""


@cl.on_chat_start
async def start():
    # Fetch existing documents
    doc_count = 0
    total_pages = 0
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{BACKEND_URL}/docs")
            if r.status_code == 200:
                docs = r.json()
                doc_count = len(docs)
                total_pages = sum(d.get("total_pages", 0) or 0 for d in docs)
    except Exception:
        pass

    welcome = (
        f"#  PPT 文档检索与问答\n\n"
        f"已索引 **{doc_count}** 份文档，共 **{total_pages}** 页\n\n"
        f"直接提问，或上传新的 PPT/PPTX/PDF 文档。"
    )
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    # ── file upload ──
    if message.elements:
        files = [e for e in message.elements if hasattr(e, 'path') and e.path]
        if not files:
            return

        # Build upload list
        items = []
        for i, elem in enumerate(files):
            doc_id = None
            ok = False
            async with httpx.AsyncClient(timeout=60) as c:
                try:
                    with open(elem.path, "rb") as f:
                        resp = await c.post(
                            f"{BACKEND_URL}/ingest",
                            files={"file": (elem.name, f)},
                        )
                    if resp.status_code == 200:
                        doc_id = resp.json()["docId"]
                        ok = True
                except Exception:
                    pass
            icon = "✅" if ok else "❌"
            status_class = "ok" if ok else "fail"
            suffix = elem.name.rsplit(".", 1)[-1].upper() if "." in elem.name else ""
            items.append(
                f'<div class="file-item">'
                f'<span class="file-icon">{icon}</span>'
                f'<span>{elem.name}</span>'
                f'<span class="file-label">{suffix}</span>'
                f'<span class="file-status {status_class}">{"OK" if ok else "FAIL"}</span>'
                f'</div>'
            )

        count = len(items)
        html = f'<div class="file-list-container">{"".join(items)}</div>'
        # Clear Chainlit elements so they don't render as horizontal file cards
        message.elements.clear()
        await cl.Message(
            content=f"**已上传 {count} 份文档**\n{html}\n\n后台解析中，稍候即可提问。",
            elements=[],
        ).send()
        return

    # ── QA ──
    question = message.content.strip()
    if not question:
        return

    async with httpx.AsyncClient(timeout=120) as c:
        try:
            resp = await c.post(
                f"{BACKEND_URL}/query",
                json={"question": question, "topK": 10, "questionType": "open_ended"},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            await cl.Message(content=f"❌ 查询失败: {e}").send()
            return

    answer = data.get("answer", "") or "（未找到相关信息）"
    evidence = data.get("evidence", []) or []
    latency = data.get("latencyMs", 0)

    # Build sources block
    source_parts = []
    for e in evidence[:6]:
        doc = e.get("docId", "?")
        page = e.get("page", "?")
        quote = (e.get("quote", "") or "")[:120]
        source_parts.append(
            f'<div class="source-line">📄 <b>{doc}</b> / 第 {page} 页</div>'
            f'<div class="meta-line">"{quote}"</div>'
        )

    sources_html = ""
    if source_parts:
        sources_html = f'<div class="sources-box">{"".join(source_parts)}</div>'

    full = (
        f'{STYLE_CSS}'
        f'{answer}\n\n'
        f'{sources_html}'
        f'<div class="meta-line">置信度 {data.get("confidence", 0):.0%} &nbsp;|&nbsp; {latency}ms</div>'
    )

    await cl.Message(content=full).send()

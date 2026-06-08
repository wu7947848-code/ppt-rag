# PPT RAG · Web 前端

苹果官网风格的单文件前端，无构建步骤。

## 启动

后端必须先运行（端口 8000）：

```
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

然后启动静态服务器：

```
cd frontend-web
python -m http.server 5173
```

浏览器打开 http://127.0.0.1:5173

## 结构说明

- **TopBar** — 顶部条，标题 + 主题切换
- **DocPanel** — 左侧 320px：品牌、文档/页数统计、上传、筛选、文档列表（hover 显示删除）
- **Chat**     — 主区：欢迎区 + 示例问题、消息流、底部 composer（题型/topK/输入）
- **SourceCard** — 答案下方的证据卡（缩略图 + 页码 + 原文片段，最多 3 行）

## 设计 Tokens

CSS 变量集中在 `:root` 与 `html.dark`：

| 类别       | 变量                                                         |
|----------|------------------------------------------------------------|
| 颜色 · 表面 | `--bg / --bg-elev / --bg-soft / --surface`                 |
| 颜色 · 边框 | `--border / --border-soft`                                 |
| 颜色 · 文字 | `--fg / --fg-muted / --fg-subtle`                          |
| 颜色 · 语义 | `--accent / --accent-soft / --success / --warning / --danger` |
| 圆角       | `--r-sm 6 / --r-md 10 / --r-lg 14 / --r-xl 20`             |
| 投影       | `--shadow-1 / --shadow-2 / --shadow-3`                     |
| 字号       | 32 / 24 / 20 / 16 / 14 / 12（含对应行高）                   |
| 间距       | Tailwind 的 1/2/3/4/5/6/8/10/12 = 4/8/12/16/20/24/32/40/48 |

主题切换通过 `html.dark` 类，状态写入 `localStorage`。

## API 约定

读自 `window.__API__`，默认 `http://127.0.0.1:8000`。如需改地址，在 `index.html` 顶部加：

```html
<script>window.__API__ = 'http://your-host:8000'</script>
```

## 修改建议

- 颜色/字号/间距 — 改 `:root` CSS 变量即可全局生效。
- 示例问题 — `Chat` 组件 `samples` 数组。
- 题型选项 — `QUESTION_TYPES` 数组。
- 状态文案 — `STATUS_LABEL` 对象。

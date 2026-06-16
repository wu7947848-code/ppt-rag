# PPT-RAG

A Retrieval-Augmented Generation (RAG) system designed for PPT documents, featuring a web-based user interface for document ingestion, semantic search, and intelligent question answering.

## Features
- Ingest and index PPT/PPTX documents with automatic parsing
- Semantic search across presentation content
- LLM-powered question answering with source citations
- Web-based UI for easy interaction

## Tech Stack
- **Language:** Python
- **RAG Framework:** RAGFlow
- **Frontend:** Web UI
- **Document Processing:** python-pptx

## Quick Start
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Requirement already satisfied: fastapi>=0.111.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 1)) (0.115.14)
Requirement already satisfied: uvicorn>=0.29.0 in d:\softwares\anaconda4\lib\site-packages (from uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (0.41.0)
Requirement already satisfied: python-pptx>=0.6.23 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 3)) (1.0.2)
Requirement already satisfied: PyMuPDF>=1.24.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 4)) (1.27.2.3)
Requirement already satisfied: pdfplumber>=0.11.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 5)) (0.11.9)
Requirement already satisfied: rank-bm25>=0.2.2 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 6)) (0.2.2)
Requirement already satisfied: jieba>=0.42.1 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 7)) (0.42.1)
Requirement already satisfied: httpx>=0.27.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 8)) (0.28.1)
Requirement already satisfied: openpyxl>=3.1.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 9)) (3.1.5)
Requirement already satisfied: lxml>=5.0.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 10)) (5.3.0)
Requirement already satisfied: pydantic>=2.7.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 11)) (2.12.5)
Requirement already satisfied: chainlit>=1.1.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 12)) (2.4.301)
Requirement already satisfied: python-multipart>=0.0.9 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 13)) (0.0.18)
Requirement already satisfied: aiosqlite>=0.20.0 in c:\users\wangl\appdata\roaming\python\python312\site-packages (from -r requirements.txt (line 14)) (0.22.1)
Requirement already satisfied: numpy>=1.26.0 in d:\softwares\anaconda4\lib\site-packages (from -r requirements.txt (line 15)) (2.4.4)
Requirement already satisfied: starlette<0.47.0,>=0.40.0 in d:\softwares\anaconda4\lib\site-packages (from fastapi>=0.111.0->-r requirements.txt (line 1)) (0.41.3)
Requirement already satisfied: typing-extensions>=4.8.0 in d:\softwares\anaconda4\lib\site-packages (from fastapi>=0.111.0->-r requirements.txt (line 1)) (4.15.0)
Requirement already satisfied: click>=7.0 in d:\softwares\anaconda4\lib\site-packages (from uvicorn>=0.29.0->uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (8.1.8)
Requirement already satisfied: h11>=0.8 in d:\softwares\anaconda4\lib\site-packages (from uvicorn>=0.29.0->uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (0.14.0)
Requirement already satisfied: Pillow>=3.3.2 in d:\softwares\anaconda4\lib\site-packages (from python-pptx>=0.6.23->-r requirements.txt (line 3)) (10.4.0)
Requirement already satisfied: XlsxWriter>=0.5.7 in d:\softwares\anaconda4\lib\site-packages (from python-pptx>=0.6.23->-r requirements.txt (line 3)) (3.2.9)
Requirement already satisfied: pdfminer.six==20251230 in d:\softwares\anaconda4\lib\site-packages (from pdfplumber>=0.11.0->-r requirements.txt (line 5)) (20251230)
Requirement already satisfied: pypdfium2>=4.18.0 in d:\softwares\anaconda4\lib\site-packages (from pdfplumber>=0.11.0->-r requirements.txt (line 5)) (5.8.0)
Requirement already satisfied: charset-normalizer>=2.0.0 in d:\softwares\anaconda4\lib\site-packages (from pdfminer.six==20251230->pdfplumber>=0.11.0->-r requirements.txt (line 5)) (3.3.2)
Requirement already satisfied: cryptography>=36.0.0 in c:\users\wangl\appdata\roaming\python\python312\site-packages (from pdfminer.six==20251230->pdfplumber>=0.11.0->-r requirements.txt (line 5)) (47.0.0)
Requirement already satisfied: anyio in d:\softwares\anaconda4\lib\site-packages (from httpx>=0.27.0->-r requirements.txt (line 8)) (4.12.1)
Requirement already satisfied: certifi in d:\softwares\anaconda4\lib\site-packages (from httpx>=0.27.0->-r requirements.txt (line 8)) (2025.4.26)
Requirement already satisfied: httpcore==1.* in d:\softwares\anaconda4\lib\site-packages (from httpx>=0.27.0->-r requirements.txt (line 8)) (1.0.2)
Requirement already satisfied: idna in d:\softwares\anaconda4\lib\site-packages (from httpx>=0.27.0->-r requirements.txt (line 8)) (3.7)
Requirement already satisfied: et-xmlfile in d:\softwares\anaconda4\lib\site-packages (from openpyxl>=3.1.0->-r requirements.txt (line 9)) (1.1.0)
Requirement already satisfied: annotated-types>=0.6.0 in d:\softwares\anaconda4\lib\site-packages (from pydantic>=2.7.0->-r requirements.txt (line 11)) (0.6.0)
Requirement already satisfied: pydantic-core==2.41.5 in d:\softwares\anaconda4\lib\site-packages (from pydantic>=2.7.0->-r requirements.txt (line 11)) (2.41.5)
Requirement already satisfied: typing-inspection>=0.4.2 in d:\softwares\anaconda4\lib\site-packages (from pydantic>=2.7.0->-r requirements.txt (line 11)) (0.4.2)
Requirement already satisfied: aiofiles<25.0.0,>=23.1.0 in c:\users\wangl\appdata\roaming\python\python312\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (24.1.0)
Requirement already satisfied: asyncer<0.0.8,>=0.0.7 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (0.0.7)
Requirement already satisfied: dataclasses_json<0.7.0,>=0.6.7 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (0.6.7)
Requirement already satisfied: filetype<2.0.0,>=1.2.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (1.2.0)
Requirement already satisfied: lazify<0.5.0,>=0.4.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (0.4.0)
Requirement already satisfied: literalai==0.1.103 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (0.1.103)
Requirement already satisfied: mcp<2.0.0,>=1.3.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (1.26.0)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.6.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (1.6.0)
Requirement already satisfied: packaging>=23.1 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (25.0)
Requirement already satisfied: pyjwt<3.0.0,>=2.8.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (2.11.0)
Requirement already satisfied: python-dotenv<2.0.0,>=1.0.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (1.2.2)
Requirement already satisfied: python-socketio<6.0.0,>=5.11.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (5.16.1)
Requirement already satisfied: syncer<3.0.0,>=2.0.3 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (2.0.3)
Requirement already satisfied: tomli<3.0.0,>=2.0.1 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (2.0.1)
Requirement already satisfied: uptrace<2.0.0,>=1.29.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.0)
Requirement already satisfied: watchfiles<0.21.0,>=0.20.0 in d:\softwares\anaconda4\lib\site-packages (from chainlit>=1.1.0->-r requirements.txt (line 12)) (0.20.0)
Requirement already satisfied: chevron>=0.14.0 in d:\softwares\anaconda4\lib\site-packages (from literalai==0.1.103->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.14.0)
Requirement already satisfied: colorama>=0.4 in d:\softwares\anaconda4\lib\site-packages (from uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (0.4.6)
Requirement already satisfied: httptools>=0.6.3 in d:\softwares\anaconda4\lib\site-packages (from uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (0.7.1)
Requirement already satisfied: pyyaml>=5.1 in d:\softwares\anaconda4\lib\site-packages (from uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (6.0.3)
Requirement already satisfied: websockets>=10.4 in d:\softwares\anaconda4\lib\site-packages (from uvicorn[standard]>=0.29.0->-r requirements.txt (line 2)) (13.1)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in d:\softwares\anaconda4\lib\site-packages (from dataclasses_json<0.7.0,>=0.6.7->chainlit>=1.1.0->-r requirements.txt (line 12)) (3.26.2)
Requirement already satisfied: typing-inspect<1,>=0.4.0 in d:\softwares\anaconda4\lib\site-packages (from dataclasses_json<0.7.0,>=0.6.7->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.9.0)
Requirement already satisfied: httpx-sse>=0.4 in d:\softwares\anaconda4\lib\site-packages (from mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.4.3)
Requirement already satisfied: jsonschema>=4.20.0 in d:\softwares\anaconda4\lib\site-packages (from mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (4.23.0)
Requirement already satisfied: pydantic-settings>=2.5.2 in d:\softwares\anaconda4\lib\site-packages (from mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (2.13.1)
Requirement already satisfied: pywin32>=310 in d:\softwares\anaconda4\lib\site-packages (from mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (311)
Requirement already satisfied: sse-starlette>=1.6.1 in d:\softwares\anaconda4\lib\site-packages (from mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (3.0.3)
Requirement already satisfied: bidict>=0.21.0 in d:\softwares\anaconda4\lib\site-packages (from python-socketio<6.0.0,>=5.11.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.23.1)
Requirement already satisfied: python-engineio>=4.11.0 in d:\softwares\anaconda4\lib\site-packages (from python-socketio<6.0.0,>=5.11.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (4.13.1)
Requirement already satisfied: opentelemetry-api~=1.41.0 in d:\softwares\anaconda4\lib\site-packages (from uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: opentelemetry-exporter-otlp~=1.41.0 in d:\softwares\anaconda4\lib\site-packages (from uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: opentelemetry-instrumentation~=0.62b0 in d:\softwares\anaconda4\lib\site-packages (from uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.62b1)
Requirement already satisfied: opentelemetry-sdk~=1.41.0 in d:\softwares\anaconda4\lib\site-packages (from uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: cffi>=2.0.0 in c:\users\wangl\appdata\roaming\python\python312\site-packages (from cryptography>=36.0.0->pdfminer.six==20251230->pdfplumber>=0.11.0->-r requirements.txt (line 5)) (2.0.0)
Requirement already satisfied: attrs>=22.2.0 in d:\softwares\anaconda4\lib\site-packages (from jsonschema>=4.20.0->mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (23.1.0)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in d:\softwares\anaconda4\lib\site-packages (from jsonschema>=4.20.0->mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (2023.7.1)
Requirement already satisfied: referencing>=0.28.4 in d:\softwares\anaconda4\lib\site-packages (from jsonschema>=4.20.0->mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.30.2)
Requirement already satisfied: rpds-py>=0.7.1 in d:\softwares\anaconda4\lib\site-packages (from jsonschema>=4.20.0->mcp<2.0.0,>=1.3.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.30.0)
Requirement already satisfied: importlib-metadata<8.8.0,>=6.0 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-api~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (8.5.0)
Requirement already satisfied: opentelemetry-exporter-otlp-proto-grpc==1.41.1 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: opentelemetry-exporter-otlp-proto-http==1.41.1 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: googleapis-common-protos~=1.57 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp-proto-grpc==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.74.0)
Requirement already satisfied: grpcio<2.0.0,>=1.63.2 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp-proto-grpc==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.80.0)
Requirement already satisfied: opentelemetry-exporter-otlp-proto-common==1.41.1 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp-proto-grpc==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: opentelemetry-proto==1.41.1 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp-proto-grpc==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.41.1)
Requirement already satisfied: requests~=2.7 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-exporter-otlp-proto-http==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (2.32.3)
Requirement already satisfied: protobuf<7.0,>=5.0 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-proto==1.41.1->opentelemetry-exporter-otlp-proto-grpc==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (5.29.6)
Requirement already satisfied: opentelemetry-semantic-conventions==0.62b1 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-instrumentation~=0.62b0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (0.62b1)
Requirement already satisfied: wrapt<3.0.0,>=1.0.0 in d:\softwares\anaconda4\lib\site-packages (from opentelemetry-instrumentation~=0.62b0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.17.3)
Requirement already satisfied: simple-websocket>=0.10.0 in d:\softwares\anaconda4\lib\site-packages (from python-engineio>=4.11.0->python-socketio<6.0.0,>=5.11.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.1.0)
Requirement already satisfied: mypy-extensions>=0.3.0 in d:\softwares\anaconda4\lib\site-packages (from typing-inspect<1,>=0.4.0->dataclasses_json<0.7.0,>=0.6.7->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.0.0)
Requirement already satisfied: pycparser in d:\softwares\anaconda4\lib\site-packages (from cffi>=2.0.0->cryptography>=36.0.0->pdfminer.six==20251230->pdfplumber>=0.11.0->-r requirements.txt (line 5)) (2.21)
Requirement already satisfied: zipp>=3.20 in d:\softwares\anaconda4\lib\site-packages (from importlib-metadata<8.8.0,>=6.0->opentelemetry-api~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (3.23.1)
Requirement already satisfied: wsproto in d:\softwares\anaconda4\lib\site-packages (from simple-websocket>=0.10.0->python-engineio>=4.11.0->python-socketio<6.0.0,>=5.11.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (1.2.0)
Requirement already satisfied: urllib3<3,>=1.21.1 in d:\softwares\anaconda4\lib\site-packages (from requests~=2.7->opentelemetry-exporter-otlp-proto-http==1.41.1->opentelemetry-exporter-otlp~=1.41.0->uptrace<2.0.0,>=1.29.0->chainlit>=1.1.0->-r requirements.txt (line 12)) (2.2.3)

## Use Cases
- Academic presentation research and review
- Business deck analysis and summarization
- Knowledge extraction from slide decks
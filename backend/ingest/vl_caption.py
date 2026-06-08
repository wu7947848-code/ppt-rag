"""VLM caption for sparse PPT pages."""
import base64
import logging
from pathlib import Path

import httpx

from backend import config

logger = logging.getLogger(__name__)


def describe(image_path: str) -> list[str]:
    """Read image, call VLM API, return list of caption strings."""
    try:
        img_bytes = Path(image_path).read_bytes()
        b64 = base64.b64encode(img_bytes).decode("utf-8")

        payload = {
            "model": config.VLM_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                        {
                            "type": "text",
                            "text": (
                                "请描述这张PPT页面图片的内容，重点描述图表、流程图、架构图、"
                                "数据表中的关键信息，不要描述视觉风格"
                            ),
                        },
                    ],
                }
            ],
            "max_tokens": 512,
        }

        headers = {"Content-Type": "application/json"}
        if config.VLM_API_KEY:
            headers["Authorization"] = f"Bearer {config.VLM_API_KEY}"

        with httpx.Client(timeout=30) as client:
            resp = client.post(config.VLM_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        caption = data["choices"][0]["message"]["content"].strip()
        return [caption] if caption else []

    except Exception as e:
        logger.warning("VLM caption failed for %s: %s", image_path, e)
        return []

from pydantic import BaseModel
from typing import List, Dict


class ChartData(BaseModel):
    chart_type: str
    title: str
    categories: List[str]
    series: List[Dict]
    nl_description: str


class Page(BaseModel):
    doc_id: str
    filename: str
    page_num: int
    title: str
    text: str
    tables_md: List[str]
    chart_data: List[ChartData]
    chart_nl: str
    image_captions: List[str]
    ocr_texts: List[str]
    thumbnail_path: str
    is_divider: bool
    has_chart: bool
    has_table: bool
    has_image: bool
    word_count: int

    @property
    def full_text(self) -> str:
        parts = []
        if self.title:
            parts.append(f"【标题】{self.title}")
        if self.text:
            parts.append(self.text)
        for t in self.tables_md:
            parts.append(t)
        if self.chart_nl:
            parts.append(self.chart_nl)
        for cap in self.image_captions:
            parts.append(cap)
        for ocr in self.ocr_texts:
            parts.append(ocr)
        return "\n".join(parts)

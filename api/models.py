from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer


class NoticiaOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    text: Optional[str] = None
    link: Optional[str] = None
    published_date: Optional[str] = None
    category: Optional[str] = None
    source_url: Optional[str] = None
    collected_at: Optional[str] = None

    @field_serializer("id")
    def serialize_id(self, value, _info):
        if value is None:
            return None
        return str(value)


class StatsOut(BaseModel):
    total: int
    unique_authors: int
    unique_categories: int
    last_collected_at: Optional[str] = None

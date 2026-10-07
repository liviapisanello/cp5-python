from pydantic import BaseModel
from typing import Optional

class BookOut(BaseModel):
    id: Optional[str] = None
    title: str
    price: float
    rating: int
    availability: bool
    category: str
    image_url: Optional[str] = None
    url: Optional[str] = None

class StatsOut(BaseModel):
    total: int
    total_categorias: int
    media_preco: float
    total_disponivel: int
    media_rating: float

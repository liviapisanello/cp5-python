from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_collection
from models import NoticiaOut, StatsOut  # noqa: F401 — imported so callers can verify

app = FastAPI(title="TechTudo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _doc_to_dict(doc: dict) -> dict:
    """Convert a MongoDB document to a JSON-serialisable dict."""
    doc["_id"] = str(doc["_id"])
    return doc


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/")
def root():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Noticias — static sub-routes MUST come before the /{id} parameterised route
# ---------------------------------------------------------------------------


@app.get("/noticias/stats", response_model=StatsOut)
def get_stats():
    collection = get_collection()
    total = collection.count_documents({})

    unique_authors = len(collection.distinct("author"))
    unique_categories = len(collection.distinct("category"))

    # Find the most recent collected_at value
    last_doc = collection.find_one(
        {"collected_at": {"$exists": True, "$ne": None}},
        sort=[("collected_at", -1)],
        projection={"collected_at": 1},
    )
    last_collected_at = last_doc["collected_at"] if last_doc else None

    return StatsOut(
        total=total,
        unique_authors=unique_authors,
        unique_categories=unique_categories,
        last_collected_at=last_collected_at,
    )


@app.get("/noticias/categorias")
def get_categorias():
    collection = get_collection()
    values = collection.distinct("category")
    return sorted(v for v in values if v)


@app.get("/noticias/autores")
def get_autores():
    collection = get_collection()
    values = collection.distinct("author")
    return sorted(v for v in values if v)


@app.get("/noticias")
def list_noticias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    categoria: Optional[str] = Query(None),
    autor: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
):
    collection = get_collection()

    query_filter: dict = {}
    if busca:
        query_filter["title"] = {"$regex": busca, "$options": "i"}
    if categoria:
        query_filter["category"] = categoria
    if autor:
        query_filter["author"] = autor

    total = collection.count_documents(query_filter)
    cursor = collection.find(query_filter).skip((page - 1) * size).limit(size)
    items = [_doc_to_dict(doc) for doc in cursor]

    return {"total": total, "page": page, "size": size, "items": items}


@app.get("/noticias/{id}")
def get_noticia(id: str):
    try:
        oid = ObjectId(id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="ID inválido")

    collection = get_collection()
    doc = collection.find_one({"_id": oid})
    if doc is None:
        raise HTTPException(status_code=404, detail="Notícia não encontrada")

    return _doc_to_dict(doc)

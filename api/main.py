from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from typing import Optional
from database import get_db
from models import BookOut, StatsOut

app = FastAPI(title="Books API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok", "service": "books-api"}

@app.get("/livros")
def list_livros(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=500),
    categoria: Optional[str] = None,
    disponivel: Optional[bool] = None,
    rating_min: Optional[int] = Query(None, ge=1, le=5),
    busca: Optional[str] = None,
    preco_max: Optional[float] = None,
):
    db = get_db()
    col = db["livros"]
    query = {}
    if categoria:
        query["category"] = categoria
    if disponivel is not None:
        query["availability"] = disponivel
    if rating_min is not None:
        query["rating"] = {"$gte": rating_min}
    if busca:
        query["title"] = {"$regex": busca, "$options": "i"}
    if preco_max is not None:
        query["price"] = {"$lte": preco_max}
    skip = (page - 1) * size
    total = col.count_documents(query)
    docs = list(col.find(query, {"_id": 1, "title": 1, "price": 1, "rating": 1,
                                 "availability": 1, "category": 1, "image_url": 1, "url": 1})
               .skip(skip).limit(size))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"total": total, "page": page, "size": size, "items": docs}

@app.get("/livros/stats")
def get_stats():
    db = get_db()
    col = db["livros"]
    total = col.count_documents({})
    total_disponivel = col.count_documents({"availability": True})
    pipeline_cats = [{"$group": {"_id": "$category"}}, {"$count": "total"}]
    cats_result = list(col.aggregate(pipeline_cats))
    total_categorias = cats_result[0]["total"] if cats_result else 0
    pipeline_media = [{"$group": {"_id": None, "media_preco": {"$avg": "$price"}, "media_rating": {"$avg": "$rating"}}}]
    media_result = list(col.aggregate(pipeline_media))
    media_preco = round(media_result[0]["media_preco"], 2) if media_result else 0.0
    media_rating = round(media_result[0]["media_rating"], 2) if media_result else 0.0
    return {
        "total": total,
        "total_categorias": total_categorias,
        "media_preco": media_preco,
        "total_disponivel": total_disponivel,
        "media_rating": media_rating,
    }

@app.get("/livros/categorias")
def get_categorias():
    db = get_db()
    categorias = db["livros"].distinct("category")
    return sorted(categorias)

@app.get("/livros/charts/por-categoria")
def chart_por_categoria():
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": "$category",
            "total": {"$sum": 1},
            "media_preco": {"$avg": "$price"}
        }},
        {"$project": {
            "_id": 0,
            "categoria": "$_id",
            "total": 1,
            "media_preco": {"$round": ["$media_preco", 2]}
        }},
        {"$sort": {"total": -1}}
    ]
    return list(db["livros"].aggregate(pipeline))

@app.get("/livros/charts/distribuicao-preco")
def chart_distribuicao_preco():
    db = get_db()
    faixas = [
        {"label": "£0-10",  "min": 0,  "max": 10},
        {"label": "£10-20", "min": 10, "max": 20},
        {"label": "£20-30", "min": 20, "max": 30},
        {"label": "£30-40", "min": 30, "max": 40},
        {"label": "£40-50", "min": 40, "max": 50},
        {"label": "£50+",   "min": 50, "max": 99999},
    ]
    result = []
    for f in faixas:
        count = db["livros"].count_documents({"price": {"$gte": f["min"], "$lt": f["max"]}})
        result.append({"faixa": f["label"], "total": count})
    return result

@app.get("/livros/charts/por-rating")
def chart_por_rating():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$rating", "total": {"$sum": 1}}},
        {"$project": {"_id": 0, "rating": "$_id", "total": 1}},
        {"$sort": {"rating": 1}}
    ]
    return list(db["livros"].aggregate(pipeline))

@app.get("/livros/charts/top-caros")
def chart_top_caros():
    db = get_db()
    docs = list(db["livros"].find(
        {},
        {"_id": 0, "title": 1, "price": 1, "category": 1}
    ).sort("price", -1).limit(10))
    return docs

@app.get("/livros/{id}")
def get_livro(id: str):
    db = get_db()
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    doc = db["livros"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    doc["id"] = str(doc.pop("_id"))
    return doc

# Books Dashboard — Plataforma de Coleta e Análise de Livros

## Integrantes

Lívia Laur – RM: 569017

Rafael Dias – RM: 570504

Lara Beatriz – RM: 572589

Gustavo Inoue – RM: 570549

Luca Baccari – RM: 569807

## Descrição

Plataforma de coleta e análise de livros do site [books.toscrape.com](http://books.toscrape.com).

O sistema realiza o fluxo completo:

```
Site (books.toscrape.com) → Web Crawler (Scrapy) → MongoDB → FastAPI → Dashboard
```

Os dados são coletados automaticamente (1000 livros, 50 categorias), armazenados em MongoDB, disponibilizados via API REST e visualizados em um dashboard web interativo com gráficos premium.

---

## Estrutura do Projeto

```
cp5-python/
├── webcrawler/              # Projeto Scrapy
│   ├── scrapy.cfg
│   └── games/
│       ├── items.py         # BookItem — campos coletados
│       ├── pipelines.py     # Pipeline MongoDB (upsert por upc)
│       ├── settings.py      # Configurações do Scrapy
│       └── spiders/
│           └── Tecnoblog.py # BooksSpider (books.toscrape.com)
├── api/                     # API FastAPI
│   ├── database.py          # Conexão MongoDB
│   ├── models.py            # Modelos Pydantic (BookOut, StatsOut)
│   ├── main.py              # Endpoints FastAPI
│   └── requirements.txt     # Dependências da API
├── dashboard/
│   └── index.html           # Dashboard dark premium (Bootstrap 5 + Chart.js 4)
├── .env                     # MONGO_URI=mongodb://localhost:27019
├── requirements.txt         # Dependências do crawler
└── README.md
```

---

## Estrutura MongoDB

**Database:** `books_db`
**Collection:** `livros`

| Campo          | Tipo     | Descrição                                     |
| -------------- | -------- | --------------------------------------------- |
| `_id`          | ObjectId | Identificador gerado pelo MongoDB             |
| `title`        | string   | Título do livro                               |
| `price`        | float    | Preço em libras (£)                           |
| `rating`       | int      | Avaliação de 1 a 5 estrelas                   |
| `availability` | bool     | `true` se em estoque, `false` se esgotado     |
| `category`     | string   | Categoria (ex: Mystery, Fiction, Travel…)     |
| `description`  | string   | Sinopse do livro                              |
| `upc`          | string   | Código único do livro (chave de deduplicação) |
| `num_reviews`  | int      | Número de avaliações                          |
| `image_url`    | string   | URL da capa do livro                          |
| `url`          | string   | URL da página do livro no site                |
| `collected_at` | datetime | Data/hora da coleta (UTC)                     |

Índice único em `upc` — evita registros duplicados em novas coletas.

---

## Instalação

### Pré-requisitos

- Python 3.10+
- MongoDB rodando em `localhost:27019`

### Instalar dependências

```bash
# Dependências do crawler
pip install -r requirements.txt

# Dependências da API
pip install -r api/requirements.txt
```

---

## Execução do Crawler

```bash
cd webcrawler
../.venv/bin/scrapy crawl books
```

O spider percorre todas as 50 páginas de listagem (1000 livros) e faz upsert por `upc` no MongoDB.

---

## Execução da API

```bash
cd api
uvicorn main:app --reload
```

Acesse a documentação interativa em: <http://localhost:8000/docs>

---

## Execução do Dashboard

```bash
python3 -m http.server 3000 --directory dashboard
```

Acesse o dashboard em: <http://localhost:3000>

> O dashboard consome a API em `http://localhost:8000`. Certifique-se de que a API está rodando antes de abrir o dashboard.

---

## Endpoints da API

### `GET /`

Verificação de saúde da API.

**Response:**

```json
{ "status": "ok", "service": "books-api" }
```

---

### `GET /livros`

Lista livros com paginação e filtros opcionais.

**Query params:**

| Param        | Tipo   | Padrão | Descrição                                   |
| ------------ | ------ | ------ | ------------------------------------------- |
| `page`       | int    | 1      | Número da página                            |
| `size`       | int    | 20     | Itens por página (máx. 500)                 |
| `busca`      | string | —      | Filtro por título (regex, case-insensitive) |
| `categoria`  | string | —      | Filtro exato por categoria                  |
| `rating_min` | int    | —      | Rating mínimo (1–5)                         |
| `preco_max`  | float  | —      | Preço máximo em £                           |
| `disponivel` | bool   | —      | Se `true`, retorna apenas livros em estoque |

**Response:**

```json
{
  "total": 1000,
  "page": 1,
  "size": 20,
  "items": [
    {
      "id": "...",
      "title": "...",
      "price": 12.99,
      "rating": 4,
      "availability": true,
      "category": "Mystery",
      "image_url": "...",
      "url": "..."
    }
  ]
}
```

---

### `GET /livros/stats`

Retorna estatísticas gerais da collection.

**Response:**

```json
{
  "total": 1000,
  "total_categorias": 50,
  "media_preco": 35.07,
  "total_disponivel": 980,
  "media_rating": 2.85
}
```

---

### `GET /livros/categorias`

Lista todos os valores distintos de categoria em ordem alfabética.

**Response:**

```json
["Academic", "Add a comment", "Adventure", "Art", "Autobiography", "..."]
```

---

### `GET /livros/charts/por-categoria`

Agrupamento de livros por categoria, ordenado por volume decrescente.

**Response:**

```json
[{ "categoria": "Mystery", "total": 32, "media_preco": 27.45 }, ...]
```

---

### `GET /livros/charts/distribuicao-preco`

Distribuição de livros por faixa de preço em £.

**Response:**

```json
[
  { "faixa": "£0-10", "total": 120 },
  { "faixa": "£10-20", "total": 230 },
  { "faixa": "£20-30", "total": 310 },
  { "faixa": "£30-40", "total": 180 },
  { "faixa": "£40-50", "total": 100 },
  { "faixa": "£50+", "total": 60 }
]
```

---

### `GET /livros/charts/por-rating`

Contagem de livros por nota de 1 a 5 estrelas.

**Response:**

```json
[
  { "rating": 1, "total": 180 },
  { "rating": 2, "total": 200 },
  { "rating": 3, "total": 210 },
  { "rating": 4, "total": 190 },
  { "rating": 5, "total": 220 }
]
```

---

### `GET /livros/charts/top-caros`

Top 10 livros mais caros.

**Response:**

```json
[{ "title": "...", "price": 59.99, "category": "Art" }, ...]
```

---

### `GET /livros/{id}`

Retorna um livro pelo seu `_id` MongoDB.

**Response (200):**

```json
{
  "id": "6748a1c3f2e1b4d5e6f70001",
  "title": "A Light in the Attic",
  "price": 51.77,
  "rating": 3,
  "availability": true,
  "category": "Poetry",
  "description": "...",
  "upc": "a897fe39b1053632",
  "num_reviews": 0,
  "image_url": "http://books.toscrape.com/media/cache/...",
  "url": "http://books.toscrape.com/catalogue/...",
  "collected_at": "2024-11-20T09:00:00"
}
```

**Response (404):**

```json
{ "detail": "Livro não encontrado" }
```

---

## Fluxo Completo

```
Site (books.toscrape.com)
        │
        ▼
Web Crawler (Scrapy)
  └─ spider: BooksSpider (name="books")
  └─ pipeline: MongoPipeline (upsert por upc)
        │
        ▼
MongoDB (localhost:27019)
  └─ database: books_db
  └─ collection: livros
        │
        ▼
FastAPI (localhost:8000)
  └─ GET /livros
  └─ GET /livros/stats
  └─ GET /livros/categorias
  └─ GET /livros/charts/por-categoria
  └─ GET /livros/charts/distribuicao-preco
  └─ GET /livros/charts/por-rating
  └─ GET /livros/charts/top-caros
  └─ GET /livros/{id}
        │
        ▼
Dashboard (localhost:3000)
  └─ KPIs, 4 gráficos Chart.js 4, filtros e tabela paginada
```

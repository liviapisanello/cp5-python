# TechTudo Jogos — Plataforma de Coleta e Análise de Dados

## Descrição

Plataforma de coleta e análise de notícias de jogos do site [techtudo.com.br](https://www.techtudo.com.br/jogos/).

O sistema realiza o fluxo completo:

```
Site (techtudo.com.br) → Web Crawler (Scrapy) → MongoDB → FastAPI → Dashboard
```

Os dados são coletados automaticamente, armazenados em MongoDB, disponibilizados via API REST e visualizados em um dashboard web interativo.

---

## Estrutura do Projeto

```
cp5-python/
├── webcrawler/              # Projeto Scrapy
│   ├── scrapy.cfg
│   └── games/
│       ├── items.py         # Definição dos campos coletados
│       ├── pipelines.py     # Pipeline MongoDB (upsert por link)
│       ├── settings.py      # Configurações do Scrapy
│       └── spiders/
│           └── Tecnoblog.py # Spider principal
├── api/                     # API FastAPI
│   ├── database.py          # Conexão MongoDB
│   ├── models.py            # Modelos Pydantic v2
│   ├── main.py              # Endpoints FastAPI
│   └── requirements.txt     # Dependências da API
├── dashboard/
│   └── index.html           # Dashboard HTML/CSS/JS (single-file)
├── requirements.txt         # Dependências do crawler
└── README.md
```

---

## Estrutura MongoDB

**Database:** `techtudo`  
**Collection:** `noticias`

| Campo            | Tipo     | Descrição                                      |
| ---------------- | -------- | ---------------------------------------------- |
| `_id`            | ObjectId | Identificador gerado pelo MongoDB              |
| `title`          | string   | Título da notícia                              |
| `author`         | string   | Nome do autor                                  |
| `text`           | string   | Texto/resumo do conteúdo                       |
| `link`           | string   | URL canônica do artigo (chave de deduplicação) |
| `published_date` | string   | Data/hora de publicação (ISO 8601)             |
| `category`       | string   | Categoria extraída da URL (ex: `jogos`)        |
| `source_url`     | string   | URL da página de origem usada pelo crawler     |
| `collected_at`   | string   | Data/hora da coleta (UTC, ISO 8601)            |

Índice único em `link` — evita registros duplicados em novas coletas.

---

## Instalação

### Pré-requisitos

- Python 3.10+
- MongoDB rodando em `localhost:27017`

### Instalar dependências

```bash
# Criar e ativar ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Dependências do crawler
pip install -r requirements.txt

# Dependências da API
pip install -r api/requirements.txt
```

---

## Execução do Crawler

```bash
cd webcrawler
scrapy crawl TechTudoJogos
```

Os dados são automaticamente armazenados na collection `noticias` do MongoDB. Novas execuções fazem upsert (não duplicam registros já coletados).

---

## Execução da API

```bash
cd api
uvicorn main:app --reload --port 8000
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
{ "status": "ok" }
```

---

### `GET /noticias`

Lista notícias com paginação e filtros opcionais.

**Query params:**

| Param       | Tipo   | Padrão | Descrição                             |
| ----------- | ------ | ------ | ------------------------------------- |
| `page`      | int    | 1      | Número da página                      |
| `size`      | int    | 20     | Itens por página (máx. 100)           |
| `busca`     | string | —      | Filtro por título (regex, insensível) |
| `categoria` | string | —      | Filtro exato por categoria            |
| `autor`     | string | —      | Filtro exato por autor                |

**Request:**

```
GET /noticias?page=1&size=2&categoria=jogos
```

**Response:**

```json
{
  "total": 142,
  "page": 1,
  "size": 2,
  "items": [
    {
      "_id": "6748a1c3f2e1b4d5e6f70001",
      "title": "Novo jogo de RPG chega ao PC em 2025",
      "author": "João Silva",
      "link": "https://www.techtudo.com.br/jogos/2024/10/novo-jogo-rpg.html",
      "published_date": "2024-10-15T14:30:00+00:00",
      "category": "jogos",
      "collected_at": "2024-11-20T09:00:00+00:00"
    }
  ]
}
```

---

### `GET /noticias/stats`

Retorna estatísticas gerais da collection.

**Request:**

```
GET /noticias/stats
```

**Response:**

```json
{
  "total": 142,
  "unique_authors": 18,
  "unique_categories": 4,
  "last_collected_at": "2024-11-20T09:00:00+00:00"
}
```

---

### `GET /noticias/categorias`

Lista todos os valores distintos de categoria.

**Request:**

```
GET /noticias/categorias
```

**Response:**

```json
["jogos", "listas", "noticias", "reviews"]
```

---

### `GET /noticias/autores`

Lista todos os valores distintos de autor.

**Request:**

```
GET /noticias/autores
```

**Response:**

```json
["Ana Costa", "Carlos Mendes", "João Silva"]
```

---

### `GET /noticias/{id}`

Retorna uma notícia pelo seu `_id` MongoDB.

**Request:**

```
GET /noticias/6748a1c3f2e1b4d5e6f70001
```

**Response (200):**

```json
{
  "_id": "6748a1c3f2e1b4d5e6f70001",
  "title": "Novo jogo de RPG chega ao PC em 2025",
  "author": "João Silva",
  "text": "O esperado título de RPG foi confirmado para 2025...",
  "link": "https://www.techtudo.com.br/jogos/2024/10/novo-jogo-rpg.html",
  "published_date": "2024-10-15T14:30:00+00:00",
  "category": "jogos",
  "source_url": "https://busca.techtudo.com.br/api/...",
  "collected_at": "2024-11-20T09:00:00+00:00"
}
```

**Response (404):**

```json
{ "detail": "Notícia não encontrada" }
```

---

## Fluxo Completo

```
Site (techtudo.com.br)
        │
        ▼
Web Crawler (Scrapy)
  └─ spider: TechTudoJogos
  └─ pipeline: MongoPipeline (upsert por link)
        │
        ▼
MongoDB (localhost:27017)
  └─ database: techtudo
  └─ collection: noticias
        │
        ▼
FastAPI (localhost:8000)
  └─ GET /noticias
  └─ GET /noticias/stats
  └─ GET /noticias/categorias
  └─ GET /noticias/autores
  └─ GET /noticias/{id}
        │
        ▼
Dashboard (localhost:3000)
  └─ KPIs, gráficos, filtros e tabela paginada
```

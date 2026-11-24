<p align="center">
  <img src="assets/banner.svg" alt="Workout API Async Pro — High-Concurrency CrossFit Engine" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11%2B%20Async-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Async" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0%20Async-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0 Async" />
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic v2" />
  <img src="https://img.shields.io/badge/FastAPI--Pagination-LimitOffsetPage-7C3AED?style=for-the-badge" alt="FastAPI Pagination" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready" />
  <img src="https://img.shields.io/badge/Pytest-Async%20100%25%20Pass-00C853?style=for-the-badge&logo=pytest&logoColor=white" alt="Tested" />
</p>

---

## Visão Geral

**Workout API Async Pro** é uma plataforma REST assíncrona de alta concorrência para gestão de competições de **CrossFit** (Atletas, Categorias e Centros de Treinamento), desenvolvida para o desafio **"Desenvolvendo uma API Assíncrona com FastAPI"** do **Bootcamp Santander 2025 Python Back-End (DIO)**.

O projeto cumpre **100% dos requisitos obrigatórios da DIO** e evolui o conceito original do `workout_api` para uma arquitetura limpa, resiliente, observável e **Plug-and-Play**: roda com **1 único comando em qualquer computador** usando **SQLite Assíncrono (`aiosqlite`)** e **Auto-Seed Inteligente**, mantendo **PostgreSQL Assíncrono (`asyncpg`) + Alembic + Docker Compose** prontos para produção.

### Checklist dos Requisitos da DIO Atendidos 100%

- [x] **Query Parameters em `GET /atletas/`**: filtros opcionais por `nome` (busca parcial/exata *case-insensitive*) e `cpf` (busca exata com sanitização automática de máscara).
- [x] **Response Customizado em `GET /atletas/` (`AtletaOutResumo`)**: retorna estritamente `nome`, `centro_treinamento` e `categoria` na listagem geral, preservando o detalhamento completo (`pk_id`, `id` UUID, `cpf`, `idade`, `peso`, `altura`, `sexo`, `created_at`) em `GET /atletas/{id}`.
- [x] **Tratamento de Integridade (`sqlalchemy.exc.IntegrityError` -> HTTP `303 See Other`)** em **todos os módulos**:
  - Atleta duplicado: `"Já existe um atleta cadastrado com o cpf: {cpf}"`
  - Categoria duplicada: `"Já existe uma categoria cadastrada com o nome: {nome}"`
  - Centro de treinamento duplicado: `"Já existe um centro de treinamento cadastrado com o nome: {nome}"`
- [x] **Paginação Oficial com `fastapi-pagination`**: `add_pagination(app)` e `LimitOffsetPage` (`limit` e `offset`) nos endpoints `GET /atletas/`, `GET /categorias/` e `GET /centros_treinamento/`.
- [x] **Observabilidade & Arquitetura Sênior**: middlewares injetando `X-Request-ID` e `X-Process-Time-Ms` em todas as respostas HTTP, `Health Check` com validação de conectividade de banco, Dual-Database Zero-Config, Auto-Seed idempotente e suíte de testes E2E assíncronos.

---

## Arquitetura Assíncrona

```mermaid
flowchart LR
    Client["Client / Swagger UI / HTTPX"] --> MW["Observability Middleware<br/>(X-Request-ID + X-Process-Time-Ms)"]
    MW --> App["FastAPI ASGI App<br/>(lifespan + add_pagination + IntegrityError Handler)"]
    App --> Routers["Domain Controllers<br/>/atletas · /categorias · /centros_treinamento"]
    Routers --> Services["Async Domain Services<br/>(Validation · Filters · 303 Integrity Handling)"]
    Services --> ORM["SQLAlchemy 2.0 AsyncSession<br/>(selectinload + Portable UUID)"]
    ORM --> SQLite[("SQLite Async<br/>aiosqlite (Zero-Config Default)")]
    ORM -. "DATABASE_URL=postgresql+asyncpg://..." .-> Postgres[("PostgreSQL 16<br/>asyncpg + Alembic (Production)")]
```

---

## Modelagem de Dados (Diagrama ER)

```mermaid
erDiagram
    CATEGORIAS ||--o{ ATLETAS : "classifica (1:N)"
    CENTROS_TREINAMENTO ||--o{ ATLETAS : "vincula (1:N)"

    CATEGORIAS {
        int pk_id PK
        uuid id UK
        varchar nome UK "Scale, RX, Elite, Master..."
    }

    CENTROS_TREINAMENTO {
        int pk_id PK
        uuid id UK
        varchar nome UK "CT Iron Box, CT Alpha Cross..."
        varchar endereco
        varchar proprietario
    }

    ATLETAS {
        int pk_id PK
        uuid id UK
        varchar nome
        varchar cpf UK "11 dígitos sanitizados"
        int idade
        float peso
        float altura
        char sexo "M / F / O"
        timestamptz created_at
        int categoria_id FK
        int centro_treinamento_id FK
    }
```

---

## Mapa Completo de Endpoints REST

| Método | Rota | Query Params | Status Codes | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | — | `200` | Metadados do serviço e links rápidos da API |
| `GET` | `/health` | — | `200` | Health check em tempo real com `SELECT 1` no banco ativo |
| `POST` | `/categorias/` | — | `201`, `303`, `422` | Cria uma nova categoria (`303` se nome já existir) |
| `GET` | `/categorias/` | `limit`, `offset` | `200` | Lista categorias paginadas (`LimitOffsetPage`) |
| `GET` | `/categorias/{id}` | — | `200`, `404` | Consulta uma categoria específica pelo `id` (UUID) |
| `POST` | `/centros_treinamento/` | — | `201`, `303`, `422` | Cria um novo centro de treinamento (`303` se nome já existir) |
| `GET` | `/centros_treinamento/` | `limit`, `offset` | `200` | Lista centros de treinamento paginados (`LimitOffsetPage`) |
| `GET` | `/centros_treinamento/{id}` | — | `200`, `404` | Consulta um centro de treinamento pelo `id` (UUID) |
| `POST` | `/atletas/` | — | `201`, `303`, `400`, `422` | Cadastra atleta (`303` se CPF duplicado; `400` se CT/Categoria inexistente) |
| `GET` | `/atletas/` | `nome`, `cpf`, `limit`, `offset` | `200` | Lista atletas com **response resumido** (`nome`, `centro_treinamento`, `categoria`), filtros e paginação |
| `GET` | `/atletas/{id}` | — | `200`, `404` | Consulta detalhes completos do atleta (`pk_id`, `id`, `cpf`, biometria, timestamps) |
| `PATCH` | `/atletas/{id}` | — | `200`, `303`, `400`, `404` | Atualização parcial de dados do atleta (`303` se novo CPF já existir) |
| `DELETE` | `/atletas/{id}` | — | `204`, `404` | Remove um atleta pelo `id` (UUID) |

---

## Guia de Instalação "Zero Dor de Cabeça" (3 Passos)

> **Não precisa instalar Docker nem PostgreSQL para testar!** O projeto sobe instantaneamente com **SQLite Assíncrono** e popula automaticamente 4 categorias, 3 centros de treinamento e 6 atletas de CrossFit na primeira inicialização.

### Passo 1 — Clone o repositório

```bash
git clone https://github.com/lcszero44-cell/workout-api-async-pro.git
cd workout-api-async-pro
```

### Passo 2 — Crie o ambiente virtual e instale as dependências

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Passo 3 — Inicie o servidor com 1 comando

```bash
python run.py
```

*(No Windows, você também pode dar duplo clique em **`start.bat`** — ele cria a `.venv`, instala as dependências e sobe o servidor automaticamente!)*

Assim que iniciar, você verá o banner no terminal com os links diretos:
- **Swagger UI Interativo:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Health Check:** http://127.0.0.1:8000/health

---

## Como Testar Cada Requisito da DIO no Swagger UI (`/docs`)

Ao abrir **`http://127.0.0.1:8000/docs`**, o **Auto-Seed** já terá criado dados reais prontos para teste imediato:

1. **Testar Response Customizado + Paginação (`limit` e `offset`)**
   - Expanda **`GET /atletas/`** -> clique em **Try it out**.
   - Preencha `limit = 2` e `offset = 0` -> clique em **Execute**.
   - Observe que cada item retorna **exclusivamente** `nome`, `centro_treinamento` e `categoria`, encapsulados em `items`, `total`, `limit`, `offset`.

2. **Testar Query Parameters (`nome` e `cpf`)**
   - Em **`GET /atletas/`**, digite `nome = lucas` (case-insensitive parcial) ou `cpf = 111.222.333-44` (com ou sem máscara) e execute.

3. **Testar Exceção `IntegrityError` -> HTTP `303 See Other`**
   - Expanda **`POST /atletas/`** -> clique em **Try it out** e envie um atleta com o CPF já cadastrado pelo Auto-Seed (`"11122233344"`):
   ```json
   {
     "nome": "Teste Duplicidade",
     "cpf": "11122233344",
     "idade": 28,
     "peso": 80.0,
     "altura": 1.80,
     "sexo": "M",
     "categoria": { "nome": "RX" },
     "centro_treinamento": { "nome": "CT Iron Box" }
   }
   ```
   - A API retornará exatamente **HTTP `303 See Other`** com o corpo:
   ```json
   {
     "detail": "Já existe um atleta cadastrado com o cpf: 11122233344"
   }
   ```
   - Faça o mesmo teste enviando `"Scale"` em **`POST /categorias/`** ou `"CT Iron Box"` em **`POST /centros_treinamento/`** para validar os tratamentos `303` em todos os módulos.

4. **Verificar Observabilidade nos Headers HTTP**
   - Em qualquer resposta no Swagger UI, confira na seção **Response headers**:
     - `x-request-id`: UUID único de rastreabilidade da requisição
     - `x-process-time-ms`: latência exata de processamento em milissegundos

---

## Rodando a Suíte de Testes Assíncronos

Os testes utilizam `pytest`, `pytest-asyncio` e `httpx.AsyncClient` contra um banco SQLite assíncrono em memória totalmente isolado por teste:

```bash
pytest
```

---

<details>
<summary><strong>Modo Produção: Rodar com Docker Compose + PostgreSQL 16 + Alembic</strong></summary>

Para executar a API conectada ao **PostgreSQL 16** com driver assíncrono **`asyncpg`** e migrations automáticas via **Alembic**:

1. Suba o banco e a API com um único comando:
   ```bash
   docker compose up --build
   ```
   O container da API aguarda o `healthcheck` do PostgreSQL, executa `alembic upgrade head` automaticamente e inicia o servidor Uvicorn na porta `8000`.

2. Caso prefira rodar a API localmente apontando para um PostgreSQL externo, crie um arquivo `.env` baseado no `.env.example`:
   ```env
   DATABASE_URL="postgresql+asyncpg://workout:workout@localhost:5432/workout"
   AUTO_SEED=true
   ```
   E aplique as migrations manualmente:
   ```bash
   alembic upgrade head
   python run.py
   ```

</details>

---

## Estrutura de Diretórios

```text
workout-api-async-pro/
├── alembic/                      # Migrations assíncronas (dual-DB SQLite / PostgreSQL)
│   ├── versions/
│   │   └── 0001_initial_schema.py
│   └── env.py
├── assets/
│   └── banner.svg                # Banner hero 3D vetorial isométrico
├── src/
│   ├── atleta/                   # Domínio Atleta (models, schemas, service, controller)
│   ├── categorias/               # Domínio Categorias (models, schemas, service, controller)
│   ├── centro_treinamento/       # Domínio Centros de Treinamento
│   ├── configs/                  # Settings (Pydantic v2), Database Dual-Engine e Auto-Seed
│   ├── contrib/                  # BaseModel UUID, Schemas, Dependencies, Exceptions 303 & Middleware
│   ├── routers.py                # Agregador central de rotas
│   └── main.py                   # App FastAPI, lifespan, add_pagination e /health
├── tests/
│   ├── conftest.py               # Fixtures assíncronas com banco isolado em memória
│   └── test_workout_api.py       # Suíte E2E cobrindo 100% das regras de negócio e DIO
├── docker-compose.yml            # Stack de produção (PostgreSQL 16 + API + Alembic)
├── Dockerfile                    # Imagem enxuta Python 3.12
├── run.py                        # Inicializador plug-and-play com banner interativo
├── start.bat                     # Atalho de 1 clique para Windows
└── requirements.txt
```

---

<p align="center">
  Desenvolvido com arquitetura limpa e alta performance para o <strong>Bootcamp Santander 2025 Python Back-End (DIO)</strong>.
</p>

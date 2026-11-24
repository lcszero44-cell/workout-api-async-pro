from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.seed import seed_database

# ==============================================================================
# Helpers
# ==============================================================================


async def _create_categoria(client: AsyncClient, nome: str = "Scale") -> dict:
    response = await client.post("/categorias/", json={"nome": nome})
    assert response.status_code == 201, response.text
    return response.json()


async def _create_ct(
    client: AsyncClient,
    nome: str = "CT Iron Box",
    endereco: str = "Av. Paulista, 1500",
    proprietario: str = "Marcos Vinícius",
) -> dict:
    response = await client.post(
        "/centros_treinamento/",
        json={"nome": nome, "endereco": endereco, "proprietario": proprietario},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_atleta(
    client: AsyncClient,
    *,
    nome: str = "Lucas Mendes",
    cpf: str = "12345678901",
    idade: int = 27,
    peso: float = 82.5,
    altura: float = 1.81,
    sexo: str = "M",
    categoria: str = "Scale",
    centro_treinamento: str = "CT Iron Box",
) -> dict:
    response = await client.post(
        "/atletas/",
        json={
            "nome": nome,
            "cpf": cpf,
            "idade": idade,
            "peso": peso,
            "altura": altura,
            "sexo": sexo,
            "categoria": {"nome": categoria},
            "centro_treinamento": {"nome": centro_treinamento},
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


# ==============================================================================
# 1. Observabilidade, Health Check & Auto-Seed
# ==============================================================================


@pytest.mark.asyncio
async def test_health_and_observability_headers(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers
    assert float(response.headers["X-Process-Time-Ms"]) >= 0.0

    # Valida propagação de X-Request-ID customizado
    custom_req_id = "req-crossfit-2025-001"
    resp_custom = await client.get("/", headers={"X-Request-ID": custom_req_id})
    assert resp_custom.status_code == 200
    assert resp_custom.headers["X-Request-ID"] == custom_req_id


@pytest.mark.asyncio
async def test_auto_seed_is_idempotent(client: AsyncClient, db_session: AsyncSession):
    first_run = await seed_database(db_session)
    second_run = await seed_database(db_session)

    assert first_run is True
    assert second_run is False

    resp_cats = await client.get("/categorias/?limit=20&offset=0")
    resp_cts = await client.get("/centros_treinamento/?limit=20&offset=0")
    resp_atletas = await client.get("/atletas/?limit=20&offset=0")

    assert resp_cats.json()["total"] == 4
    assert resp_cts.json()["total"] == 3
    assert resp_atletas.json()["total"] == 6


# ==============================================================================
# 2. Módulo Categorias (CRUD + Paginação + IntegrityError 303)
# ==============================================================================


@pytest.mark.asyncio
async def test_categorias_crud_pagination_and_duplicate_303(client: AsyncClient):
    cat_scale = await _create_categoria(client, "Scale")
    await _create_categoria(client, "RX")
    await _create_categoria(client, "Elite")

    # Consulta por ID
    resp_get = await client.get(f"/categorias/{cat_scale['id']}")
    assert resp_get.status_code == 200
    assert resp_get.json()["nome"] == "Scale"
    assert resp_get.json()["id"] == cat_scale["id"]

    # 404 para ID inexistente
    resp_not_found = await client.get(f"/categorias/{uuid4()}")
    assert resp_not_found.status_code == 404

    # Paginação limit / offset
    resp_page = await client.get("/categorias/?limit=2&offset=1")
    assert resp_page.status_code == 200
    page = resp_page.json()
    assert page["total"] == 3
    assert page["limit"] == 2
    assert page["offset"] == 1
    assert [item["nome"] for item in page["items"]] == ["RX", "Elite"]

    # IntegrityError -> HTTP 303 See Other com mensagem exata
    resp_dup = await client.post("/categorias/", json={"nome": "Scale"})
    assert resp_dup.status_code == 303
    assert resp_dup.json() == {
        "detail": "Já existe uma categoria cadastrada com o nome: Scale"
    }


# ==============================================================================
# 3. Módulo Centros de Treinamento (CRUD + Paginação + IntegrityError 303)
# ==============================================================================


@pytest.mark.asyncio
async def test_centros_treinamento_crud_pagination_and_duplicate_303(client: AsyncClient):
    ct1 = await _create_ct(client, nome="CT Iron Box")
    await _create_ct(client, nome="CT Alpha Cross", endereco="Rua B, 200", proprietario="Camila")
    await _create_ct(client, nome="CT Arena WOD", endereco="Av. C, 300", proprietario="Rafael")

    # Consulta por ID
    resp_get = await client.get(f"/centros_treinamento/{ct1['id']}")
    assert resp_get.status_code == 200
    assert resp_get.json()["nome"] == "CT Iron Box"
    assert resp_get.json()["proprietario"] == "Marcos Vinícius"

    # 404 para ID inexistente
    resp_404 = await client.get(f"/centros_treinamento/{uuid4()}")
    assert resp_404.status_code == 404

    # Paginação limit / offset
    resp_page = await client.get("/centros_treinamento/?limit=1&offset=2")
    assert resp_page.status_code == 200
    page = resp_page.json()
    assert page["total"] == 3
    assert page["limit"] == 1
    assert page["offset"] == 2
    assert len(page["items"]) == 1
    assert page["items"][0]["nome"] == "CT Arena WOD"

    # IntegrityError -> HTTP 303 See Other com mensagem exata
    resp_dup = await client.post(
        "/centros_treinamento/",
        json={
            "nome": "CT Iron Box",
            "endereco": "Outro endereço, 999",
            "proprietario": "Outro Dono",
        },
    )
    assert resp_dup.status_code == 303
    assert resp_dup.json() == {
        "detail": "Já existe um centro de treinamento cadastrado com o nome: CT Iron Box"
    }


# ==============================================================================
# 4. Módulo Atletas (CRUD + Response Customizado + Filtros + Paginação + 303)
# ==============================================================================


@pytest.mark.asyncio
async def test_atletas_custom_response_and_detailed_get(client: AsyncClient):
    await _create_categoria(client, "RX")
    await _create_ct(client, nome="CT Iron Box")

    created = await _create_atleta(
        client,
        nome="Beatriz Almeida",
        cpf="123.456.789-01",
        idade=25,
        peso=61.2,
        altura=1.67,
        sexo="F",
        categoria="RX",
        centro_treinamento="CT Iron Box",
    )

    # Sanitização automática do CPF no cadastro
    assert created["cpf"] == "12345678901"

    # GET /atletas/ deve retornar EXCLUSIVAMENTE AtletaOutResumo (nome, centro_treinamento, categoria)
    resp_list = await client.get("/atletas/")
    assert resp_list.status_code == 200
    items = resp_list.json()["items"]
    assert len(items) == 1
    assert set(items[0].keys()) == {"nome", "centro_treinamento", "categoria"}
    assert items[0] == {
        "nome": "Beatriz Almeida",
        "centro_treinamento": {"nome": "CT Iron Box"},
        "categoria": {"nome": "RX"},
    }

    # GET /atletas/{id} deve retornar os detalhes completos (pk_id, id UUID, cpf, etc.)
    resp_detail = await client.get(f"/atletas/{created['id']}")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    expected_detail_keys = {
        "pk_id",
        "id",
        "nome",
        "cpf",
        "idade",
        "peso",
        "altura",
        "sexo",
        "categoria",
        "centro_treinamento",
        "created_at",
    }
    assert expected_detail_keys.issubset(set(detail.keys()))
    assert detail["id"] == created["id"]
    assert detail["cpf"] == "12345678901"
    assert detail["peso"] == 61.2


@pytest.mark.asyncio
async def test_atletas_query_filters_nome_and_cpf(client: AsyncClient):
    await _create_categoria(client, "Scale")
    await _create_categoria(client, "Elite")
    await _create_ct(client, nome="CT Alpha Cross")

    await _create_atleta(
        client,
        nome="Lucas Mendes",
        cpf="11122233344",
        categoria="Scale",
        centro_treinamento="CT Alpha Cross",
    )
    await _create_atleta(
        client,
        nome="Luciana Ferreira",
        cpf="22233344455",
        sexo="F",
        categoria="Elite",
        centro_treinamento="CT Alpha Cross",
    )
    await _create_atleta(
        client,
        nome="Rafael Souza",
        cpf="33344455566",
        categoria="Elite",
        centro_treinamento="CT Alpha Cross",
    )

    # Filtro por nome parcial case-insensitive
    resp_nome = await client.get("/atletas/?nome=luc")
    assert resp_nome.status_code == 200
    nomes = [item["nome"] for item in resp_nome.json()["items"]]
    assert nomes == ["Lucas Mendes", "Luciana Ferreira"]

    # Filtro por nome exato case-insensitive
    resp_nome_exact = await client.get("/atletas/?nome=RAFAEL SOUZA")
    assert resp_nome_exact.status_code == 200
    assert [item["nome"] for item in resp_nome_exact.json()["items"]] == ["Rafael Souza"]

    # Filtro por CPF exato (apenas dígitos)
    resp_cpf_raw = await client.get("/atletas/?cpf=22233344455")
    assert resp_cpf_raw.status_code == 200
    assert [item["nome"] for item in resp_cpf_raw.json()["items"]] == ["Luciana Ferreira"]

    # Filtro por CPF exato com pontuação (sanitização automática)
    resp_cpf_masked = await client.get("/atletas/?cpf=111.222.333-44")
    assert resp_cpf_masked.status_code == 200
    assert [item["nome"] for item in resp_cpf_masked.json()["items"]] == ["Lucas Mendes"]


@pytest.mark.asyncio
async def test_atletas_pagination_limit_offset(client: AsyncClient):
    await _create_categoria(client, "RX")
    await _create_ct(client, nome="CT Arena WOD")

    for i in range(1, 6):
        await _create_atleta(
            client,
            nome=f"Atleta {i}",
            cpf=f"1000000000{i}",
            categoria="RX",
            centro_treinamento="CT Arena WOD",
        )

    page_1 = (await client.get("/atletas/?limit=2&offset=0")).json()
    page_2 = (await client.get("/atletas/?limit=2&offset=2")).json()
    page_3 = (await client.get("/atletas/?limit=2&offset=4")).json()

    assert page_1["total"] == 5
    assert page_1["limit"] == 2
    assert page_1["offset"] == 0
    assert [a["nome"] for a in page_1["items"]] == ["Atleta 1", "Atleta 2"]

    assert [a["nome"] for a in page_2["items"]] == ["Atleta 3", "Atleta 4"]
    assert [a["nome"] for a in page_3["items"]] == ["Atleta 5"]


@pytest.mark.asyncio
async def test_atletas_duplicate_cpf_returns_303_exact_message(client: AsyncClient):
    await _create_categoria(client, "Scale")
    await _create_ct(client, nome="CT Iron Box")

    await _create_atleta(
        client,
        nome="Primeiro Atleta",
        cpf="98765432100",
        categoria="Scale",
        centro_treinamento="CT Iron Box",
    )

    # Tentativa de duplicidade com CPF sem máscara
    resp_dup = await client.post(
        "/atletas/",
        json={
            "nome": "Segundo Atleta",
            "cpf": "98765432100",
            "idade": 30,
            "peso": 80.0,
            "altura": 1.80,
            "sexo": "M",
            "categoria": {"nome": "Scale"},
            "centro_treinamento": {"nome": "CT Iron Box"},
        },
    )
    assert resp_dup.status_code == 303
    assert resp_dup.json() == {
        "detail": "Já existe um atleta cadastrado com o cpf: 98765432100"
    }

    # Tentativa de duplicidade com CPF mascarado (deve sanitizar e barrar com 303 igual)
    resp_dup_masked = await client.post(
        "/atletas/",
        json={
            "nome": "Terceiro Atleta",
            "cpf": "987.654.321-00",
            "idade": 26,
            "peso": 75.0,
            "altura": 1.75,
            "sexo": "M",
            "categoria": {"nome": "Scale"},
            "centro_treinamento": {"nome": "CT Iron Box"},
        },
    )
    assert resp_dup_masked.status_code == 303
    assert resp_dup_masked.json() == {
        "detail": "Já existe um atleta cadastrado com o cpf: 98765432100"
    }


@pytest.mark.asyncio
async def test_atletas_patch_delete_and_validation_errors(client: AsyncClient):
    await _create_categoria(client, "Scale")
    await _create_categoria(client, "Elite")
    await _create_ct(client, nome="CT Iron Box")

    atleta_1 = await _create_atleta(
        client,
        nome="Carlos Eduardo",
        cpf="55511122233",
        categoria="Scale",
        centro_treinamento="CT Iron Box",
    )
    atleta_2 = await _create_atleta(
        client,
        nome="Juliana Lima",
        cpf="66611122233",
        sexo="F",
        categoria="Scale",
        centro_treinamento="CT Iron Box",
    )

    # PATCH atualizando nome, peso e categoria
    resp_patch = await client.patch(
        f"/atletas/{atleta_1['id']}",
        json={"nome": "Carlos E. Silva", "peso": 85.0, "categoria": {"nome": "Elite"}},
    )
    assert resp_patch.status_code == 200
    patched = resp_patch.json()
    assert patched["nome"] == "Carlos E. Silva"
    assert patched["peso"] == 85.0
    assert patched["categoria"]["nome"] == "Elite"

    # PATCH tentando assumir CPF já pertencente a outro atleta -> 303
    resp_patch_dup = await client.patch(
        f"/atletas/{atleta_2['id']}",
        json={"cpf": "55511122233"},
    )
    assert resp_patch_dup.status_code == 303
    assert resp_patch_dup.json() == {
        "detail": "Já existe um atleta cadastrado com o cpf: 55511122233"
    }

    # POST com categoria inexistente -> 400
    resp_bad_cat = await client.post(
        "/atletas/",
        json={
            "nome": "Atleta Sem Cat",
            "cpf": "77711122233",
            "idade": 24,
            "peso": 70.0,
            "altura": 1.72,
            "sexo": "M",
            "categoria": {"nome": "Inexistente"},
            "centro_treinamento": {"nome": "CT Iron Box"},
        },
    )
    assert resp_bad_cat.status_code == 400

    # DELETE -> 204 e subsequente GET -> 404
    resp_del = await client.delete(f"/atletas/{atleta_1['id']}")
    assert resp_del.status_code == 204

    resp_after_del = await client.get(f"/atletas/{atleta_1['id']}")
    assert resp_after_del.status_code == 404

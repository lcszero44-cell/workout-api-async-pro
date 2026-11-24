from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.atleta.models import AtletaModel
from src.categorias.models import CategoriaModel
from src.centro_treinamento.models import CentroTreinamentoModel

SEED_CATEGORIAS = [
    "Scale",
    "RX",
    "Elite",
    "Master",
]

SEED_CENTROS_TREINAMENTO = [
    {
        "nome": "CT Iron Box",
        "endereco": "Av. Paulista, 1500 - Bela Vista, São Paulo/SP",
        "proprietario": "Marcos Vinícius",
    },
    {
        "nome": "CT Alpha Cross",
        "endereco": "Rua Oscar Freire, 820 - Pinheiros, São Paulo/SP",
        "proprietario": "Camila Rocha",
    },
    {
        "nome": "CT Arena WOD",
        "endereco": "Av. das Américas, 3400 - Barra da Tijuca, Rio de Janeiro/RJ",
        "proprietario": "Rafael Cavalcanti",
    },
]

SEED_ATLETAS = [
    {
        "nome": "Lucas Mendes",
        "cpf": "11122233344",
        "idade": 27,
        "peso": 82.5,
        "altura": 1.81,
        "sexo": "M",
        "categoria": "RX",
        "centro_treinamento": "CT Iron Box",
    },
    {
        "nome": "Beatriz Almeida",
        "cpf": "22233344455",
        "idade": 25,
        "peso": 61.2,
        "altura": 1.67,
        "sexo": "F",
        "categoria": "Elite",
        "centro_treinamento": "CT Alpha Cross",
    },
    {
        "nome": "Gabriel Oliveira",
        "cpf": "33344455566",
        "idade": 31,
        "peso": 88.0,
        "altura": 1.84,
        "sexo": "M",
        "categoria": "Scale",
        "centro_treinamento": "CT Arena WOD",
    },
    {
        "nome": "Mariana Costa",
        "cpf": "44455566677",
        "idade": 38,
        "peso": 64.8,
        "altura": 1.70,
        "sexo": "F",
        "categoria": "Master",
        "centro_treinamento": "CT Iron Box",
    },
    {
        "nome": "Thiago Santana",
        "cpf": "55566677788",
        "idade": 29,
        "peso": 79.4,
        "altura": 1.77,
        "sexo": "M",
        "categoria": "Elite",
        "centro_treinamento": "CT Alpha Cross",
    },
    {
        "nome": "Fernanda Ribeiro",
        "cpf": "66677788899",
        "idade": 23,
        "peso": 58.0,
        "altura": 1.63,
        "sexo": "F",
        "categoria": "RX",
        "centro_treinamento": "CT Arena WOD",
    },
]


async def seed_database(session: AsyncSession) -> bool:
    """Popula automaticamente o banco caso esteja vazio (idempotente).

    Retorna True se o seed foi executado e False caso já existissem dados.
    """
    existing_categories = (
        await session.execute(select(func.count()).select_from(CategoriaModel))
    ).scalar_one()

    if existing_categories > 0:
        return False

    categorias_map: dict[str, CategoriaModel] = {}
    for nome in SEED_CATEGORIAS:
        categoria = CategoriaModel(nome=nome)
        session.add(categoria)
        categorias_map[nome] = categoria

    centros_map: dict[str, CentroTreinamentoModel] = {}
    for ct_data in SEED_CENTROS_TREINAMENTO:
        centro = CentroTreinamentoModel(**ct_data)
        session.add(centro)
        centros_map[ct_data["nome"]] = centro

    await session.flush()

    now = datetime.now(timezone.utc)
    for atleta_data in SEED_ATLETAS:
        atleta = AtletaModel(
            nome=atleta_data["nome"],
            cpf=atleta_data["cpf"],
            idade=atleta_data["idade"],
            peso=atleta_data["peso"],
            altura=atleta_data["altura"],
            sexo=atleta_data["sexo"],
            created_at=now,
            categoria_id=categorias_map[atleta_data["categoria"]].pk_id,
            centro_treinamento_id=centros_map[atleta_data["centro_treinamento"]].pk_id,
        )
        session.add(atleta)

    await session.commit()
    return True

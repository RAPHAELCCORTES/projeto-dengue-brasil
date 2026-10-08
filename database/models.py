"""
Modelagem relacional do projeto de análise de dengue no Brasil.

Define a tabela `registros_dengue` via SQLAlchemy ORM e expõe uma função
utilitária para carregar o CSV simulado dentro do banco SQLite local
(dengue.db). Essa camada é a funcionalidade avançada de "Persistência em
banco" / "Modelagem relacional" pedida no enunciado do projeto G1.

Uso:
    python database/models.py
    (recria o banco a partir de dados/simulacao_dengue_brasil.csv)
"""
from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "dados", "simulacao_dengue_brasil.csv")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dengue.db")
DB_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()


class RegistroDengue(Base):
    """Um registro mensal de casos de dengue em um município brasileiro."""

    __tablename__ = "registros_dengue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    regiao = Column(String(20), nullable=False, index=True)
    uf = Column(String(2), nullable=False, index=True)
    municipio = Column(String(100), nullable=False, index=True)
    populacao = Column(Integer, nullable=False)
    chuva_mm = Column(Float, nullable=False)
    temperatura_media = Column(Float, nullable=False)
    casos_dengue = Column(Integer, nullable=False)
    internacoes = Column(Integer, nullable=False)
    obitos = Column(Integer, nullable=False)
    incidencia_100k = Column(Float, nullable=False)
    nivel_alerta = Column(String(10), nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover - apenas debug
        return (
            f"<RegistroDengue {self.municipio}/{self.uf} {self.ano}-{self.mes:02d} "
            f"casos={self.casos_dengue}>"
        )


def get_engine(echo: bool = False):
    return create_engine(DB_URL, echo=echo)


def criar_banco(df: pd.DataFrame | None = None, echo: bool = False) -> None:
    """Cria (ou recria) o banco SQLite e popula com os dados do CSV."""
    engine = get_engine(echo=echo)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    if df is None:
        df = pd.read_csv(CSV_PATH, parse_dates=["data"])
    else:
        df = df.copy()
        df["data"] = pd.to_datetime(df["data"])

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        registros = [
            RegistroDengue(
                ano=int(row.ano),
                mes=int(row.mes),
                data=row.data.date(),
                regiao=row.regiao,
                uf=row.uf,
                municipio=row.municipio,
                populacao=int(row.populacao),
                chuva_mm=float(row.chuva_mm),
                temperatura_media=float(row.temperatura_media),
                casos_dengue=int(row.casos_dengue),
                internacoes=int(row.internacoes),
                obitos=int(row.obitos),
                incidencia_100k=float(row.incidencia_100k),
                nivel_alerta=row.nivel_alerta,
            )
            for row in df.itertuples(index=False)
        ]
        session.bulk_save_objects(registros)
        session.commit()
        print(f"Banco criado em {DB_PATH} com {len(registros)} registros.")
    finally:
        session.close()


def carregar_dataframe() -> pd.DataFrame:
    """Lê todos os registros do banco SQLite e devolve um DataFrame pandas."""
    engine = get_engine()
    query = "SELECT * FROM registros_dengue"
    df = pd.read_sql(query, engine, parse_dates=["data"])
    return df


if __name__ == "__main__":
    criar_banco()

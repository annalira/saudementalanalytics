from typing import Union
from uvicorn import run
from fastapi import FastAPI
from typing import List, Dict

from sqlalchemy import create_engine, Column, Integer, String, func, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import numpy as np

DATABASE_URL = "postgresql://postgres:anna1412@localhost:5432/saudemental"

app = FastAPI()

engine = create_engine(DATABASE_URL)

# Cria uma sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

Base = declarative_base()

class DataSus(Base):
    __tablename__ = 'datasus'

    id = Column(Integer, primary_key=True)
    fonte = Column(String)
    origem = Column(String)
    ano = Column(Integer)
    morbidade = Column(String)
    estado = Column(String)
    sigla_estado = Column("sigla estado", String)
    casos = Column(Integer)

class Sisab(Base):
    __tablename__ = 'sisab'

    id = Column(Integer, primary_key=True)
    fonte = Column(String(10))
    origem = Column(String(50))
    ano = Column(Integer)
    estado = Column(String(50))
    sigla_estado = Column("sigla estado", String(10))
    consulta_agendada = Column("consulta agendada", Integer)
    consulta_no_dia = Column("consulta no dia", Integer)
    atendimento_de_urgencia = Column("atendimento de urgência", Integer)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# cards estáticos
@app.get("/total_internacoes")
def consulta_total_internacoes():
    with SessionLocal() as db:
        total_internacoes = db.query(func.sum(DataSus.casos)).scalar()
    return {"total_internacoes": total_internacoes}

@app.get("/total_atendimentos_sisab")
def consulta_total_atendimentos():
    with SessionLocal() as db:
        result = db.query(
            func.sum(Sisab.consulta_agendada),
            func.sum(Sisab.consulta_no_dia),
            func.sum(Sisab.atendimento_de_urgencia)
        ).first()

    total_consultas_agendadas, total_consultas_no_dia, total_atendimentos_urgencia = result
    total_geral = total_consultas_agendadas + total_consultas_no_dia + total_atendimentos_urgencia
    return {
        "total_geral": total_geral
    }

@app.get("/maior_numero_morbidade")
def consulta_morbidade_casos():
    with SessionLocal() as db:
        result = db.query(
            DataSus.morbidade,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.morbidade
        ).order_by(
            func.sum(DataSus.casos).desc()
        ).first()

    morbidade_maior_numero, total_casos = result
    return {
        "morbidade": morbidade_maior_numero,
        "total_casos": total_casos
    }


# gráfico de rosca
@app.get("/casos_por_morbidade", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_morbidade():
    with SessionLocal() as db:
        result = db.query(
            DataSus.morbidade,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.morbidade
        ).order_by(
            func.sum(DataSus.casos).desc()
        ).all()

    if not result:
        return {"error": "Nenhuma morbidade encontrada na base de dados"}

    return [{"morbidade": r[0], "total_casos": r[1]} for r in result]

@app.get("/casos_atendimentos_sisab", response_model=Dict[str, Union[int, str]])
def consulta_atendimentos_sisab():
    with SessionLocal() as db:
        result = db.query(
            func.sum(Sisab.consulta_agendada).label('total_consultas_agendadas'),
            func.sum(Sisab.consulta_no_dia).label('total_consultas_no_dia'),
            func.sum(Sisab.atendimento_de_urgencia).label('total_atendimentos_urgencia')
        ).first()

    if not result:
        return {"error": "Nenhum registro encontrado na base de dados"}

    return {
        "total_consultas_agendadas": result[0] or 0,
        "total_consultas_no_dia": result[1] or 0,
        "total_atendimentos_urgencia": result[2] or 0
    }


# gráfico de linhas
@app.get("/casos_por_morbidade_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_morbidade_ano_estado():
    with SessionLocal() as db:
        result = db.query(
            DataSus.morbidade,
            DataSus.ano,
            DataSus.estado,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.morbidade,
            DataSus.ano,
            DataSus.estado
        ).order_by(
            DataSus.morbidade,
            DataSus.ano,
            DataSus.estado
        ).all()

    return [{"morbidade": r.morbidade, "ano": r.ano, "estado": r.estado, "total_casos": r.total_casos} for r in result]

@app.get("/atendimentos_sisab_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_atendimentos_sisab_ano_estado():
    with SessionLocal() as db:
        result = db.query(
            Sisab.ano,
            Sisab.estado,
            func.sum(Sisab.consulta_agendada).label('total_consultas_agendadas'),
            func.sum(Sisab.consulta_no_dia).label('total_consultas_no_dia'),
            func.sum(Sisab.atendimento_de_urgencia).label('total_atendimentos_urgencia')
        ).group_by(
            Sisab.ano,
            Sisab.estado
        ).order_by(
            Sisab.ano,
            Sisab.estado
        ).all()

    if not result:
        return {"error": "Nenhum registro encontrado na base de dados"}

    return [
        {
            "ano": r[0],
            "estado": r[1],
            "total_consultas_agendadas": r[2],
            "total_consultas_no_dia": r[3],
            "total_atendimentos_urgencia": r[4]
        } for r in result
    ]


# gráfico de colunas
@app.get("/casos_por_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_ano_estado():
    with SessionLocal() as db:
        result = db.query(
            DataSus.ano,
            DataSus.estado,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.ano,
            DataSus.estado
        ).order_by(
            DataSus.ano,
            DataSus.estado
        ).all()

    if not result:
        return {"error": "Nenhum registro encontrado na base de dados"}

    return [
        {
            "ano": r[0],
            "estado": r[1],
            "total_casos": r[2]
        } for r in result
    ]

@app.get("/atendimentos_por_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_atendimentos_por_ano_estado():
    with SessionLocal() as db:
        result = db.query(
            Sisab.ano,
            Sisab.estado,
            (func.sum(Sisab.consulta_agendada) + func.sum(Sisab.consulta_no_dia) + func.sum(
                Sisab.atendimento_de_urgencia)).label('total_atendimentos')
        ).group_by(
            Sisab.ano,
            Sisab.estado
        ).order_by(
            Sisab.ano,
            Sisab.estado
        ).all()

    if not result:
        return {"error": "Nenhum registro encontrado na base de dados"}

    return [
        {
            "ano": r[0],
            "estado": r[1],
            "total_atendimentos": r[2]
        } for r in result
    ]


# mapa de casos
@app.get("/mapa_casos_datasus", response_model=List[Dict[str, Union[str, int, str]]])
def consulta_casos_por_estado():
    with SessionLocal() as db:
        results = db.query(
            DataSus.estado,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.estado
        ).order_by(
            DataSus.estado
        ).all()

    # Calcula os percentis para determinar os limites das faixas
    totais = [r[1] for r in results]
    p20 = round(np.percentile(totais, 20))
    p40 = round(np.percentile(totais, 40))
    p60 = round(np.percentile(totais, 60))
    p80 = round(np.percentile(totais, 80))

    response_data = []
    for r in results:
        estado, total_casos = r
        if total_casos <= p20:
            categoria = f"Faixa 1: 0 - {p20}"
        elif total_casos <= p40:
            categoria = f"Faixa 2: {p20+1} - {p40}"
        elif total_casos <= p60:
            categoria = f"Faixa 3: {p40+1} - {p60}"
        elif total_casos <= p80:
            categoria = f"Faixa 4: {p60+1} - {p80}"
        else:
            maximo = round(max(totais))
            categoria = f"Faixa 5: {p80+1} - {maximo}"
        response_data.append({
            "estado": estado,
            "total_casos": total_casos,
            "categoria": categoria
        })

    return response_data

@app.get("/mapa_atendimentos_sisab", response_model=List[Dict[str, Union[str, int, str]]])
def consulta_atendimentos_por_estado():
    with SessionLocal() as db:
        results = db.query(
            Sisab.estado,
            (func.sum(Sisab.consulta_agendada) +
             func.sum(Sisab.consulta_no_dia) +
             func.sum(Sisab.atendimento_de_urgencia)).label('total_atendimentos')
        ).group_by(
            Sisab.estado
        ).order_by(
            Sisab.estado
        ).all()

    # Calcula os percentis para determinar os limites das faixas
    totais_atendimentos = [r[1] for r in results]
    p20 = round(np.percentile(totais_atendimentos, 20))
    p40 = round(np.percentile(totais_atendimentos, 40))
    p60 = round(np.percentile(totais_atendimentos, 60))
    p80 = round(np.percentile(totais_atendimentos, 80))

    response_data = []
    for r in results:
        estado, total_atendimentos = r
        if total_atendimentos <= p20:
            categoria = f"Faixa 1: 0 - {p20}"
        elif total_atendimentos <= p40:
            categoria = f"Faixa 2: {p20+1} - {p40}"
        elif total_atendimentos <= p60:
            categoria = f"Faixa 3: {p40+1} - {p60}"
        elif total_atendimentos <= p80:
            categoria = f"Faixa 4: {p60+1} - {p80}"
        else:
            maximo = round(max(totais_atendimentos))
            categoria = f"Faixa 5: {p80+1} - {maximo}"
        response_data.append({
            "estado": estado,
            "total_atendimentos": total_atendimentos,
            "categoria": categoria
        })

    return response_data


# ranking
@app.get("/top5_estados_datasus", response_model=List[Dict[str, Union[str, int]]])
def consulta_top5_estados():
    with SessionLocal() as db:
        results = db.query(
            DataSus.estado,
            func.sum(DataSus.casos).label('total_casos')
        ).group_by(
            DataSus.estado
        ).order_by(
            func.sum(DataSus.casos).desc()
        ).limit(5).all()

    response_data = [{"estado": r[0], "total_casos": r[1]} for r in results]
    return response_data

@app.get("/top5_estados_sisab", response_model=List[Dict[str, Union[str, int]]])
def consulta_top5_estados_sisab():
    with SessionLocal() as db:
        results = db.query(
            Sisab.estado,
            (func.sum(Sisab.consulta_agendada)
             + func.sum(Sisab.consulta_no_dia)
             + func.sum(Sisab.atendimento_de_urgencia)).label('total_consultas')
        ).group_by(
            Sisab.estado
        ).order_by(
            (func.sum(Sisab.consulta_agendada)
             + func.sum(Sisab.consulta_no_dia)
             + func.sum(Sisab.atendimento_de_urgencia)).desc()
        ).limit(5).all()

    response_data = [{"estado": r[0], "total_consultas": r[1]} for r in results]
    return response_data



if __name__ == '__main__':
    run("main:app", host="127.0.0.1", port=8000, reload=True)

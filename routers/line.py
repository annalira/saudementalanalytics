from typing import List, Dict, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DataSus, Sisab
from sqlalchemy import func


router = APIRouter()

# gráfico de linhas
@router.get("/casos_por_morbidade_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_morbidade_ano_estado(db: Session = Depends(get_db)):

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


@router.get("/atendimentos_sisab_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_atendimentos_sisab_ano_estado(db: Session = Depends(get_db)):

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

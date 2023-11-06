from typing import List, Dict, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DataSus, Sisab
from sqlalchemy import func


router = APIRouter()


@router.get("/casos_por_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_ano_estado(db: Session = Depends(get_db)):

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


@router.get("/atendimentos_por_ano_estado", response_model=List[Dict[str, Union[str, int]]])
def consulta_atendimentos_por_ano_estado(db: Session = Depends(get_db)):

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

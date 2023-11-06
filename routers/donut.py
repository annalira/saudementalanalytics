from typing import List, Dict, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DataSus, Sisab
from sqlalchemy import func


router = APIRouter()


@router.get("/casos_por_morbidade", response_model=List[Dict[str, Union[str, int]]])
def consulta_casos_por_morbidade(db: Session = Depends(get_db)):

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


@router.get("/casos_atendimentos_sisab", response_model=Dict[str, Union[int, str]])
def consulta_atendimentos_sisab(db: Session = Depends(get_db)):

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

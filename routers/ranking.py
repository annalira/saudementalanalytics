from typing import List, Dict, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DataSus, Sisab
from sqlalchemy import func


router = APIRouter()


@router.get("/top5_estados_datasus", response_model=List[Dict[str, Union[str, int]]])
def consulta_top5_estados(db: Session = Depends(get_db)):

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


@router.get("/top5_estados_sisab", response_model=List[Dict[str, Union[str, int]]])
def consulta_top5_estados_sisab(db: Session = Depends(get_db)):

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

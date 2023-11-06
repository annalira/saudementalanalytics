from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DataSus, Sisab
from sqlalchemy import func


router = APIRouter()


# cards estáticos
@router.get("/total_internacoes")
def consulta_total_internacoes(db: Session = Depends(get_db)):
    total_internacoes = db.query(func.sum(DataSus.casos)).scalar()
    return {"total_internacoes": total_internacoes}


@router.get("/total_atendimentos_sisab")
def consulta_total_atendimentos(db: Session = Depends(get_db)):
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


@router.get("/maior_numero_morbidade")
def consulta_morbidade_casos(db: Session = Depends(get_db)):

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


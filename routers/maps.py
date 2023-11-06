from typing import List, Dict, Union

import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import DataSus, Sisab

router = APIRouter()


@router.get("/mapa_casos_datasus", response_model=List[Dict[str, Union[str, int, str]]])
def consulta_casos_por_estado(db: Session = Depends(get_db)):

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
            categoria = f"Faixa 2: {p20 + 1} - {p40}"
        elif total_casos <= p60:
            categoria = f"Faixa 3: {p40 + 1} - {p60}"
        elif total_casos <= p80:
            categoria = f"Faixa 4: {p60 + 1} - {p80}"
        else:
            maximo = round(max(totais))
            categoria = f"Faixa 5: {p80 + 1} - {maximo}"
        response_data.append({
            "estado": estado,
            "total_casos": total_casos,
            "categoria": categoria
        })

    return response_data


@router.get("/mapa_atendimentos_sisab", response_model=List[Dict[str, Union[str, int, str]]])
def consulta_atendimentos_por_estado(db: Session = Depends(get_db)):

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
            categoria = f"Faixa 2: {p20 + 1} - {p40}"
        elif total_atendimentos <= p60:
            categoria = f"Faixa 3: {p40 + 1} - {p60}"
        elif total_atendimentos <= p80:
            categoria = f"Faixa 4: {p60 + 1} - {p80}"
        else:
            maximo = round(max(totais_atendimentos))
            categoria = f"Faixa 5: {p80 + 1} - {maximo}"
        response_data.append({
            "estado": estado,
            "total_atendimentos": total_atendimentos,
            "categoria": categoria
        })

    return response_data

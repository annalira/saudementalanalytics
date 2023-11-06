from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
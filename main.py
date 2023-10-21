from typing import Union
from uvicorn import run
from fastapi import FastAPI

from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://postgres:admin@localhost/postgres"
# DATABASE_URL = "postgresql://<meu_usuario>:<minha_senha>@localhost/postgres"

app = FastAPI()

engine = create_engine(DATABASE_URL)

# Cria uma sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a classe de modelo (opcional)
Base = declarative_base()


class Pessoa(Base):
    __tablename__ = "pessoa"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/consulta")
def realizar_consulta():
    # Cria uma sessão do SQLAlchemy
    db = SessionLocal()
    # Exemplo de consulta
    # pessoas = db.query(Pessoa).filter_by(id=4).first()
    maior_idade = db.query(func.max(Pessoa.idade)).scalar()

    db.close()

    return maior_idade


# receita de bolo
@app.get("/maior_estado")
def consulta_maior_estado():
    db = SessionLocal()
    resultado = "consulta sqlalchemy"
    db.close()
    return resultado


if __name__ == '__main__':
    run("main:app", host="127.0.0.1", port=8000, reload=True)

#novo comentário
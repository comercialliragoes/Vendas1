# database.py
from sqlmodel import SQLModel, Field, create_engine
from datetime import date, time, datetime
#import streamlit as st
# Configuração do layout (wide mode)
#st.set_page_config(layout="wide")

# Definição das tabelas
class Produtos(SQLModel, table=True, extend_existing=True):
    id: int = Field(primary_key=True)
    codigo: str
    codInterno: str
    descricao: str
    preco: float

class Vendas(SQLModel, table=True, extend_existing=True):
    id: int = Field(primary_key=True)
    nome_cliente: str = Field(default='Cliente padrao')
    Total_venda: float
    forma_pagamento: str
    data: date = Field(default_factory=lambda: datetime.now().date(), nullable=False)

class Vendas_item(SQLModel, table=True, extend_existing=True):
    id: int = Field(primary_key=True)
    numero_venda: int
    codigo: str
    descricao: str
    preco: float
    quantidade: float
    total: float
    data: date = Field(default_factory=lambda: datetime.now().date(), nullable=False)
    hora: time = Field(default_factory=lambda: datetime.now().time(), nullable=False)

# Função para criar o engine e as tabelas para poder usar com o Streamlit
#@st.cache_resource
def setup_database():
    sqlite_file_name = "produtosBeta.db"
    connection_string = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(connection_string, echo=False)
    # descomente para criar as tabelas executando python database.py
    #SQLModel.metadata.create_all(engine)
    return engine

# Cria o engine e as tabelas
engine = setup_database()

if __name__ == "__main__":
   SQLModel.metadata.create_all(engine)

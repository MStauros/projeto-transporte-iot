# src/models/db_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Define a Base declarativa para seus modelos de banco de dados
# Esta Base é essencial para o SQLAlchemy mapear suas classes para tabelas.
Base = declarative_base()

class ViagemDB(Base): # Esta é a classe que o SQLAlchemy usará para interagir com o DB
    __tablename__ = 'viagens' # Nome da tabela no seu banco de dados PostgreSQL

    # Definição das colunas da tabela
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    categoria = Column(String, nullable=False)
    local_inicio = Column(String, nullable=False)
    local_fim = Column(String, nullable=False)
    distancia = Column(Float, nullable=False)
    proposito = Column(String, nullable=True) # 'nullable=True' significa que este campo pode ser nulo no DB

    def __repr__(self):
        """Representação da classe para facilitar a depuração."""
        return (f"<ViagemDB(id={self.id}, data_inicio='{self.data_inicio}', "
                f"categoria='{self.categoria}', distancia={self.distancia})>")


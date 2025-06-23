import os
from typing import Any, Dict


class DBConfig:
    """Configuração que lê do Docker Compose ou .env"""

    def __init__(self):
        # Valores padrão para desenvolvimento local
        default_config = {
            "user": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": "5432",
            "database": "viagens_db",
        }

        # Tenta ler do Docker Compose (quando rodando dentro do container)
        self.user = os.getenv("POSTGRES_USER", default_config["user"])
        self.password = os.getenv(
            "POSTGRES_PASSWORD", default_config["password"]
        )
        self.host = os.getenv(
            "POSTGRES_HOST", "postgres"
        )  # Nome do serviço no compose
        self.port = os.getenv("POSTGRES_PORT", default_config["port"])
        self.database = os.getenv("POSTGRES_DB", default_config["database"])

    def get_connection_dict(self) -> Dict[str, Any]:
        """Retorna configurações como dicionário"""
        return {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.database,
        }

    def get_sqlalchemy_url(self) -> str:
        """Retorna URL de conexão para SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Instância única da configuração
db_config = DBConfig()

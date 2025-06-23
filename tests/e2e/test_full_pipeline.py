# tests/e2e/test_full_pipeline.py

import json
import os
import time

import pytest
from kafka import KafkaProducer
from sqlalchemy import create_engine, text

# Configurações do Kafka e PostgreSQL para o ambiente de teste
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "iot")


@pytest.fixture(scope="module")
def kafka_producer_e2e():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    yield producer
    producer.close()


@pytest.fixture(scope="module")
def db_engine_e2e():
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(db_url)
    # Espera o banco de dados estar pronto
    max_retries = 10
    for i in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Conexão com o banco de dados estabelecida para E2E.")
            break
        except Exception as e:
            print(
                f"Tentativa {i+1}/{max_retries}: Conexão com o banco de dados falhou para E2E: {e}"
            )
            time.sleep(2)
    else:
        raise Exception(
            "Não foi possível conectar ao banco de dados após várias tentativas para E2E."
        )

    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS viagens"))
        connection.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS viagens (
                id SERIAL PRIMARY KEY,
                data_inicio TIMESTAMP,
                data_fim TIMESTAMP,
                categoria VARCHAR(255),
                local_inicio VARCHAR(255),
                local_fim VARCHAR(255),
                distancia FLOAT,
                proposito VARCHAR(255)
            )
        """
            )
        )
    yield engine
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS viagens"))


# Função de espera ativa
def wait_for_db_entry(engine, query, max_wait=10):
    for _ in range(max_wait):
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            if result:
                return result
        time.sleep(1)
    raise TimeoutError("Entrada não encontrada no banco após espera.")


def test_full_pipeline_data_flow(kafka_producer_e2e, db_engine_e2e):
    test_data = {
        "data_inicio": "2025-01-02T10:00:00",
        "data_fim": "2025-01-02T12:00:00",
        "categoria": "Viagem",
        "local_inicio": "Origem E2E",
        "local_fim": "Destino E2E",
        "distancia": 200.0,
        "proposito": "Lazer",
    }
    message_to_send = json.dumps(test_data).encode("utf-8")
    kafka_producer_e2e.send("dados-viagem", message_to_send)
    kafka_producer_e2e.flush()

    query = "SELECT * FROM viagens WHERE local_inicio = 'Origem E2E'"
    result = wait_for_db_entry(db_engine_e2e, query)

    assert len(result) == 1
    assert result[0]["categoria"] == "Viagem"
    assert result[0]["distancia"] == 200.0
    assert result[0]["proposito"] == "Lazer"

import pytest
import os
import time
import json
from kafka import KafkaProducer, KafkaConsumer
from sqlalchemy import create_engine, text

# Configurações do Kafka e PostgreSQL para o ambiente de teste
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin123')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'iot')

@pytest.fixture(scope='module')
def kafka_producer():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    yield producer
    producer.close()

@pytest.fixture(scope='module')
def kafka_consumer():
    consumer = KafkaConsumer(
        'dados-viagem',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id='test_group',
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )
    yield consumer
    consumer.close()

@pytest.fixture(scope='module')
def db_engine():
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(db_url)

    # Espera o banco de dados estar pronto
    max_retries = 10
    for i in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Conexão com o banco de dados estabelecida.")
            break
        except Exception as e:
            print(f"Tentativa {i+1}/{max_retries}: Conexão com o banco de dados falhou: {e}")
            time.sleep(2)
    else:
        raise Exception("Não foi possível conectar ao banco de dados após várias tentativas.")

    # Limpa a tabela antes dos testes
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS viagens"))
        connection.execute(text("""
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
        """))
    yield engine
    # Limpa a tabela após os testes
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS viagens"))

# Função utilitária para espera ativa no banco de dados
def wait_for_db_entry(engine, query, max_wait=10):
    for _ in range(max_wait):
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            if result:
                return result
        time.sleep(1)
    raise TimeoutError("Entrada não encontrada no banco após espera.")

def test_kafka_producer_sends_message(kafka_producer, kafka_consumer):
    test_dict = {"key": "test_producer", "value": "test_message"}
    test_message = json.dumps(test_dict).encode('utf-8')
    kafka_producer.send('dados-viagem', test_message)
    kafka_producer.flush()

    # Espera a mensagem ser entregue
    time.sleep(2)

    messages = []
    for message in kafka_consumer:
        decoded = json.loads(message.value.decode('utf-8'))
        messages.append(decoded)
        break  # Pega apenas uma mensagem

    assert test_dict in messages

def test_consumer_processes_message_and_stores_in_db(kafka_producer, db_engine):
    # Simula o envio de uma mensagem pelo produtor
    test_data = {
        "data_inicio": "2025-01-01T10:00:00",
        "data_fim": "2025-01-01T12:00:00",
        "categoria": "Negocio",
        "local_inicio": "Origem Teste",
        "local_fim": "Destino Teste",
        "distancia": 100.5,
        "proposito": "Reuniao"
    }
    test_message = json.dumps(test_data).encode('utf-8')
    kafka_producer.send('dados-viagem', test_message)
    kafka_producer.flush()

    # Espera o consumidor processar a mensagem
    query = "SELECT * FROM viagens WHERE local_inicio = 'Origem Teste'"
    result = wait_for_db_entry(db_engine, query)

    assert len(result) == 1
    assert result[0]["categoria"] == 'Negocio'
    assert result[0]["distancia"] == 100.5

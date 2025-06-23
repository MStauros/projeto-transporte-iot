# tests/unit/test_producer.py

import pytest
from src.producer.kafka_producer import ViagemKafkaProducer
from src.producer.sensor_simulator import gerar_viagens

class MockKafkaProducer:
    # ... (seu código existente) ...

def test_simulador_envia_viagem(monkeypatch):
    # Mock KafkaProducer para não precisar de Kafka real
    monkeypatch.setattr("src.producer.kafka_producer.KafkaProducer", MockKafkaProducer)

    producer = ViagemKafkaProducer(bootstrap_servers="mock:9092", topic="viagens")
    # Alteração aqui: pegue o primeiro item da lista
    viagens_geradas = gerar_viagens(1)
    viagem_unica = viagens_geradas[0] # <--- Pegue o único objeto Viagem da lista
    producer.enviar_viagem(viagem_unica) # <--- Envie o objeto único

    assert len(producer.producer.sent) == 1

    dados_enviados = producer.producer.sent[0][1]
    assert dados_enviados["categoria"] in ["Negócio", "Pessoal"]
    assert dados_enviados["distancia"] >= 0
    assert dados_enviados["local_inicio"] != dados_enviados["local_fim"]
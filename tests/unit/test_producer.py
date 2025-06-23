# tests/unit/test_producer.py

from src.producer.kafka_producer import ViagemKafkaProducer
from src.producer.sensor_simulator import gerar_viagens


class MockKafkaProducer:
    def __init__(self, *args, **kwargs):
        self.sent = []

    def send(self, topic, value):
        # O 'value' aqui já é o dicionário formatado pelo producer.viagem_to_payload.
        # Não precisa ser serializado para bytes pelo MockKafkaProducer para o propósito do teste.
        self.sent.append((topic, value))
        return True

    def flush(self):
        pass


def test_simulador_envia_viagem(monkeypatch):
    # Mock KafkaProducer para não precisar de Kafka real
    monkeypatch.setattr("src.producer.kafka_producer.KafkaProducer", MockKafkaProducer)

    producer = ViagemKafkaProducer(bootstrap_servers="mock:9092", topic="viagens")

    viagens_geradas = gerar_viagens(1)
    viagem_unica = viagens_geradas[0]  # Extrai o único objeto Viagem da lista

    producer.enviar_viagem(viagem_unica)

    assert len(producer.producer.sent) == 1

    # AQUI ESTÁ A CORREÇÃO FINAL PARA ESTE TESTE:
    # dados_enviados_raw já é o dicionário. Apenas atribua diretamente para 'dados_enviados'.
    dados_enviados = producer.producer.sent[0][1]  # <--- CORREÇÃO AQUI. Esta linha agora é a linha 35 no seu log.

    assert dados_enviados["categoria"] in ["Negócio", "Pessoal"]
    assert dados_enviados["distancia"] >= 0
    assert dados_enviados["local_inicio"] != dados_enviados["local_fim"]

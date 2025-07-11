from src.producer.kafka_producer import ViagemKafkaProducer
from src.producer.sensor_simulator import gerar_viagens


class MockKafkaProducer:
    def __init__(self, *args, **kwargs):
        self.sent = []

    def send(self, topic, value):
        # Mock simula o envio do valor direto, sem serialização para bytes
        self.sent.append((topic, value))
        return True

    def flush(self):
        pass


def test_simulador_envia_viagem(monkeypatch):
    # Mock KafkaProducer para não precisar de Kafka real
    monkeypatch.setattr("src.producer.kafka_producer.KafkaProducer", MockKafkaProducer)

    producer = ViagemKafkaProducer(bootstrap_servers="mock:9092", topic="viagens")

    viagens_geradas = gerar_viagens(1)
    viagem_unica = viagens_geradas[0]

    producer.enviar_viagem(viagem_unica)

    assert len(producer.producer.sent) == 1

    dados_enviados = producer.producer.sent[0][1]

    print(f"\nDEBUG: Conteúdo de dados_enviados no teste: {dados_enviados}")

    assert "CATEGORIA" in dados_enviados
    assert dados_enviados["CATEGORIA"] in ["Negócio", "Pessoal"]
    assert float(dados_enviados["DISTANCIA"]) >= 0
    assert dados_enviados["LOCAL_INICIO"] != dados_enviados["LOCAL_FIM"]

import json

from kafka import KafkaProducer

from ..models.sensor_data import Viagem


class ViagemKafkaProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.topic = topic

    def viagem_to_payload(self, viagem: Viagem) -> dict:
        """Formata os dados do objeto Viagem para o payload esperado pelo consumidor."""
        return {
            "DATA_INICIO": viagem.data_inicio.strftime("%m-%d-%Y %H"),
            "DATA_FIM": viagem.data_fim.strftime("%m-%d-%Y %H"),
            "CATEGORIA": viagem.categoria,
            "LOCAL_INICIO": viagem.local_inicio,
            "LOCAL_FIM": viagem.local_fim,
            "DISTANCIA": f"{viagem.distancia:.2f}",
            "PROPOSITO": viagem.proposito,
        }

    def enviar_viagem(self, viagem: Viagem):
        payload = self.viagem_to_payload(viagem)
        self.producer.send(self.topic, payload)
        self.producer.flush()

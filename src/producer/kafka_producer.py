from kafka import KafkaProducer
import json
from ..models.sensor_data import Viagem

class ViagemKafkaProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: v.encode("utf-8")
        )
        self.topic = topic

    def enviar_viagem(self, viagem: Viagem):
        self.producer.send(self.topic, viagem.model_dump_json())
        self.producer.flush()

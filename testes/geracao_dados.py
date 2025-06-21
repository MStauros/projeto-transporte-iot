import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.producer.kafka_producer import ViagemKafkaProducer
from src.producer.sensor_simulator import gerar_viagens
import time


def main():
    producer = ViagemKafkaProducer(
        bootstrap_servers="localhost:9092",  # se estiver rodando fora do container
        topic="dados-viagem"
    )

    viagens = gerar_viagens(10)  # gera 10 viagens

    for viagem in viagens:
        producer.enviar_viagem(viagem)
        print("Viagem enviada:", viagem)
        time.sleep(1)  # espera 1 segundo entre envios (só para simular algo mais realista)

if __name__ == "__main__":
    main()

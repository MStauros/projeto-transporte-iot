import time

from src.producer.kafka_producer import ViagemKafkaProducer
from src.producer.sensor_simulator import gerar_viagens


def run_simulador(n_iteracoes=100, intervalo=5):
    """
    Simula a geração e envio de dados de viagens para o Kafka.
    Args:
        n_iteracoes (int): Número de iterações para gerar e enviar lotes de viagens.
        intervalo (int): Intervalo em segundos entre cada envio de lote.
    """
    producer = ViagemKafkaProducer(bootstrap_servers="kafka:29092", topic="dados-viagem")

    for i in range(n_iteracoes):
        viagens = gerar_viagens(5)
        for viagem in viagens:
            producer.enviar_viagem(viagem)
            print(f"[{i+1}] Enviado: {viagem}")
        time.sleep(intervalo)


if __name__ == "__main__":
    run_simulador()

from src.producer.sensor_simulator import gerar_viagens
from src.producer.kafka_producer import ViagemKafkaProducer
import time

def run_simulador(n_iteracoes=10, intervalo=5):
    producer = ViagemKafkaProducer(bootstrap_servers="localhost:9092", topic="viagens")

    for i in range(n_iteracoes):
        viagens = gerar_viagens(5)
        for viagem in viagens:
            producer.enviar_viagem(viagem)
            print(f"[{i+1}] Enviado: {viagem}")
        time.sleep(intervalo)

if __name__ == "__main__":
    run_simulador()

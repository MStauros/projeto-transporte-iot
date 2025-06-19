from faker import Faker
from datetime import timedelta
import random
from typing import List
from ..models.sensor_data import Viagem

fake = Faker("pt_BR")

propositos_por_categorias = {
    "Negócio" : [
        "Alimentação",
        "Entregas",
        "Reunião",
        "Visita ao cliente",
        "Parada temporária",
        "Entre escritórios",
        "Aeroporto/Viagem",
        None
    ],
    "Pessoal" : [
        "Alimentação",
        "Parada temporária",
        "Caridade",
        "Deslocamento",
        "Aeroporto/Viagem",
        "Consulta Médica",
        None
    ]
}

categorias_viagem = list(propositos_por_categorias)

def gerar_cidade():
    cidade = fake.city()
    return f"{cidade}"

def gerar_viagem() -> Viagem:
    data_inicio = fake.date_time_between(start_date="-1y", end_date="now")
    duracao = timedelta(
        hours = random.randint(1, 24),
        days = random.randint(0, 14)
    )
    data_fim = data_inicio + duracao
    
    categoria = random.choice(categorias_viagem)
    proposito = random.choice(propositos_por_categorias[categoria])

    origem = gerar_cidade()
    destino = gerar_cidade()
    
    distancia = random.uniform(10, 500)
    
    return Viagem(
        data_inicio = data_inicio,
        data_fim = data_fim,
        categoria = categoria,
        local_inicio = origem,
        local_fim = destino,
        distancia = distancia,
        proposito = proposito
    )

def gerar_viagens(quantidade: int) -> List[Viagem]:
    return [gerar_viagem() for _ in range(quantidade)]
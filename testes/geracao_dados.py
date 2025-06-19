#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.producer.sensor_simulator import gerar_viagens

def main():
    print("=== TESTE DE GERAÇÃO DE DADOS DE VIAGEM ===")
    print("\n2. Gerando 3 viagens de uma vez:")
    viagens = gerar_viagens(3)
    for i, viagem in enumerate(viagens, 1):
        print(f"\nViagem {i}:")
        print(f"- Categoria: {viagem.categoria}")
        print(f"- De: {viagem.local_inicio} para {viagem.local_fim}")
        print(f"- Distância: {viagem.distancia:.2f} km")
        print(f"- Período: {viagem.data_inicio} a {viagem.data_fim}")
        if viagem.proposito:
            print(f"- Propósito: {viagem.proposito}")

if __name__ == "__main__":
    main()
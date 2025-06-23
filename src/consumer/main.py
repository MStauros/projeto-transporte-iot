import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao sys.path para permitir imports relativos
sys.path.append(str(Path(__file__).parent.parent.parent))


from src.consumer.data_processor import DataProcessor

# Carrega variáveis de ambiente do .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MainConsumer")


def main():
    kafka_config = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
        "group.id": os.getenv("KAFKA_GROUP_ID", "viagem-consumer-group"),
    }

    db_connection_url = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )
    print(f"DEBUG: DB Connection URL: {db_connection_url}")

    processor = DataProcessor(kafka_config, db_connection_url)
    processor.consume_messages(os.getenv("KAFKA_TOPIC", "dados-viagem"))


if __name__ == "__main__":
    main()

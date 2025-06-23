import json
import logging
from datetime import datetime
from confluent_kafka import Consumer, KafkaException, KafkaError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.sensor_data import Viagem

from src.models.sensor_data import Viagem as PydanticViagem
from src.models.db_models import ViagemDB, Base

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ViagemProcessor")


class DataProcessor:
    def __init__(self, kafka_config: dict, db_connection_url: str):
        """Inicializa o processador com conexões Kafka e PostgreSQL"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.kafka_config = kafka_config
        self.db_connection_url = db_connection_url
        self.setup_db()
        self.setup_kafka()

    def setup_db(self):
        """Configura a conexão com o banco de dados"""
        try:
            # Usar db_connection_url diretamente, que já vem do main.py com as variáveis de ambiente
            self.engine = create_engine(self.db_connection_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info("Conexão com PostgreSQL configurada.")
        except Exception as e:
            self.logger.error("Erro ao conectar no PostgreSQL: %s", str(e))
            raise

    def setup_kafka(self):
        """Configura o consumer Kafka"""
        try:
            self.consumer = Consumer(
                {
                    "bootstrap.servers": self.kafka_config["bootstrap.servers"],
                    "group.id": self.kafka_config.get("group.id", "viagem-group"),
                    "auto.offset.reset": self.kafka_config.get(
                        "auto.offset.reset", "earliest"
                    ),
                    "enable.auto.commit": self.kafka_config.get(
                        "enable.auto.commit", False
                    ),
                }
            )
            self.logger.info(
                "Consumer Kafka configurado para servers: %s",
                self.kafka_config["bootstrap.servers"],
            )
        except Exception as e:
            self.logger.error("Erro ao configurar Kafka consumer: %s", str(e))
            raise

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Converte string no formato mm-dd-yyyy HH para datetime"""
        try:
            return datetime.strptime(dt_str, "%m-%d-%Y %H")
        except ValueError as e:
            logger.warning("Formato de data inválido: %s - %s", dt_str, str(e))
            raise

    def process_message(self, msg_value: dict) -> ViagemDB:
        """Processa e valida uma mensagem Kafka"""
        try:
            # Validação básica dos campos obrigatórios
            required_fields = [
                "DATA_INICIO",
                "DATA_FIM",
                "CATEGORIA",
                "LOCAL_INICIO",
                "LOCAL_FIM",
                "DISTANCIA",
            ]
            if not all(field in msg_value for field in required_fields):
                raise ValueError("Mensagem incompleta - campos obrigatórios faltando")

            # Conversão de tipos
            data_inicio = self._parse_datetime(msg_value["DATA_INICIO"])
            data_fim = self._parse_datetime(msg_value["DATA_FIM"])
            distancia = float(msg_value["DISTANCIA"])

            # Validações de negócio
            if distancia < 0:
                raise ValueError("Distância não pode ser negativa")
            if data_fim < data_inicio:
                raise ValueError("Data de fim anterior à data de início")

            return ViagemDB(
                data_inicio=data_inicio,
                data_fim=data_fim,
                categoria=msg_value["CATEGORIA"],
                local_inicio=msg_value["LOCAL_INICIO"],
                local_fim=msg_value["LOCAL_FIM"],
                distancia=distancia,
                proposito=msg_value.get("PROPOSITO"),
            )

        except Exception as e:
            self.logger.error("Erro no processamento da mensagem: %s", str(e))
            raise

    def save_to_db(self, data: ViagemDB):
        """Salva os dados processados no PostgreSQL"""
        session = self.Session()
        try:
            session.add(data)
            session.commit()
            self.logger.debug("Dados salvos no DB - ID: %s", data.id)
        except Exception as e:
            session.rollback()
            self.logger.error("Erro ao salvar no PostgreSQL: %s", str(e))
            raise
        finally:
            session.close()

    def consume_messages(self, topic: str):
        """Consome mensagens do tópico Kafka indefinidamente"""
        self.consumer.subscribe([topic])
        self.logger.info("Iniciando consumo do tópico: {topic}")

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        self.logger.error("Erro no Kafka: %s", msg.error())
                        continue  # Continua tentando consumir outras mensagens

                try:
                    payload = json.loads(msg.value().decode("utf-8"))
                    processed_data = self.process_message(payload)
                    self.save_to_db(processed_data)
                    self.consumer.commit(asynchronous=False)
                    self.logger.info("Mensagem processada - Offset: %d", msg.offset())

                except Exception as e:
                    self.logger.error(
                        "Erro no processamento ou salvamento da mensagem (offset %d): %s",
                        msg.offset(),
                        str(e),
                    )
                    # Não relança o erro aqui para não parar o consumer por uma única mensagem inválida
                    # O commit não é feito para esta mensagem, permitindo reprocessamento ou tratamento posterior
                    continue

        except KeyboardInterrupt:
            self.logger.info("Interrompido pelo usuário")
        finally:
            self.consumer.close()
            self.logger.info("Consumer Kafka fechado")

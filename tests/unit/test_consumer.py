from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.consumer.data_processor import DataProcessor
from src.models.db_models import ViagemDB


@pytest.fixture
def sample_valid_message():
    return {"DATA_INICIO": "06-15-2023 14", "DATA_FIM": "06-15-2023 18", "CATEGORIA": "URBANA", "LOCAL_INICIO": "SÃO PAULO", "LOCAL_FIM": "SÃO PAULO", "DISTANCIA": "50.0", "PROPOSITO": "ENTREGA"}


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_process_valid_message(sample_valid_message):
    # Fornece um kafka_config válido para a inicialização do DataProcessor nos testes
    processor = DataProcessor({"bootstrap.servers": "mock_kafka:9092"}, "sqlite:///:memory:")
    result = processor.process_message(sample_valid_message)

    assert isinstance(result, ViagemDB)
    assert result.categoria == "URBANA"
    assert result.distancia == 50.0
    assert result.data_inicio.year == 2023


def test_process_invalid_message():
    # Fornece um kafka_config válido para a inicialização do DataProcessor nos testes
    processor = DataProcessor({"bootstrap.servers": "mock_kafka:9092"}, "sqlite:///:memory:")
    invalid_msg = {"DATA_INICIO": "06-15-2023 14"}

    with pytest.raises(ValueError):
        processor.process_message(invalid_msg)


def test_store_data(mock_db_session):
    # Fornece um kafka_config válido para a inicialização do DataProcessor nos testes
    processor = DataProcessor({"bootstrap.servers": "mock_kafka:9092"}, "sqlite:///:memory:")
    processor.Session = MagicMock(return_value=mock_db_session)

    test_data = ViagemDB(data_inicio=datetime.now(), data_fim=datetime.now(), categoria="TEST", local_inicio="A", local_fim="B", distancia=10.0)

    processor.save_to_db(test_data)
    mock_db_session.add.assert_called_once_with(test_data)
    mock_db_session.commit.assert_called_once()

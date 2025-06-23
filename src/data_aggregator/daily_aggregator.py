# src/data_aggregator/daily_aggregator.py

import logging
import os

from sqlalchemy import and_, case, create_engine, func
from sqlalchemy.orm import sessionmaker

from src.models.db_models import Base, InfoCorridasDoDia, ViagemDB

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DailyAggregator")


class DailyAggregator:
    def __init__(self, db_connection_url: str):
        self.db_connection_url = db_connection_url
        self.engine = create_engine(self.db_connection_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Aggregator: Conexão com PostgreSQL configurada.")

    def aggregate_daily_data(self):
        """
        Agrega os dados da tabela 'viagens' por dia e popula/atualiza
        a tabela 'info_corridas_do_dia'.
        """
        session = self.Session()
        try:
            logger.info("Iniciando agregação diária de dados de viagens...")

            # --- CONSTRUÇÃO DA CONSULTA SQL MAIS MODULAR E EXPLÍCITA ---
            # Definindo as colunas agregadas individualmente
            dt_refe_col = func.date(ViagemDB.data_inicio).label("dt_refe")
            qt_corr_col = func.count(ViagemDB.id).label("qt_corr")

            # Contagens condicionais usando func.sum(case(...))
            qt_corr_neg_col = func.sum(
                case((ViagemDB.categoria == "Negócio", 1), else_=0)
            ).label("qt_corr_neg")

            qt_corr_pess_col = func.sum(
                case((ViagemDB.categoria == "Pessoal", 1), else_=0)
            ).label("qt_corr_pess")

            vl_max_dist_col = func.max(ViagemDB.distancia).label("vl_max_dist")
            vl_min_dist_col = func.min(ViagemDB.distancia).label("vl_min_dist")
            vl_avg_dist_col = func.avg(ViagemDB.distancia).label("vl_avg_dist")

            qt_corr_reuni_col = func.sum(
                case((ViagemDB.proposito == "Reunião", 1), else_=0)
            ).label("qt_corr_reuni")

            qt_corr_nao_reuni_col = func.sum(
                case(
                    (
                        and_(
                            ViagemDB.proposito is not None,
                            ViagemDB.proposito != "Reunião",
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("qt_corr_nao_reuni")

            # Combina todas as colunas para a consulta principal
            daily_stats_query = (
                session.query(
                    dt_refe_col,
                    qt_corr_col,
                    qt_corr_neg_col,
                    qt_corr_pess_col,
                    vl_max_dist_col,
                    vl_min_dist_col,
                    vl_avg_dist_col,
                    qt_corr_reuni_col,
                    qt_corr_nao_reuni_col,
                )
                .group_by(dt_refe_col)
                .all()
            )  # Agrupa pela coluna de data_referencia

            # Processa os resultados e insere/atualiza na tabela info_corridas_do_dia
            for row in daily_stats_query:  # Iterar sobre o resultado da query
                dt_refe = row.dt_refe

                # Tenta encontrar um registro existente para a data
                existing_entry = (
                    session.query(InfoCorridasDoDia).filter_by(dt_refe=dt_refe).first()
                )

                if existing_entry:
                    # Atualiza o registro existente
                    existing_entry.qt_corr = row.qt_corr
                    existing_entry.qt_corr_neg = row.qt_corr_neg
                    existing_entry.qt_corr_pess = row.qt_corr_pess
                    existing_entry.vl_max_dist = row.vl_max_dist
                    existing_entry.vl_min_dist = row.vl_min_dist
                    existing_entry.vl_avg_dist = row.vl_avg_dist
                    existing_entry.qt_corr_reuni = row.qt_corr_reuni
                    existing_entry.qt_corr_nao_reuni = row.qt_corr_nao_reuni
                    logger.debug(f"Atualizado InfoCorridasDoDia para {dt_refe}")
                else:
                    # Cria um novo registro
                    new_entry = InfoCorridasDoDia(
                        dt_refe=dt_refe,
                        qt_corr=row.qt_corr,
                        qt_corr_neg=row.qt_corr_neg,
                        qt_corr_pess=row.qt_corr_pess,
                        vl_max_dist=row.vl_max_dist,
                        vl_min_dist=row.vl_min_dist,
                        vl_avg_dist=row.vl_avg_dist,
                        qt_corr_reuni=row.qt_corr_reuni,
                        qt_corr_nao_reuni=row.qt_corr_nao_reuni,
                    )
                    session.add(new_entry)
                    logger.debug(f"Inserido novo InfoCorridasDoDia para {dt_refe}")

            session.commit()
            logger.info("Agregação diária concluída e dados salvos com sucesso.")

        except Exception as e:
            session.rollback()
            logger.error("Erro durante a agregação diária: %s", str(e))
            raise
        finally:
            session.close()


# Exemplo de como rodar o agregador (pode ser usado em um script principal separado)
if __name__ == "__main__":
    # Carregar variáveis de ambiente para a URL do DB
    from dotenv import load_dotenv

    load_dotenv()

    db_connection_url = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    aggregator = DailyAggregator(db_connection_url)
    aggregator.aggregate_daily_data()

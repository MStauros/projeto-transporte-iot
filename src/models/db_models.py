from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

# Define a Base declarativa para seus modelos de banco de dados
Base = declarative_base()


class ViagemDB(Base):
    __tablename__ = "viagens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    categoria = Column(String, nullable=False)
    local_inicio = Column(String, nullable=False)
    local_fim = Column(String, nullable=False)
    distancia = Column(Float, nullable=False)
    proposito = Column(String, nullable=True)

    def __repr__(self):
        return f"<ViagemDB(id={self.id}, data_inicio='{self.data_inicio}', " f"categoria='{self.categoria}', distancia={self.distancia})>"


class InfoCorridasDoDia(Base):
    __tablename__ = "info_corridas_do_dia"

    dt_refe = Column(Date, primary_key=True, nullable=False)
    qt_corr = Column(Integer, nullable=False)
    qt_corr_neg = Column(Integer, nullable=False)
    qt_corr_pess = Column(Integer, nullable=False)
    vl_max_dist = Column(Float, nullable=False)
    vl_min_dist = Column(Float, nullable=False)
    vl_avg_dist = Column(Float, nullable=False)
    qt_corr_reuni = Column(Integer, nullable=False)
    qt_corr_nao_reuni = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<InfoCorridasDoDia(dt_refe='{self.dt_refe}', qt_corr={self.qt_corr}, " f"vl_avg_dist={self.vl_avg_dist})>"

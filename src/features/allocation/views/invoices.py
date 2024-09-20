from sqlalchemy import text
from src.features.allocation.service_layer import unit_of_work


def client_statistics(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text("SELECT * FROM prueba"),
        )
    data = [dict(row._mapping) for row in results]
    return data


def system_load(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session
        load_query = text("""
            SELECT record_timestamp, SUM(value) AS load
            FROM consumption
            GROUP BY record_timestamp
            ORDER BY record_timestamp
        """)
        return session.execute(load_query).fetchall()
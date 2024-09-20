from sqlalchemy import text
from src.features.allocation.service_layer import unit_of_work
#GET /client-statistics/{client_id}: Proporciona estadísticas de consumo e
#inyección para un cliente
def client_statistics(client_id , uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session
        load_query = text("""
            SELECT record_timestamp, SUM(value) AS load
            FROM consumption
            GROUP BY record_timestamp
            ORDER BY record_timestamp
        """)
        return session.execute(load_query).fetchall()



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
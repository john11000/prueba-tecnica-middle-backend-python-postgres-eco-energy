from sqlalchemy import text
from src.features.allocation.service_layer import unit_of_work

def system_load(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session
        load_query = text("""
            SELECT record_timestamp, SUM(value) AS load
            FROM consumption c
            join records r 
            on r.id_record  = c.id_record 
            GROUP BY record_timestamp
            ORDER BY record_timestamp

        """)
        results = session.execute(load_query).fetchall()
        return [{"timestamp": row.record_timestamp, "load": row.load} for row in results]
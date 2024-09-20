from sqlalchemy import text
from src.features.allocation.service_layer import unit_of_work


def get_invoice(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text("SELECT * FROM prueba"),
        )
    data = [dict(row._mapping) for row in results]
    return data
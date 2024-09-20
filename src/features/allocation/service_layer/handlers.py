from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import asdict

from sqlalchemy import text

from src.features.allocation.domain import commands

if TYPE_CHECKING:
    from . import unit_of_work


# def add_batch(
#     cmd: commands.CreateBatch,
#     uow: unit_of_work.AbstractUnitOfWork,
# ):
#     with uow:
#         product = uow.products.get(sku=cmd.sku)
#         if product is None:
#             product = model.Product(cmd.sku, batches=[])
#             uow.products.add(product)
#         product.batches.append(model.Batch(cmd.ref, cmd.sku, cmd.qty, cmd.eta))
#         uow.commit()

# def remove_allocation_from_read_model(
#     event: events.Deallocated,
#     uow: unit_of_work.SqlAlchemyUnitOfWork,
# ):
#     with uow:
#         uow.session.execute(
#             text("""
#             DELETE FROM allocations_view
#             WHERE orderid = :orderid AND sku = :sku
#             """),
#             dict(orderid=event.orderid, sku=event.sku),
#         )
#         uow.commit()

def get_invoice(
        cmd: commands.GetInvoice,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        results = uow.session.execute(
            text("""
            SELECT * FROM prueba
            """),
        )
        data = [dict(row._mapping) for row in results]
        return data
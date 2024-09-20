from datetime import datetime
from fastapi import APIRouter

from src.features.allocation.domain import commands
from src.features.allocation.api.views import view_router
from src.features.allocation.service_layer import messagebus, unit_of_work

api_router = APIRouter()
api_router.include_router(view_router)


"""POST /calculate-invoice: Calcula la factura para un cliente y un mes específico"""
@api_router.post("/calculate-invoice/{client_id}/{month}")
def calculate_invoice(client_id: int, month: int):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    cmd = commands.GetInvoice(client_id, month)
    invoice = messagebus.handle(cmd, uow)
    return { "client_id": client_id, "month": month, "invoice": invoice}


"""Adicionar un endpoint para el cálculo independiente de cada concepto"""
@api_router.post("/calculate-concept-invoice/{client_id}/{month}/{concept}")
def calculate_concept_invoice(client_id: int, month: int, concept: str):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    cmd = commands.CalculateInvoiceByConcept(client_id, month, concept)
    invoice = messagebus.handle(cmd, uow)
    return { "client_id": client_id, "month": month, "invoice": invoice }

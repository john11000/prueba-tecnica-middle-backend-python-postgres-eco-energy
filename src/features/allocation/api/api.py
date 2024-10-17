from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.features.allocation.api.schema import ConceptEnum, EntitiesEnum
from src.features.allocation.domain import commands
from src.features.allocation.api.views import view_router
from src.features.allocation.service_layer import messagebus, unit_of_work

api_router = APIRouter()
api_router.include_router(view_router)
uow = unit_of_work.SqlAlchemyUnitOfWork()


"""POST /calculate-invoice: Calcula la factura para un cliente y un mes específico"""
@api_router.post("/calculate-invoice/{id_service}/{month}")
def calculate_invoice(id_service: int, month: int):
    try:
        cmd = commands.GetInvoice(id_service, month)
        invoice = messagebus.handle(cmd, uow)
        return { "id_service": id_service, "month": month, "invoice": invoice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""Adicionar un endpoint para el cálculo independiente de cada concepto"""
@api_router.post("/calculate-invoice/{id_service}/{month}/{concept}")
def calculate_concept_invoice(id_service: int, month: int, concept: ConceptEnum):
    try:
        cmd = commands.GetInvoice(id_service, month, concept)
        invoice = messagebus.handle(cmd, uow)
        return { "id_service": id_service, "month": month, "invoice": invoice }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

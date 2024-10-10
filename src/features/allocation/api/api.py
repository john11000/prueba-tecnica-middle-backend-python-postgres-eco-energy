from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, Form, File

from src.features.allocation.api.schema import ConceptEnum, EntitiesEnum
from src.features.allocation.domain import commands
from src.features.allocation.api.views import view_router
from src.features.allocation.service_layer import messagebus, unit_of_work

api_router = APIRouter()
api_router.include_router(view_router)
uow = unit_of_work.SqlAlchemyUnitOfWork()


"""POST /calculate-invoice: Calcula la factura para un cliente y un mes específico"""
@api_router.post("/calculate-invoice/{client_id}/{month}")
def calculate_invoice(client_id: int, month: int):
    try:
        cmd = commands.GetInvoice(client_id, month)
        invoice = messagebus.handle(cmd, uow)
        return { "client_id": client_id, "month": month, "invoice": invoice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""Adicionar un endpoint para el cálculo independiente de cada concepto"""
@api_router.post("/calculate-invoice/{client_id}/{month}/{concept}")
def calculate_concept_invoice(client_id: int, month: int, concept: ConceptEnum):
    try:
        cmd = commands.GetInvoice(client_id, month, concept)
        invoice = messagebus.handle(cmd, uow)
        return { "client_id": client_id, "month": month, "invoice": invoice }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

""" 
POST /upload-excel: endpoint para subir excels o importar datos masivos
"""
@api_router.post("/upload-excel")
async def upload_excel(fileToProcess: UploadFile = File(), to: EntitiesEnum = Form(...)):
    try:
        cmd = commands.UploadFile(fileToProcess, to)
        invoice = messagebus.handle(cmd, uow)
        return {"msg": f"File uploaded successfully to {to.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
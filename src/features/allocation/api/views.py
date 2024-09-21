from typing import List

from fastapi import APIRouter, Query, HTTPException

from src.features.allocation import views
from src.features.allocation.api.schema import Message, ClientStatistics
from src.features.allocation.domain import commands
from src.features.allocation.service_layer import messagebus, unit_of_work


view_router = APIRouter()
uow = unit_of_work.SqlAlchemyUnitOfWork()


"""GET /client-statistics/{client_id}: Proporciona estadísticas de consumo e
inyección para un cliente"""
@view_router.get("/client-statistics/{client_id}")
def client_statistics(client_id: int, show_details: bool = Query(False)):
    try:
        cmd = commands.GetClientStatistics(client_id, show_details)
        results = messagebus.handle(cmd, uow)
        return {
            "client_id": client_id,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
GET /system-load: Muestra la carga del sistema por hora basada en los datos
de consumo
"""
@view_router.get("/system-load")
def system_load():
    try: 
        results = views.system_load(uow)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
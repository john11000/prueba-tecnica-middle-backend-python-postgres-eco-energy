from typing import List

from fastapi import APIRouter

from src.features.allocation import views
from src.features.allocation.api.schema import Message, ClientStatistics
from src.features.allocation.domain import commands
from src.features.allocation.service_layer import messagebus, unit_of_work


view_router = APIRouter()


"""GET /client-statistics/{client_id}: Proporciona estadísticas de consumo e
inyección para un cliente"""
@view_router.get("/client-statistics/{client_id}")
def client_statistics(client_id: int):
    try:
        uow = unit_of_work.SqlAlchemyUnitOfWork()
        cmd = commands.GetClientStatistics(client_id)
        results = messagebus.handle(cmd, uow)
        return {
            "client_id": client_id,
            "results": results,
        }
    except Exception as e:
        return {"message": str(e)}


"""
GET /system-load: Muestra la carga del sistema por hora basada en los datos
de consumo
"""
@view_router.get("/system-load")
def system_load() -> List[Message]:
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    results = views.system_load(uow)
    return results
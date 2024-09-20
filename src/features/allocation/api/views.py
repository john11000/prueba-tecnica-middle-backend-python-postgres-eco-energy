from typing import List

from fastapi import APIRouter

from src.features.allocation import views
from src.features.allocation.api.schema import Message
from src.features.allocation.service_layer import unit_of_work


view_router = APIRouter()


@view_router.get('/hello')
def hello() -> Message:
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    results = views.get_test(uow)
    print(results)
    return {"message": "Hello, World!", "data": results}

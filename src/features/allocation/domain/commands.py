# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass
from src.features.allocation.api.schema import ConceptEnum, EntitiesEnum

class Command:
    pass

@dataclass
class GetInvoice(Command):
    id_service: int
    month: int
    concept: Optional[ConceptEnum] = None


@dataclass
class CalculateInvoiceByConcept(Command):
    id_service: int
    month: int
    concept: str

@dataclass
class GetClientStatistics(Command):
    id_service: int
    show_details: bool = False

@dataclass
class GetSystemLoad(Command):
    pass

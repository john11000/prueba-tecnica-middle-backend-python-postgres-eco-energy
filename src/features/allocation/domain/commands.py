# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass

from src.features.allocation.api.schema import ConceptEnum

class Command:
    pass

@dataclass
class GetInvoice(Command):
    client_id: int
    month: int
    concept: Optional[ConceptEnum] = None


@dataclass
class CalculateInvoiceByConcept(Command):
    client_id: int
    month: int
    concept: str

@dataclass
class GetClientStatistics(Command):
    client_id: int
    show_details: bool = False

@dataclass
class GetSystemLoad(Command):
    pass
# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass

class Command:
    pass
@dataclass
class GetInvoice(Command):
    client_id: int
    month: int

@dataclass
class CalculateInvoiceByConcept(Command):
    client_id: int
    month: int
    concept: str
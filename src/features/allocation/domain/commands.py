# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass
from fastapi import UploadFile as FastAPIUploadFile
from src.features.allocation.api.schema import ConceptEnum, EntitiesEnum

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

@dataclass
class UploadFile(Command):
    fileToProcess: FastAPIUploadFile
    to: Optional[EntitiesEnum] = None
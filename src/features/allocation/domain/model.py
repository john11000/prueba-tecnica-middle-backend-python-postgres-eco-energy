from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set

@dataclass
class Injection:
    id_record: int
    value: float


@dataclass
class Consumption:
    id_record: int
    value: float


@dataclass
class XMDataHourlyPerAgent:
    record_timestamp: datetime
    value: float


@dataclass
class Service:
    id_service: int
    id_market: int
    cdi: int
    voltage_level: int
    records: Set['Record'] = None


@dataclass
class Record:
    id_record: int
    id_service: int
    record_timestamp: datetime
    service: Service = None
    xm_data: XMDataHourlyPerAgent = None


@dataclass
class Tariff:
    id_market: int
    cdi: int
    voltage_level: int
    G: float
    T: float
    D: float
    R: float
    C: float
    P: float
    CU: float
    service: Service = None

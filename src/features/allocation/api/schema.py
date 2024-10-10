from enum import Enum
from pydantic import BaseModel, Field
class Message(BaseModel):
    message: str = Field(..., example="hello world")

class ConceptEnum(str, Enum):
    EA = "EA"
    EC = "EC"
    EE1 = "EE1"
    EE2 = "EE2"
    
class EntitiesEnum(str, Enum):
    SERVICES = "services"
    RECORDS = "records"
    INJECTION = "Injection"
    CONSUMPTION = "Consumption"
    XM = "xm_data_hourly_per_agent"
    TARIFFS = "tariffs"

class ClientStatistics(BaseModel):
    client_id: int = Field(..., example="400")
    total_consumed: float 
    total_injected: float

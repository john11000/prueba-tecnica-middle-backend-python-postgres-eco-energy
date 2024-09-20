from pydantic import BaseModel, Field
class Message(BaseModel):
    message: str = Field(..., example="hello world")

class ClientStatistics(BaseModel):
    client_id: int
    total_consumed: float
    total_injected: float

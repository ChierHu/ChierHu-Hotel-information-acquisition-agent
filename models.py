from pydantic import BaseModel

class Output(BaseModel):
    property_name: str
    address: str
    postal_code: str
    country: str
    overview: str

class Lists(BaseModel):
    lists: list[Output] 
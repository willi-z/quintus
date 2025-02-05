from pydantic import BaseModel


class Flag(BaseModel):
    field: str
    flag_as: str

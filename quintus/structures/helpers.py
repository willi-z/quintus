from typing import Type
from pydantic import BaseModel


def collect_model_attr(model: Type[BaseModel] | None) -> set[str]:
    fields = set()
    if model is None:
        return fields
    if issubclass(model, BaseModel):
        fields.update(model.__fields__.keys())
    return fields

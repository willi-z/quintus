from pydantic import BaseModel, field_validator
import re


class Measurement(BaseModel):
    value: float = None
    unit: str = None
    tol: tuple[float] | list[float] = None
    source: str = None
    at: dict[str, "Measurement"] = None

    @field_validator("unit")
    def valid_unit(cls, val):
        if val is None:
            return "1"
        return val

    @field_validator("tol")
    def valid_tolerance(cls, val):
        if val is None:
            return val
        if len(val) > 2:
            raise ValueError(
                "Tolerance sould be of size 2! " + f"(detemined size {len(val)})"
            )
        if val[0] > val[1]:
            raise ValueError("Tolerance should be (minumum, maximum)!")
        return val

    @field_validator("source")
    def valid_source(cls, val: str):
        if val is None:
            return val
        regexs = [
            r"^approximation$",
            r"^experiment$",
            r"^literature$",
            r"^computation$",
            r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b',  # doi
        ]
        for regex in regexs:
            p = re.compile(regex)
            if len(p.findall(val)) > 0:
                return val
        raise ValueError("Source did not match!")

    def is_empty(self) -> bool:
        if self.value is None:
            return True
        return False

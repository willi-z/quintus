from pydantic import BaseModel, validator
import re


class SimpleMeasurement(BaseModel):
    value: float
    unit: str
    tol: tuple[float] | list[float] = None

    @validator("unit")
    def valid_unit(cls, val):
        return val

    @validator("tol")
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


class Measurement(SimpleMeasurement):
    at: dict[str, SimpleMeasurement] = None
    source: str = None

    @validator("source")
    def valid_source(cls, val: str):
        if val is None:
            return val
        regexs = [
            r"^experiment$",
            r"^computation$",
            r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b',
        ]
        for regex in regexs:
            p = re.compile(regex)
            if len(p.findall(val)) > 0:
                return val
        raise ValueError("Source did not match!")


class Measurements(BaseModel):
    __base__: dict[str, Measurement]

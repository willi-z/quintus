from .measurement import Measurement
from .component import Component
from pydantic import BaseModel
from quintus.helpers import parse_unit
from typing import cast
from pydantic.fields import FieldInfo


def get_SI_value(measurement: Measurement) -> float:
    if measurement.unit is None:
        return measurement.value
    else:
        return measurement.value * parse_unit(measurement.unit)


def get_SI_tol(measurement: Measurement) -> tuple[float, float]:
    if measurement.tol is not None:
        tols = measurement.tol
        unit_convertion = parse_unit(measurement.unit)
        return (
            tols[0] * unit_convertion,
            tols[1] * unit_convertion,
        )
    else:
        return (0.0, 0.0)


def component_to_dict(comp: Component) -> dict:
    # result = json.loads(comp.model_dump_json(exclude_unset=True, exclude_none=True))
    # warnings.filterwarnings("error")
    result = dict()
    try:
        result = comp.model_dump(
            exclude_none=True,
            by_alias=True,
        )
    except UserWarning as warn:
        print(
            warn.args[0]
            + "for entry with id: "
            + comp.identifier
        )
    if (identifier := result.get("identifier")) is not None:
        result["_id"] = identifier
        del result["identifier"]
    return result


def dict_to_component(content: dict) -> Component:
    if (tags := content.get("tags")) is not None:
        content["tags"] = set(tags)
    if (identifier := content.get("_id")) is not None:
        content["identifier"] = identifier
        del content["_id"]
    return Component(**content)


def component_to_filter(comp: Component, prefix: list[str] = None) -> dict:
    attr_filter = dict()
    if comp is None:
        return attr_filter

    if prefix is None:
        prefix = []

    fields = None
    if issubclass(comp.__class__, BaseModel):
        fields = comp.model_fields
    elif isinstance(comp, dict):
        fields = comp

    for attr, field in fields.items():
        if attr in {"identifier"}:
            continue
        if isinstance(field, FieldInfo):
            field = cast(FieldInfo, field)
            if (content := field.default) is None:
                continue
        elif isinstance(field, Component):
            new_prefix = [*prefix, attr]
            attr_filter.update(component_to_filter(field, new_prefix))

        if attr in {"properties", "composition"}:
            new_prefix = [*prefix, attr]
            attr_filter.update(component_to_filter(content, new_prefix))
        else:
            attr_name = ".".join(prefix + [attr])
            attr_filter.update({attr_name: {"$exists": True}})
    return attr_filter

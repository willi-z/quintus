import pytest
from pydantic import BaseModel
from quintus.structures import Component, Measurement
from quintus.structures.helpers import component_to_dict, component_to_filter


class Measurments(BaseModel):
    potential_vs_Li: Measurement = Measurement()
    thickness: Measurement = Measurement()
    density: Measurement = Measurement()


class OnlyProperties(Component):
    properties: dict[str, Measurement] = Measurments()


class Components(BaseModel):
    a: Component = Component()
    b: Component = Component(properties=Measurments().model_dump())


class OnlyComposite(Component):
    composition: dict[str, Component] = Components()


class OnlyComposite2(Component):
    composition: dict[str, Component] = {"a": Component(), "b": Component()}


@pytest.mark.parametrize("comp, result", [(OnlyComposite2(), {})])
def test_component_to_dict(comp: Component, result: dict):
    result["_id"] = comp.identifier
    assert component_to_dict(comp) == result


@pytest.mark.parametrize(
    "comp, result",
    [
        (
            OnlyProperties(),
            {
                "$and": [
                    {"properties.potential_vs_Li": {"$exists": True}},
                    {"properties.thickness": {"$exists": True}},
                    {"properties.density": {"$exists": True}},
                ]
            },
        ),
        (
            OnlyComposite(),
            {
                "$and": [
                    {"composition.a": {"$exists": True}},
                    {"composition.b": {"$exists": True}},
                ]
            },
        ),
        (
            OnlyComposite2(),
            {
                "$and": [
                    {"composition.a": {"$exists": True}},
                    {"composition.b": {"$exists": True}},
                ]
            },
        ),
    ],
)
def test_component_to_filter(comp: Component, result):
    assert component_to_filter(comp) == result

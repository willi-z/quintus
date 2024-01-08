from .measurement import Measurement
from pydantic import BaseModel, ConfigDict, field_serializer
import warnings


class Component(BaseModel):
    model_config = ConfigDict(extra="allow")
    identifier: str | None = None  # Field(default_factory=generate_id)
    name: str | None = None
    description: str | None = None
    tags: set[str] | None = None
    properties: dict[str, Measurement] | None = None
    composition: dict[str, "Component"] | None = None

    @field_serializer("tags")
    def serialize_tags(self, tags: set[str], _info):
        if tags is not None:
            return list(self.tags)
        else:
            return None

    def is_valid(self) -> bool:
        # if self.name is None:
        #    return False
        if self.composition is not None:
            for component in self.composition.values():
                if not component.is_valid():
                    return False
        return True

    def is_empty(self) -> bool:
        if self.name is not None:
            return False
        if self.description is not None:
            return False
        if self.tags is not None:
            if len(self.tags) > 0:
                return False

        if self.properties is not None:
            for measu in self.properties.values():
                if not measu.is_empty():
                    return False

        if self.composition is not None:
            for comp in self.composition.values():
                if not comp.is_empty():
                    return False
        return True

    def clear_empty(self) -> None:
        if self.properties is not None:
            keys = [k for k, v in self.properties.items() if v.is_empty()]
            for key in keys:
                del self.properties[key]
            if len(self.properties.keys()) == 0:
                self.properties = None

        if self.composition is not None:
            keys = [k for k, v in self.composition.items() if v.is_empty()]
            for key in keys:
                del self.composition[key]
            if len(self.composition.keys()) == 0:
                self.composition = None

    def warn_if_not_valid(
        self, parent: "Component" = None, composite: list[str] = None
    ) -> None:
        if composite is None:
            composite = []

        if self.name is None:
            if parent is not None:
                pass
                """
                warnings.warn(
                    f"Composite name with path '{composite}' "
                    + f"from component {parent.name} "
                    + "is not known!",
                    RuntimeWarning,
                )
                """
            else:
                warnings.warn("Component name is not known!", RuntimeWarning)
            return
        if self.composition is not None:
            for comp, component in self.composition.items():
                component.warn_if_not_valid(self, composite + [comp])

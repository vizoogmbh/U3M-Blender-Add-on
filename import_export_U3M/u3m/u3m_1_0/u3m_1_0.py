from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict
from .. import tools
from .material.material import Material


class Schema(Enum):
    THE_10 = "1.0"


@dataclass
class U3M_1_0:
    material: Material
    schema: Schema
    custom: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> U3M_1_0:
        assert isinstance(obj, dict)
        material = Material.from_dict(obj.get("material"), error_handler)
        schema = Schema(obj.get("schema"))
        custom = tools.from_union(
            [tools.from_none, lambda x: tools.from_dict(lambda x: x, x)],
            obj.get("custom"),
        )
        return U3M_1_0(material, schema, custom)

    def to_dict(self, error_handler: Any) -> dict:
        result: dict = {}
        result["material"] = tools.to_class_with_errors(
            Material, self.material, error_handler
        )
        result["schema"] = tools.to_enum(Schema, self.schema)
        result["custom"] = tools.from_union(
            [tools.from_none, lambda x: tools.from_dict(lambda x: x, x)], self.custom
        )
        return result

    def get_material(self) -> Material:
        return self.material

    def get_schema(self) -> Schema:
        return tools.to_enum(Schema, self.schema)

    def get_custom(self):
        return self.custom


def U3M_1_0_from_dict(s: Any, error_handler: Any) -> U3M_1_0:
    return U3M_1_0.from_dict(s, error_handler)


def U3M_1_0_to_dict(x: U3M_1_0, error_handler: Any) -> Any:
    return tools.to_class_with_errors(U3M_1_0, x, error_handler)

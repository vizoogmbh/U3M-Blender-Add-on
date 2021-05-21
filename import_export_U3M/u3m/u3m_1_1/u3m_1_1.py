
from dataclasses import dataclass
from typing import Any, Optional, List, Dict, TypeVar, Type, cast, Callable
from enum import Enum
from datetime import datetime
from import_export_U3M.u3m import tools as U3M
from .material.material import Material


class Schema(Enum):
    THE_11 = "1.1"


@dataclass
class U3M_1_1:
    material: Material
    schema: Schema
    custom: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'U3M_1_1':
        assert isinstance(obj, dict)
        material = Material.from_dict(obj.get("material"), error_handler)
        schema = Schema(obj.get("schema"))
        custom = U3M.from_union(
            [U3M.from_none, lambda x: U3M.from_dict(lambda x: x, x)], obj.get("custom"))
        return U3M_1_1(material, schema, custom)

    def to_dict(self, error_handler: Any) -> dict:
        result: dict = {}
        result["material"] = U3M.to_class_with_errors(
            Material, self.material, error_handler)
        result["schema"] = U3M.to_enum(Schema, self.schema)
        result["custom"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.from_dict(lambda x: x, x)], self.custom)
        return result

    def get_material(self) -> Material:
        return self.material

    def get_schema(self) -> Schema:
        return U3M.to_enum(Schema, self.schema)

    def get_custom(self):
        return self.custom


def U3M_1_1_from_dict(s: Any, error_handler: Any) -> U3M_1_1:
    return U3M_1_1.from_dict(s, error_handler)


def U3M_1_1_to_dict(x: U3M_1_1, error_handler: Any) -> Any:
    return U3M.to_class_with_errors(U3M_1_1, x, error_handler)

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
import uuid
from uuid import UUID
from datetime import datetime
from import_export_U3M.u3m import tools as U3M
from .visualisation import Visualisation


class UUID4:
    def __init__(self, id, error_handler):
        if self.validate_uuid4(id):
            self.id = id
        else:
            error_handler.handle("invalid_id")
            self.create_new_uuid4()

    def validate_uuid4(self, uuid_string):
        try:
            val = UUID(uuid_string)
        except Exception:
            return False
        return val.hex == uuid_string.replace('-', '').replace('{', '').replace('}', '').lower()

    def create_new_uuid4(self):
        self.id = str(uuid.uuid4())

    def get_id(self):
        return self.id


class MaterialName:
    def __init__(self, name, error_handler):
        if self.validate_name(name):
            self.name = name
        else:
            error_handler.handle("invalid_mat_name")
            self.name = "unnamed_material"

    def validate_name(self, name):
        return len(name) > 0

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name


class Date:
    def __init__(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def set_date(self):
        self.date = datetime.today()


@dataclass
class Material:
    created: Date
    description: str
    id: UUID4
    modified: Date
    name: MaterialName
    back: Optional[Visualisation] = None
    front: Optional[Visualisation] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'Material':
        assert isinstance(obj, dict)
        created = Date(U3M.from_datetime(obj.get("created"), error_handler))
        description = U3M.from_str(obj.get("description"))
        id = UUID4(U3M.from_str(obj.get("id")), error_handler)
        modified = Date(U3M.from_datetime(obj.get("modified"), error_handler))
        name = MaterialName(U3M.from_str(obj.get("name")), error_handler)
        back = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, Visualisation.from_dict], obj.get("back"), error_handler)
        front = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, Visualisation.from_dict], obj.get("front"), error_handler)
        return Material(created, description, id, modified, name, back, front)

    def to_dict(self, error_handler: Any) -> dict:
        result: dict = {}
        result["created"] = U3M.date_parser.write(
            self.get_created(), error_handler)
        result["description"] = U3M.from_str(self.description)
        result["id"] = U3M.from_str(self.id.get_id())
        result["modified"] = U3M.date_parser.write(
            self.modified.get_date(), error_handler)
        result["name"] = U3M.from_str(self.name.get_name())
        result["back"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(Visualisation, x)], self.back)
        result["front"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(Visualisation, x)], self.front)
        return result

    def set_created(self):
        self.created.set_date()

    def get_created(self) -> datetime:
        return self.created.get_date()

    def get_created_as_str(self) -> str:
        return U3M.date_parser.write(self.get_created())

    def update(self):
        self.set_modified()
        self.set_id()

    def get_description(self) -> str:
        return self.description

    def set_description(self, some_str):
        self.update()
        self.description = some_str

    def get_id(self) -> str:
        return self.id.get_id()

    def set_id(self):
        self.id.create_new_uuid4()

    def get_modified(self) -> datetime:
        return self.modified.get_date()

    def set_modified(self):
        self.modified.set_date()

    def get_name(self) -> str:
        return self.name.get_name()

    def set_name(self, new_name):
        self.update()
        self.set_created()
        self.name.set_name(new_name)

    def get_back(self) -> Visualisation:
        return self.back

    def set_back(self, back):
        self.update()
        self.back = back

    def get_front(self) -> Visualisation:
        return self.front

    def set_front(self, front):
        self.update()
        self.front = front

    def has_front(self) -> bool:
        return self.front != None

    def has_back(self) -> bool:
        return self.back != None

    def has_side(self, side) -> bool:
        if side == "front":
            return self.has_front()
        elif side == "back":
            return self.has_back()
        else:
            return False

    def get_side(self, side):
        if side == "front":
            return self.front
        elif side == "back":
            return self.back
        else:
            return None

    def add_side(self, side, error_handler):
        template = {
            "alpha": {
                "constant": 1,
                "texture": None
            },
            "anisotropy_value": {
                "constant": 0,
                "texture": None
            },
            "anisotropy_rotation": {
                "constant": 0,
                "texture": None
            },
            "clearcoat_value": {
                "constant": 0,
                "texture": None
            },
            "clearcoat_normal": {
                "scale": 1.0,
                "image": None
            },
            "clearcoat_roughness": {
                "constant": 0,
                "texture": None
            },
            "ior": {
                "constant": 1.4,
                "texture": None
            },
            "metalness": {
                "constant": 0,
                "texture": None
            },
            "normal": {
                "scale": 1.0,
                "image": None
            },
            "displacement": {
                "constant": 0,
                "texture": None
            },
            "roughness": {
                "constant": 0.7,
                "texture": None
            },
            "sheen_value": {
                "constant": 0,
                "texture": None
            },
            "sheen_tint": {
                "constant": 0,
                "texture": None
            },
            "specular_value": {
                "constant": 0.5,
                "texture": None
            },
            "specular_tint": {
                "constant": 0,
                "texture": None
            },
            "subsurface_radius": {
                "constant": 0,
                "texture": None
            },
            "subsurface_value": {
                "constant": 0,
                "texture": None
            },
            "transmission": {
                "constant": 0,
                "texture": None
            },
            "basecolor": {
                "constant": {
                    "r": 1,
                    "g": 1,
                    "b": 1
                },
                "texture": None
            },
            "subsurface_color": {
                "constant": {
                    "r": 1,
                    "g": 1,
                    "b": 1
                },
                "texture": None
            },
            "shader": "principled",
            "preview": None
        }
        
        if side == "front":
            self.front = Visualisation.from_dict(template, error_handler)
        elif side == "back":
            self.back = Visualisation.from_dict(template, error_handler)

    def remove_side(self, side):
        if side == "front":
            self.front = None
        elif side == "back":
            self.back = None
        elif side == "side":
            self.side = None
        else:
            pass
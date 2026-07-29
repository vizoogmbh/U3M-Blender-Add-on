from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List
from ... import tools


class PartType(Enum):
    ABACA = "Abaca"
    ACETATE = "Acetate"
    ACRYLIC = "Acrylic"
    ALFA = "Alfa"
    ALGINATE = "Alginate"
    ALPACA = "Alpaca"
    ALUMINIUM = "Aluminium"
    ANGORA = "Angora"
    ARAMID = "Aramid"
    BEAVER = "Beaver"
    CAMELHAIR = "Camelhair"
    CASHMERE = "Cashmere"
    COTTON = "Cotton"
    CUPRO = "Cupro"
    ELASTANE = "Elastane"
    GUANACO = "Guanaco"
    HARDWARE = "Hardware"
    HEMP = "Hemp"
    JUTE = "Jute"
    LINEN = "Linen"
    LLAMA = "Llama"
    LYCRA = "Lycra"
    LYOCELL = "Lyocell"
    MERIL = "Meril"
    METALLIC_FIBRE = "Metallic Fibre"
    METALLISED_POLYESTER = "Metallised Polyester"
    MICROPOLYPCH = "Micropolypch"
    MODACRYLIC = "Modacrylic"
    MODAL = "Modal"
    MODAL_COTTON = "Modal Cotton"
    MOHAIR = "Mohair"
    NEOPRENE = "Neoprene"
    NYLON = "Nylon"
    ORGANIC_COTTON = "Organic cotton"
    OTHER = "other"
    POLYACRYL = "Polyacryl"
    POLYAMID = "Polyamid"
    POLYESTER = "Polyester"
    POLYETHYLENE = "Polyethylene"
    POLYPROPYLEN = "Polypropylen"
    POLYTASLAN = "Polytaslan"
    RAMIE = "Ramie"
    RAYON = "Rayon"
    RECYCLED_COTTON = "Recycled Cotton"
    RECYCLED_POLYAMIDE = "Recycled Polyamide"
    RECYCLED_POLYESTER = "Recycled Polyester"
    SILK = "Silk"
    SPANDEX = "Spandex"
    TACTEL = "Tactel"
    TRIACETATE = "Triacetate"
    UNKNOWN = "unknown"
    VICUGNA = "Vicugna"
    VINYL = "Vinyl"
    VIRGIN_WOOL = "Virgin Wool"
    WILD_SILK = "Wild Silk"
    WOOL = "Wool"
    YACK = "Yack"


@dataclass
class CompositionPart:
    ratio: float
    type: PartType
    """user defined additional name e.g. bio-cotton"""
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "CompositionPart":
        assert isinstance(obj, dict)
        ratio = tools.from_float(obj.get("ratio"))
        type = PartType(obj.get("type"))
        name = tools.from_union([tools.from_none, tools.from_str], obj.get("name"))
        return CompositionPart(ratio, type, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ratio"] = tools.to_float(self.ratio)
        result["type"] = tools.to_enum(PartType, self.type)
        result["name"] = tools.from_union([tools.from_none, tools.from_str], self.name)
        return result


@dataclass
class Composition:
    """must have at least 1 value & ratio must sum up to 1"""

    parts: List[CompositionPart]

    @staticmethod
    def from_dict(obj: Any) -> "Composition":
        assert isinstance(obj, dict)
        parts = tools.from_list(CompositionPart.from_dict, obj.get("parts"))
        return Composition(parts)

    def to_dict(self) -> dict:
        result: dict = {}
        result["parts"] = tools.from_list(
            lambda x: tools.to_class(CompositionPart, x), self.parts
        )
        return result


class ConstructionType(Enum):
    CANVAS = "Canvas"
    DOBBY = "Dobby"
    DOUBLEKNIT = "Doubleknit"
    DOUBLEWEAVE = "Doubleweave"
    ENGINEERED = "Engineered"
    FLEECE = "Fleece"
    FRENCH_TERRY = "French terry"
    INTERLOCK = "Interlock"
    JACQUARD = "Jacquard"
    MESH = "Mesh"
    OTHER = "other"
    OXFORD = "Oxford"
    PIQUE = "Pique"
    PLAIN_WEAVE = "Plain weave"
    POLARFLEECE = "Polarfleece"
    POPLIN = "Poplin"
    RASCHEL = "Raschel"
    RIPSTOP = "Ripstop"
    SATIN = "Satin"
    SINGLE_JERSEY = "Single jersey"
    SPACER = "Spacer"
    TAF_FETA = "TafFeta"
    TERRY_LOOP = "Terry loop"
    THE_1_X_1_FLATKNIT = "1 x 1 flatknit"
    THE_1_X_1_RIB = "1 x 1 rib"
    THE_2_X_2_RIB = "2 x 2 rib"
    THE_4_X_2_RIB = "4 x 2 rib"
    TOWEL = "Towel"
    TRICOT = "Tricot"
    TWILL = "Twill"
    TWILL_LEFT_HAND_S = "Twill - left hand (S)"
    TWILL_RIGHT_HAND_Z = "Twill - right hand (Z)"
    UNKNOWN = "unknown"
    VELOUR = "Velour"
    WAFFLE = "Waffle"


@dataclass
class Construction:
    type: ConstructionType
    """user defined additional name e.g. woven"""
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "Construction":
        assert isinstance(obj, dict)
        type = ConstructionType(obj.get("type"))
        name = tools.from_union([tools.from_none, tools.from_str], obj.get("name"))
        return Construction(type, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = tools.to_enum(ConstructionType, self.type)
        result["name"] = tools.from_union([tools.from_none, tools.from_str], self.name)
        return result


@dataclass
class Devices:
    """relative path to the fab physics file"""

    fab: str

    @staticmethod
    def from_dict(obj: Any) -> "Devices":
        assert isinstance(obj, dict)
        fab = tools.from_str(obj.get("fab"))
        return Devices(fab)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fab"] = tools.from_str(self.fab)
        return result


class MaterialTypeType(Enum):
    ARTWORK = "Artwork"
    ELASTICS = "Elastics"
    KNIT = "Knit"
    LEATHER = "Leather"
    METAL = "Metal"
    OTHER = "other"
    SEAM = "Seam"
    UNKNOWN = "unknown"
    WOOD = "Wood"
    WOVEN = "Woven"


@dataclass
class MaterialType:
    type: MaterialTypeType
    """user defined additional name e.g. veal-leather"""
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "MaterialType":
        assert isinstance(obj, dict)
        type = MaterialTypeType(obj.get("type"))
        name = tools.from_union([tools.from_none, tools.from_str], obj.get("name"))
        return MaterialType(type, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = tools.to_enum(MaterialTypeType, self.type)
        result["name"] = tools.from_union([tools.from_none, tools.from_str], self.name)
        return result


@dataclass
class Physics:
    devices: Devices
    composition: Optional[Composition] = None
    construction: Optional[Construction] = None
    material_type: Optional[MaterialType] = None
    thickness: Optional[float] = None
    weight: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> "Physics":
        assert isinstance(obj, dict)
        devices = Devices.from_dict(obj.get("devices"))
        composition = tools.from_union(
            [tools.from_none, Composition.from_dict], obj.get("composition")
        )
        construction = tools.from_union(
            [tools.from_none, Construction.from_dict], obj.get("construction")
        )
        material_type = tools.from_union(
            [tools.from_none, MaterialType.from_dict], obj.get("material_type")
        )
        thickness = tools.from_union(
            [tools.from_none, tools.from_float], obj.get("thickness")
        )
        weight = tools.from_union(
            [tools.from_none, tools.from_float], obj.get("weight")
        )
        return Physics(
            devices, composition, construction, material_type, thickness, weight
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["devices"] = tools.to_class(Devices, self.devices)
        result["composition"] = tools.from_union(
            [tools.from_none, lambda x: tools.to_class(Composition, x)],
            self.composition,
        )
        result["construction"] = tools.from_union(
            [tools.from_none, lambda x: tools.to_class(Construction, x)],
            self.construction,
        )
        result["material_type"] = tools.from_union(
            [tools.from_none, lambda x: tools.to_class(MaterialType, x)],
            self.material_type,
        )
        result["thickness"] = tools.from_union(
            [tools.from_none, tools.to_float], self.thickness
        )
        result["weight"] = tools.from_union(
            [tools.from_none, tools.to_float], self.weight
        )
        return result

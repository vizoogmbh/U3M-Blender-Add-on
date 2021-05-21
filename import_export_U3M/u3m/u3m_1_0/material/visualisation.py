from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
from import_export_U3M.u3m import tools as U3M
from import_export_U3M.u3m.tools import RelativeFilePath


class RepeatMode(Enum):
    MIRROR_X = "mirror_x"
    MIRROR_XY = "mirror_xy"
    MIRROR_Y = "mirror_y"
    NORMAL = "normal"


@dataclass
class Repeat:
    mode: RepeatMode
    rotation: float

    @staticmethod
    def from_dict(obj: Any) -> 'Repeat':
        assert isinstance(obj, dict)
        mode = RepeatMode(obj.get("mode"))
        rotation = U3M.from_float(obj.get("rotation"))
        return Repeat(mode, rotation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["mode"] = U3M.to_enum(RepeatMode, self.mode)
        result["rotation"] = U3M.to_float(self.rotation)
        return result


@dataclass
class Image:
    dpi: float
    height: float
    path: RelativeFilePath
    repeat: Repeat
    width: float

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'Image':
        assert isinstance(obj, dict)
        dpi = U3M.from_float(obj.get("dpi"))
        height = U3M.from_float(obj.get("height"))
        path = RelativeFilePath(U3M.from_str(obj.get("path")), error_handler)
        repeat = Repeat.from_dict(obj.get("repeat"))
        width = U3M.from_float(obj.get("width"))
        return Image(dpi, height, path, repeat, width)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dpi"] = U3M.to_float(self.dpi)
        result["height"] = U3M.to_float(self.height)
        result["path"] = U3M.from_str(self.path.get_path())
        result["repeat"] = U3M.to_class(Repeat, self.repeat)
        result["width"] = U3M.to_float(self.width)
        return result


@dataclass
class TextureAndNumberTexture:
    factor: float
    image: Image
    offset: float

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumberTexture':
        assert isinstance(obj, dict)
        factor = U3M.from_float(obj.get("factor"))
        image = Image.from_dict(obj.get("image"), error_handler)
        offset = U3M.from_float(obj.get("offset"))
        return TextureAndNumberTexture(factor, image, offset)

    def to_dict(self) -> dict:
        result: dict = {}
        result["factor"] = U3M.to_float(self.factor)
        result["image"] = U3M.to_class(Image, self.image)
        result["offset"] = U3M.to_float(self.offset)
        return result


@dataclass
class TextureAndNumber:
    constant: float
    texture: Optional[TextureAndNumberTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumberTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumberTexture, x)], self.texture)
        return result

    def add_texture(self):
        template = {'factor': 0, 'image': {'dpi': 0.0, 'height': 1.0, 'path': 'none', 'repeat': {
            'mode': 'normal', 'rotation': 0}, 'width': 1.0}, 'offset': 0}
        self.texture = U3M.from_union(
            [U3M.from_none, TextureAndNumberTexture.from_dict], template)

    def remove_texture(self):
        self.texture = None


@dataclass
class ColorRGB:
    b: float
    g: float
    r: float

    @staticmethod
    def from_dict(obj: Any) -> 'ColorRGB':
        assert isinstance(obj, dict)
        b = U3M.from_float(obj.get("b"))
        g = U3M.from_float(obj.get("g"))
        r = U3M.from_float(obj.get("r"))
        return ColorRGB(b, g, r)

    def to_dict(self) -> dict:
        result: dict = {}
        result["b"] = U3M.to_float(self.b)
        result["g"] = U3M.to_float(self.g)
        result["r"] = U3M.to_float(self.r)
        return result


class TextureMode(Enum):
    ADD = "add"
    DIVIDE = "divide"
    MAX = "max"
    MIN = "min"
    MULTIPLY = "multiply"
    OVERLAY = "overlay"
    SUBTRACT = "subtract"


@dataclass
class TextureAndColorTexture:
    factor: ColorRGB
    image: Image
    mode: TextureMode

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndColorTexture':
        assert isinstance(obj, dict)
        factor = ColorRGB.from_dict(obj.get("factor"))
        image = Image.from_dict(obj.get("image"), error_handler)
        mode = TextureMode(obj.get("mode"))
        return TextureAndColorTexture(factor, image, mode)

    def to_dict(self) -> dict:
        result: dict = {}
        result["factor"] = U3M.to_class(ColorRGB, self.factor)
        result["image"] = U3M.to_class(Image, self.image)
        result["mode"] = U3M.to_enum(TextureMode, self.mode)
        return result


@dataclass
class TextureAndColor:
    constant: ColorRGB
    texture: Optional[TextureAndColorTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndColor':
        assert isinstance(obj, dict)
        constant = ColorRGB.from_dict(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndColorTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndColor(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_class(ColorRGB, self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndColorTexture, x)], self.texture)
        return result

    def add_texture(self, error_handler):
        template = {
            "factor": {
                "b": 1.0,
                "g": 1.0,
                "r": 1.0
            },
            "image": {
                "dpi": 1.0,
                "height": 1.0,
                "path": "none",
                        "repeat": {
                            "mode": "normal",
                            "rotation": 0.0
                        },
                "width": 1.0
            },
            "mode": "multiply"
        }
        self.texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndColorTexture.from_dict], template, error_handler)

    def remove_texture(self):
        self.texture = None


class Shader(Enum):
    PRINCIPLED = "principled"


@dataclass
class Visualisation:
    alpha: Optional[TextureAndNumber] = None
    anisotropy_rotation: Optional[TextureAndNumber] = None
    anisotropy_value: Optional[TextureAndNumber] = None
    basecolor: Optional[TextureAndColor] = None
    clearcoat_normal: Optional[TextureAndNumber] = None
    clearcoat_roughness: Optional[TextureAndNumber] = None
    clearcoat_value: Optional[TextureAndNumber] = None
    displacement: Optional[TextureAndNumber] = None
    ior: Optional[TextureAndNumber] = None
    metalness: Optional[TextureAndNumber] = None
    normal: Optional[TextureAndNumber] = None
    roughness: Optional[TextureAndNumber] = None
    shader: Optional[Shader] = None
    sheen_tint: Optional[TextureAndNumber] = None
    sheen_value: Optional[TextureAndNumber] = None
    specular_tint: Optional[TextureAndNumber] = None
    specular_value: Optional[TextureAndNumber] = None
    subsurface_color: Optional[TextureAndColor] = None
    subsurface_radius: Optional[TextureAndNumber] = None
    subsurface_value: Optional[TextureAndNumber] = None
    transmission: Optional[TextureAndNumber] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'Visualisation':
        assert isinstance(obj, dict)
        alpha = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("alpha"), error_handler)
        anisotropy_rotation = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("anisotropy_rotation"), error_handler)
        anisotropy_value = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("anisotropy_value"), error_handler)
        basecolor = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndColor.from_dict], obj.get("basecolor"), error_handler)
        clearcoat_normal = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("clearcoat_normal"), error_handler)
        clearcoat_roughness = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("clearcoat_roughness"), error_handler)
        clearcoat_value = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("clearcoat_value"), error_handler)
        displacement = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("displacement"), error_handler)
        ior = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("ior"), error_handler)
        metalness = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("metalness"), error_handler)
        normal = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("normal"), error_handler)
        roughness = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("roughness"), error_handler)
        shader = U3M.from_union([Shader, U3M.from_none], obj.get("shader"))
        sheen_tint = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("sheen_tint"), error_handler)
        sheen_value = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("sheen_value"), error_handler)
        specular_tint = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("specular_tint"), error_handler)
        specular_value = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("specular_value"), error_handler)
        subsurface_color = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndColor.from_dict], obj.get("subsurface_color"), error_handler)
        subsurface_radius = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("subsurface_radius"), error_handler)
        subsurface_value = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("subsurface_value"), error_handler)
        transmission = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, TextureAndNumber.from_dict], obj.get("transmission"), error_handler)
        return Visualisation(alpha, anisotropy_rotation, anisotropy_value, basecolor, clearcoat_normal, clearcoat_roughness, clearcoat_value, displacement, ior, metalness, normal, roughness, shader, sheen_tint, sheen_value, specular_tint, specular_value, subsurface_color, subsurface_radius, subsurface_value, transmission)

    def to_dict(self) -> dict:
        result: dict = {}
        result["alpha"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.alpha)
        result["anisotropy_rotation"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.anisotropy_rotation)
        result["anisotropy_value"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.anisotropy_value)
        result["basecolor"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndColor, x)], self.basecolor)
        result["clearcoat_normal"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.clearcoat_normal)
        result["clearcoat_roughness"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.clearcoat_roughness)
        result["clearcoat_value"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.clearcoat_value)
        result["displacement"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.displacement)
        result["ior"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.ior)
        result["metalness"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.metalness)
        result["normal"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.normal)
        result["roughness"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.roughness)
        result["shader"] = U3M.from_union(
            [lambda x: U3M.to_enum(Shader, x), U3M.from_none], self.shader)
        result["sheen_tint"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.sheen_tint)
        result["sheen_value"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.sheen_value)
        result["specular_tint"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.specular_tint)
        result["specular_value"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.specular_value)
        result["subsurface_color"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndColor, x)], self.subsurface_color)
        result["subsurface_radius"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.subsurface_radius)
        result["subsurface_value"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.subsurface_value)
        result["transmission"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(TextureAndNumber, x)], self.transmission)
        return result

    def get(self, viz_prop):
        if viz_prop == "alpha":
            return self.alpha
        elif viz_prop == "anisotropy_rotation":
            return self.anisotropy_rotation
        elif viz_prop == "anisotropy_value":
            return self.anisotropy_value
        elif viz_prop == "basecolor":
            return self.basecolor
        elif viz_prop == "clearcoat_normal":
            return self.clearcoat_normal
        elif viz_prop == "clearcoat_roughness":
            return self.clearcoat_roughness
        elif viz_prop == "clearcoat_value":
            return self.clearcoat_value
        elif viz_prop == "displacement":
            return self.displacement
        elif viz_prop == "ior":
            return self.ior
        elif viz_prop == "metalness":
            return self.metalness
        elif viz_prop == "normal":
            return self.normal
        elif viz_prop == "roughness":
            return self.roughness
        elif viz_prop == "shader":
            return self.shader
        elif viz_prop == "sheen_tint":
            return self.sheen_tint
        elif viz_prop == "sheen_value":
            return self.sheen_value
        elif viz_prop == "specular_tint":
            return self.specular_tint
        elif viz_prop == "specular_value":
            return self.specular_value
        elif viz_prop == "subsurface_color":
            return self.subsurface_color
        elif viz_prop == "subsurface_radius":
            return self.subsurface_radius
        elif viz_prop == "subsurface_value":
            return self.subsurface_value
        elif viz_prop == "transmission":
            return self.transmission

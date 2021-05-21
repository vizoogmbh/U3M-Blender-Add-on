from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict
import uuid
from uuid import UUID
from datetime import datetime
from import_export_U3M.u3m import tools as U3M
from import_export_U3M.u3m.tools import RelativeFilePath


@dataclass
class ImageDPI:
    x: float
    y: float

    @staticmethod
    def from_dict(obj: Any) -> 'ImageDPI':
        assert isinstance(obj, dict)
        x = U3M.from_float(obj.get("x"))
        y = U3M.from_float(obj.get("y"))
        return ImageDPI(x, y)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = U3M.to_float(self.x)
        result["y"] = U3M.to_float(self.y)
        return result


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
    """grayscale image without colorspace (do not convert)!, if multiple channels are given has
    to be converted to grayscale by averaging the 3 channels

    color image, has to be converted to u3m standard colorspace before use

    3 channel image without colorspace (do not convert)!, may need renormalizing in the shader
    """
    dpi: ImageDPI
    height: float
    """relative path to the image file"""
    path: RelativeFilePath
    repeat: Repeat
    width: float

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'Image':
        assert isinstance(obj, dict)
        dpi = ImageDPI.from_dict(obj.get("dpi"))
        height = U3M.from_float(obj.get("height"))
        path = RelativeFilePath(U3M.from_str(obj.get("path")), error_handler)
        repeat = Repeat.from_dict(obj.get("repeat"))
        width = U3M.from_float(obj.get("width"))
        return Image(dpi, height, path, repeat, width)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dpi"] = U3M.to_class(ImageDPI, self.dpi)
        result["height"] = U3M.to_float(self.height)
        result["path"] = U3M.from_str(self.path.get_path())
        result["repeat"] = U3M.to_class(Repeat, self.repeat)
        result["width"] = U3M.to_float(self.width)
        return result


@dataclass
class ScalarTexture:
    factor: float
    """grayscale image without colorspace (do not convert)!, if multiple channels are given has
    to be converted to grayscale by averaging the 3 channels
    """
    image: Image
    offset: float

    @staticmethod
    def from_dict(obj: Any, error_handler) -> 'ScalarTexture':
        assert isinstance(obj, dict)
        factor = U3M.from_float(obj.get("factor"))
        image = Image.from_dict(obj.get("image"), error_handler)
        offset = U3M.from_float(obj.get("offset"))
        return ScalarTexture(factor, image, offset)

    def to_dict(self) -> dict:
        result: dict = {}
        result["factor"] = U3M.to_float(self.factor)
        result["image"] = U3M.to_class(Image, self.image)
        result["offset"] = U3M.to_float(self.offset)
        return result


@dataclass
class TextureAndNumber01_1:
    constant: float
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber01_1':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber01_1(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None

    def add_texture(self, error_handler):
        template = {
            "constant": 1.0,
            "texture": {
                "factor": 0.0,
                "image": {
                    "dpi": {
                        "x": 0.0,
                        "y": 0.0
                    },
                    "height": 1.0,
                    "path": "none",
                    "repeat": {
                            "mode": "normal",
                            "rotation": 0
                    },
                    "width": 1.0
                },
                "offset": 0
            }
        }
        self.texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], template, error_handler)


@dataclass
class TextureAndNumber01_0:
    """value is in percent, to get to degree, multiply by 360"""
    constant: 0
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber01_0':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber01_0(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None

    def add_texture(self, error_handler):
        template = {
            "constant": 0.0,
            "texture": {
                "factor": 0.0,
                "image": {
                    "dpi": {
                        "x": 0.0,
                        "y": 0.0
                    },
                    "height": 1.0,
                    "path": "none",
                    "repeat": {
                            "mode": "normal",
                            "rotation": 0
                    },
                    "width": 1.0
                },
                "offset": 0
            }
        }
        self.texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], template, error_handler)


@dataclass
class TextureAndNumber0:
    constant: 0
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber0':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber0(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None

    def add_texture(self, error_handler):
        template = {
            "constant": 1.0,
            "texture": {
                "factor": 0.0,
                "image": {
                    "dpi": {
                        "x": 0.0,
                        "y": 0.0
                    },
                    "height": 1.0,
                    "path": "none",
                    "repeat": {
                            "mode": "normal",
                            "rotation": 0
                    },
                    "width": 1.0
                },
                "offset": 0
            }
        }
        self.texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], template, error_handler)


@dataclass
class ColorRGB:
    """color value in u3m standard colorspace

    additional factor, in u3m standard colorspace
    """
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


class ColorTextureMode(Enum):
    ADD = "add"
    DIVIDE = "divide"
    MAX = "max"
    MIN = "min"
    MULTIPLY = "multiply"
    OVERLAY = "overlay"
    SUBTRACT = "subtract"


@dataclass
class ColorTexture:
    """additional factor, in u3m standard colorspace"""
    factor: ColorRGB
    """color image, has to be converted to u3m standard colorspace before use"""
    image: Image
    mode: ColorTextureMode

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'ColorTexture':
        assert isinstance(obj, dict)
        factor = ColorRGB.from_dict(obj.get("factor"))
        image = Image.from_dict(obj.get("image"), error_handler)
        mode = ColorTextureMode(obj.get("mode"))
        return ColorTexture(factor, image, mode)

    def to_dict(self) -> dict:
        result: dict = {}
        result["factor"] = U3M.to_class(ColorRGB, self.factor)
        result["image"] = U3M.to_class(Image, self.image)
        result["mode"] = U3M.to_enum(ColorTextureMode, self.mode)
        return result


@dataclass
class TextureAndColor:
    constant: ColorRGB
    texture: Optional[ColorTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndColor':
        assert isinstance(obj, dict)
        constant = ColorRGB.from_dict(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ColorTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndColor(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_class(ColorRGB, self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ColorTexture, x)], self.texture)
        return result


@dataclass
class Constant:
    """3 component vector, may need renormalizing in the shader"""
    x: float
    y: float
    z: float

    @staticmethod
    def from_dict(obj: Any) -> 'Constant':
        assert isinstance(obj, dict)
        x = U3M.from_float(obj.get("x"))
        y = U3M.from_float(obj.get("y"))
        z = U3M.from_float(obj.get("z"))
        return Constant(x, y, z)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = U3M.to_float(self.x)
        result["y"] = U3M.to_float(self.y)
        result["z"] = U3M.to_float(self.z)
        return result


@dataclass
class NormalTexture:
    """3 channel image without colorspace (do not convert)!, may need renormalizing in the shader"""
    image: Image
    """scaling factor, multiplied to x & y component before renormalization"""
    scale: float

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'NormalTexture':
        assert isinstance(obj, dict)
        image = Image.from_dict(obj.get("image"), error_handler)
        scale = U3M.from_float(obj.get("scale"))
        return NormalTexture(image, scale)

    def to_dict(self) -> dict:
        result: dict = {}
        result["image"] = U3M.to_class(Image, self.image)
        result["scale"] = U3M.to_float(self.scale)
        return result

    def remove_texture(self):
        self.texture = None


@dataclass
class TextureAndNormal:
    """3 component vector, may need renormalizing in the shader"""
    constant: Constant
    texture: Optional[NormalTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNormal':
        assert isinstance(obj, dict)
        constant = Constant.from_dict(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, NormalTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNormal(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_class(Constant, self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(NormalTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None


@dataclass
class TextureAndNumber1D4:
    constant: float(1.4)
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber1D4':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber1D4(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None

    def add_texture(self, error_handler):
        template = {
            "constant": 1.0,
            "texture": {
                "factor": 0.0,
                "image": {
                    "dpi": {
                        "x": 0.0,
                        "y": 0.0
                    },
                    "height": 1.0,
                    "path": "none",
                    "repeat": {
                            "mode": "normal",
                            "rotation": 0
                    },
                    "width": 1.0
                },
                "offset": 0
            }
        }
        self.texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], template, error_handler)


@dataclass
class PreviewImageDPI:
    x: float
    y: float

    @staticmethod
    def from_dict(obj: Any) -> 'PreviewImageDPI':
        assert isinstance(obj, dict)
        x = U3M.from_float(obj.get("x"))
        y = U3M.from_float(obj.get("y"))
        return PreviewImageDPI(x, y)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = U3M.to_float(self.x)
        result["y"] = U3M.to_float(self.y)
        return result


@dataclass
class PreviewImage:
    dpi: PreviewImageDPI
    height: float
    """relative path to the image file"""
    path: RelativeFilePath
    width: float

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'PreviewImage':
        assert isinstance(obj, dict)
        dpi = PreviewImageDPI.from_dict(obj.get("dpi"))
        height = U3M.from_float(obj.get("height"))
        path = RelativeFilePath(U3M.from_str(obj.get("path")), error_handler)
        width = U3M.from_float(obj.get("width"))
        return PreviewImage(dpi, height, path, width)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dpi"] = U3M.to_class(PreviewImageDPI, self.dpi)
        result["height"] = U3M.to_float(self.height)
        result["path"] = U3M.from_str(self.path.get_path())
        result["width"] = U3M.to_float(self.width)
        return result


@dataclass
class TextureAndNumber0D7:
    constant: float
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber0D7':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber0D7(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None


class Shader(Enum):
    PRINCIPLED = "principled"


@dataclass
class TextureAndNumber0D5:
    """value is defined on the segment [0%, 8%] -> 0.0 equals 0%, and 1.0 equals 8%"""
    constant: float
    texture: Optional[ScalarTexture] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'TextureAndNumber0D5':
        assert isinstance(obj, dict)
        constant = U3M.from_float(obj.get("constant"))
        texture = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, ScalarTexture.from_dict], obj.get("texture"), error_handler)
        return TextureAndNumber0D5(constant, texture)

    def to_dict(self) -> dict:
        result: dict = {}
        result["constant"] = U3M.to_float(self.constant)
        result["texture"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(ScalarTexture, x)], self.texture)
        return result

    def remove_texture(self):
        self.texture = None


@dataclass
class Visualisation:
    alpha: TextureAndNumber01_1
    """value is in percent, to get to degree, multiply by 360"""
    anisotropy_rotation: TextureAndNumber01_0
    anisotropy_value: TextureAndNumber0
    basecolor: TextureAndColor
    clearcoat_normal: TextureAndNormal
    clearcoat_roughness: TextureAndNumber0
    clearcoat_value: TextureAndNumber0
    displacement: TextureAndNumber0
    ior: TextureAndNumber1D4
    metalness: TextureAndNumber01_0
    normal: TextureAndNormal
    roughness: TextureAndNumber0D7
    shader: Shader
    sheen_tint: TextureAndNumber0
    sheen_value: TextureAndNumber0
    specular_tint: TextureAndNumber0
    """value is defined on the segment [0%, 8%] -> 0.0 equals 0%, and 1.0 equals 8%"""
    specular_value: TextureAndNumber0D5
    subsurface_color: TextureAndColor
    subsurface_radius: TextureAndNumber0
    subsurface_value: TextureAndNumber0
    transmission: TextureAndNumber01_0
    preview: Optional[PreviewImage] = None

    @staticmethod
    def from_dict(obj: Any, error_handler: Any) -> 'Visualisation':
        assert isinstance(obj, dict)
        alpha = TextureAndNumber01_1.from_dict(obj.get("alpha"), error_handler)
        anisotropy_rotation = TextureAndNumber01_0.from_dict(
            obj.get("anisotropy_rotation"), error_handler)
        anisotropy_value = TextureAndNumber0.from_dict(
            obj.get("anisotropy_value"), error_handler)
        basecolor = TextureAndColor.from_dict(
            obj.get("basecolor"), error_handler)
        clearcoat_normal = TextureAndNormal.from_dict(
            obj.get("clearcoat_normal"), error_handler)
        clearcoat_roughness = TextureAndNumber0.from_dict(
            obj.get("clearcoat_roughness"), error_handler)
        clearcoat_value = TextureAndNumber0.from_dict(
            obj.get("clearcoat_value"), error_handler)
        displacement = TextureAndNumber0.from_dict(
            obj.get("displacement"), error_handler)
        ior = TextureAndNumber1D4.from_dict(obj.get("ior"), error_handler)
        metalness = TextureAndNumber01_0.from_dict(
            obj.get("metalness"), error_handler)
        normal = TextureAndNormal.from_dict(obj.get("normal"), error_handler)
        roughness = TextureAndNumber0D7.from_dict(
            obj.get("roughness"), error_handler)
        shader = Shader(obj.get("shader"))
        sheen_tint = TextureAndNumber0.from_dict(
            obj.get("sheen_tint"), error_handler)
        sheen_value = TextureAndNumber0.from_dict(
            obj.get("sheen_value"), error_handler)
        specular_tint = TextureAndNumber0.from_dict(
            obj.get("specular_tint"), error_handler)
        specular_value = TextureAndNumber0D5.from_dict(
            obj.get("specular_value"), error_handler)
        subsurface_color = TextureAndColor.from_dict(
            obj.get("subsurface_color"), error_handler)
        subsurface_radius = TextureAndNumber0.from_dict(
            obj.get("subsurface_radius"), error_handler)
        subsurface_value = TextureAndNumber0.from_dict(
            obj.get("subsurface_value"), error_handler)
        transmission = TextureAndNumber01_0.from_dict(
            obj.get("transmission"), error_handler)
        preview = U3M.from_union_with_errors(
            [U3M.from_none_with_errors, PreviewImage.from_dict], obj.get("preview"), error_handler)

        return Visualisation(alpha, anisotropy_rotation, anisotropy_value, basecolor, clearcoat_normal, clearcoat_roughness, clearcoat_value, displacement, ior, metalness, normal, roughness, shader, sheen_tint, sheen_value, specular_tint, specular_value, subsurface_color, subsurface_radius, subsurface_value, transmission, preview)

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

    def to_dict(self) -> dict:
        result: dict = {}
        result["alpha"] = U3M.to_class(TextureAndNumber01_1, self.alpha)
        result["anisotropy_rotation"] = U3M.to_class(
            TextureAndNumber01_0, self.anisotropy_rotation)
        result["anisotropy_value"] = U3M.to_class(
            TextureAndNumber0, self.anisotropy_value)
        result["basecolor"] = U3M.to_class(TextureAndColor, self.basecolor)
        result["clearcoat_normal"] = U3M.to_class(
            TextureAndNormal, self.clearcoat_normal)
        result["clearcoat_roughness"] = U3M.to_class(
            TextureAndNumber0, self.clearcoat_roughness)
        result["clearcoat_value"] = U3M.to_class(
            TextureAndNumber0, self.clearcoat_value)
        result["displacement"] = U3M.to_class(
            TextureAndNumber0, self.displacement)
        result["ior"] = U3M.to_class(TextureAndNumber1D4, self.ior)
        result["metalness"] = U3M.to_class(
            TextureAndNumber01_0, self.metalness)
        result["normal"] = U3M.to_class(TextureAndNormal, self.normal)
        result["roughness"] = U3M.to_class(TextureAndNumber0D7, self.roughness)
        result["shader"] = U3M.to_enum(Shader, self.shader)
        result["sheen_tint"] = U3M.to_class(TextureAndNumber0, self.sheen_tint)
        result["sheen_value"] = U3M.to_class(
            TextureAndNumber0, self.sheen_value)
        result["specular_tint"] = U3M.to_class(
            TextureAndNumber0, self.specular_tint)
        result["specular_value"] = U3M.to_class(
            TextureAndNumber0D5, self.specular_value)
        result["subsurface_color"] = U3M.to_class(
            TextureAndColor, self.subsurface_color)
        result["subsurface_radius"] = U3M.to_class(
            TextureAndNumber0, self.subsurface_radius)
        result["subsurface_value"] = U3M.to_class(
            TextureAndNumber0, self.subsurface_value)
        result["transmission"] = U3M.to_class(
            TextureAndNumber01_0, self.transmission)
        result["preview"] = U3M.from_union(
            [U3M.from_none, lambda x: U3M.to_class(PreviewImage, x)], self.preview)
        return result

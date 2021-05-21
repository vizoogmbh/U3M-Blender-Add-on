# dict key: [parameter name in principled bsdf, location in u3m, default value, shader subnode, node input]

u3m_pbr = {"sides": {
    "front": {
        "id": 1,
        "visualization": None
    },
    "back": {
        "id": 2,
        "visualization": None
    }
},
    "material_properties": {
    "custom": ["custom", ""],
    "name": ["material/name", ""],
    "id": ["material/id", ""],
    "created": ["material/created", ""],
    "modified": ["material/modified", ""],
    "description": ["material/description", ""]
},
    "visualization": {
    "alpha": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Alpha",
        "suffix": "ALPHA",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Alpha'].default_value"],
            "texture": ["/texture/image/path", None, "alpha", "image"],
            "factor": ["/texture/factor", 1, "alpha_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "alpha_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "alpha_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "alpha_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "anisotropy_value": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Anisotropic",
        "suffix": "ANISOTROPY",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Anisotropic'].default_value"],
            "texture": ["/texture/image/path", None, "anisotropy_value", "image"],
            "factor": ["/texture/factor", 1, "anisotropy_value_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "anisotropy_value_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "anisotropy_value_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "anisotropy_value_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "anisotropy_rotation": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Anisotropic Rotation",
        "suffix": "ANISOTROPY_ROTATION",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Anisotropic Rotation'].default_value"],
            "texture": ["/texture/image/path", None, "anisotropy_rotation", "image"],
            "factor": ["/texture/factor", 1, "anisotropy_rotation_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "anisotropy_rotation_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "anisotropy_rotation_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "anisotropy_rotation_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "basecolor": {
        "principled": True,
        "color-space": "sRGB",
        "alias": "Base Color",
        "suffix": "BASE",
        "type": "texture_and_color",
        "editor_level": 0,
        "properties": {
            "constant_r": ["/constant/r", 0.5, "Principled BSDF", "inputs['Base Color'].default_value[0]"],
            "constant_g": ["/constant/g", 0.5, "Principled BSDF", "inputs['Base Color'].default_value[1]"],
            "constant_b": ["/constant/b", 0.5, "Principled BSDF", "inputs['Base Color'].default_value[2]"],
            "texture": ["/texture/image/path", None, "basecolor", "image"],
            "factor_r": ["/texture/factor/r", 1, "basecolor_factor", "inputs[1].default_value[0]"],
            "factor_g": ["/texture/factor/g", 1, "basecolor_factor", "inputs[1].default_value[1]"],
            "factor_b": ["/texture/factor/b", 1, "basecolor_factor", "inputs[1].default_value[2]"],
            "width": ["/texture/image/width", 1, "basecolor_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "basecolor_size", "inputs['Scale'].default_value[1]"],
            "mode": ["/texture/mode", "'MULTIPLY'", "basecolor_factor", "blend_type"]
        }
    },
    "clearcoat_value": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Clearcoat",
        "suffix": "CLEARCOAT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Clearcoat'].default_value"],
            "texture": ["/texture/image/path", None, "clearcoat_value", "image"],
            "factor": ["/texture/factor", 1, "clearcoat_value_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "clearcoat_value_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "clearcoat_value_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "clearcoat_value_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "clearcoat_normal": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Clearcoat Normal",
        "suffix": "CLEARCOAT_NORMAL",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "texture": ["/texture/image/path", None, "clearcoat_normal", "image"],
            "factor": ["/texture/factor", 1, "clearcoat_normal_factor", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "clearcoat_normal_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "clearcoat_normal_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "clearcoat_roughness": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Clearcoat Roughness",
        "suffix": "CLEARCOAT_ROUGHNESS",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Clearcoat Roughness'].default_value"],
            "texture": ["/texture/image/path", None, "clearcoat_roughness", "image"],
            "factor": ["/texture/factor", 1, "clearcoat_roughness_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "clearcoat_roughness_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "clearcoat_roughness_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "clearcoat_roughness_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "metalness": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Metallic",
        "suffix": "MTL",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Metallic'].default_value"],
            "texture": ["/texture/image/path", None, "metalness", "image"],
            "factor": ["/texture/factor", 1, "metalness_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "metalness_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "metalness_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "metalness_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "normal": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Normal",
        "suffix": "NRM",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "texture": ["/texture/image/path", None, "normal", "image"],
            "factor": ["/texture/factor", 1, "normal_factor", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "normal_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "normal_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "displacement": {
        "principled": False,
        "color-space": "Non-Color",
        "alias": "Displacement",
        "suffix": "DISP",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "texture": ["/texture/image/path", None, "displacement", "image"],
            "factor": ["/texture/factor", 1, "displacement_factor", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "displacement_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "displacement_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "roughness": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Roughness",
        "suffix": "ROUGH",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0.5, "Principled BSDF", "inputs['Roughness'].default_value"],
            "texture": ["/texture/image/path", None, "roughness", "image"],
            "factor": ["/texture/factor", 1, "roughness_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "roughness_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "roughness_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "roughness_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "sheen_value": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Sheen",
        "suffix": "SHEEN",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Sheen'].default_value"],
            "texture": ["/texture/image/path", None, "sheen_value", "image"],
            "factor": ["/texture/factor", 1, "sheen_value_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "sheen_value_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "sheen_value_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "sheen_value_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "sheen_tint": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Sheen Tint",
        "suffix": "SHEEN_TINT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0.5, "Principled BSDF", "inputs['Sheen Tint'].default_value"],
            "texture": ["/texture/image/path", None, "sheen_tint", "image"],
            "factor": ["/texture/factor", 1, "sheen_tint_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "sheen_tint_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "sheen_tint_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "sheen_tint_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "specular_value": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Specular",
        "suffix": "SPECULAR",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0.5, "Principled BSDF", "inputs['Specular'].default_value"],
            "texture": ["/texture/image/path", None, "specular_value", "image"],
            "factor": ["/texture/factor", 1, "specular_value_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "specular_value_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "specular_value_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "specular_value_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "specular_tint": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Specular Tint",
        "suffix": "SPECULAR_TINT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Specular Tint'].default_value"],
            "texture": ["/texture/image/path", None, "specular_tint", "image"],
            "factor": ["/texture/factor", 1, "specular_tint_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "specular_tint_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "specular_tint_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "specular_tint_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "subsurface_radius": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Subsurface Radius",
        "suffix": "SUBSURFACE_RADIUS",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Subsurface Radius'].default_value"],
            "texture": ["/texture/image/path", None, "subsurface_radius", "image"],
            "factor": ["/texture/factor", 1, "subsurface_radius_factor", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "subsurface_radius_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "subsurface_radius_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "subsurface_value": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Subsurface",
        "suffix": "SUBSURFACE",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Subsurface'].default_value"],
            "texture": ["/texture/image/path", None, "subsurface_value", "image"],
            "factor": ["/texture/factor", 1, "subsurface_value_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "subsurface_value_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "subsurface_value_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "subsurface_value_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "ior": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "IOR",
        "suffix": "IOR",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 1.45, "Principled BSDF", "inputs['IOR'].default_value"],
            "texture": ["/texture/image/path", None, "ior", "image"],
            "factor": ["/texture/factor", 1, "ior_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "ior_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "ior_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "ior_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "transmission": {
        "principled": True,
        "color-space": "Non-Color",
        "alias": "Transmission",
        "suffix": "TRANSMISSION",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "Principled BSDF", "inputs['Transmission'].default_value"],
            "texture": ["/texture/image/path", None, "transmission", "image"],
            "factor": ["/texture/factor", 1, "transmission_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "transmission_offset", "inputs[0].default_value"],
            "width": ["/texture/image/width", 1, "transmission_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "transmission_size", "inputs['Scale'].default_value[1]"]
        }
    },
    "subsurface_color": {
        "principled": True,
        "color-space": "sRGB",
        "alias": "Subsurface Color",
        "suffix": "SURBSURFACE_COLOR",
        "type": "texture_and_color",
        "editor_level": 1,
        "properties": {
            "constant_r": ["/constant/r", 0.5, "Principled BSDF", "inputs['Subsurface Color'].default_value[0]"],
            "constant_g": ["/constant/g", 0.5, "Principled BSDF", "inputs['Subsurface Color'].default_value[1]"],
            "constant_b": ["/constant/b", 0.5, "Principled BSDF", "inputs['Subsurface Color'].default_value[2]"],
            "texture": ["/texture/image/path", None, "subsurface_color", "image"],
            "factor_r": ["/texture/factor/r", 1, "subsurface_color_factor", "inputs[1].default_value[0]"],
            "factor_g": ["/texture/factor/g", 1, "subsurface_color_factor", "inputs[1].default_value[1]"],
            "factor_b": ["/texture/factor/b", 1, "subsurface_color_factor", "inputs[1].default_value[2]"],
            "width": ["/texture/image/width", 1, "subsurface_color_size", "inputs['Scale'].default_value[0]"],
            "height": ["/texture/image/height", 1, "subsurface_color_size", "inputs['Scale'].default_value[1]"],
            "mode": ["/texture/mode", "'MULTIPLY'", "subsurface_color_factor", "blend_type"]
        }
    }
}
}

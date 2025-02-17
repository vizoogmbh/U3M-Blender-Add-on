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
        "color-space": "Non-Color",
        "alias": "Alpha",
        "suffix": "ALPHA",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['alpha'].default_value"],
            "texture": ["/texture/image/path", None, "alpha", "image"],
            "factor": ["/texture/factor", 1, "alpha_factor", "inputs[1].default_value"],
            "offset": ["/texture/offset", 0, "alpha_offset", "inputs[1].default_value"],
        }
    },
    "anisotropy_value": {
        "color-space": "Non-Color",
        "alias": "Anisotropic",
        "suffix": "ANISOTROPY",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['anisotropy_value'].default_value"]
        }
    },
    "anisotropy_rotation": {
        "color-space": "Non-Color",
        "alias": "Anisotropic Rotation",
        "suffix": "ANISOTROPY_ROTATION",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['anisotropy_rotation'].default_value"]
        }
    },
    "basecolor": {
        "color-space": "sRGB",
        "alias": "Base Color",
        "suffix": "BASE",
        "type": "texture_and_color",
        "editor_level": 0,
        "properties": {
            "constant_r": ["/constant/r", 0.5, "U3M_out", "inputs['basecolor'].default_value[0]"],
            "constant_g": ["/constant/g", 0.5, "U3M_out", "inputs['basecolor'].default_value[1]"],
            "constant_b": ["/constant/b", 0.5, "U3M_out", "inputs['basecolor'].default_value[2]"],
            "texture": ["/texture/image/path", None, "basecolor", "image"],
            "factor_r": ["/texture/factor/r", 1, "basecolor_factor", "inputs[1].default_value[0]"],
            "factor_g": ["/texture/factor/g", 1, "basecolor_factor", "inputs[1].default_value[1]"],
            "factor_b": ["/texture/factor/b", 1, "basecolor_factor", "inputs[1].default_value[2]"],
            "width": ["/texture/image/width", 1, None, None],
            "height": ["/texture/image/height", 1, None, None],
            "mode": ["/texture/mode", "'MULTIPLY'", "basecolor_factor", "blend_type"]
        }
    },
    "clearcoat_value": {
        "color-space": "Non-Color",
        "alias": "Clearcoat",
        "suffix": "CLEARCOAT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['clearcoat_value'].default_value"]
        }
    },
    "clearcoat_normal": {
        "color-space": "Non-Color",
        "alias": "Clearcoat Normal",
        "suffix": "CLEARCOAT_NORMAL",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "factor": ["/texture/factor", 0, "clearcoat_normal_factor", "inputs[0].default_value"]
        }
    },
    "clearcoat_roughness": {
        "color-space": "Non-Color",
        "alias": "Clearcoat Roughness",
        "suffix": "CLEARCOAT_ROUGHNESS",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['clearcoat_roughness'].default_value"]
        }
    },
    "metalness": {
        "color-space": "Non-Color",
        "alias": "Metallic",
        "suffix": "MTL",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['metalness'].default_value"],
            "texture": ["/texture/image/path", None, "metalness", "image"],
            "factor": ["/texture/factor", 1, "metalness_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "metalness_offset", "inputs[0].default_value"]
        }
    },
    "normal": {
        "color-space": "Non-Color",
        "alias": "Normal",
        "suffix": "NRM",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "texture": ["/texture/image/path", None, "normal", "image"],
            "factor": ["/texture/factor", 1, "normal_factor", "inputs[0].default_value"]
        }
    },
    "displacement": {
        "color-space": "Non-Color",
        "alias": "Displacement",
        "suffix": "DISP",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "texture": ["/texture/image/path", None, "displacement", "image"],
            "factor": ["/texture/factor", 0, "displacement_factor", "inputs[0].default_value"]
        }
    },
    "roughness": {
        "color-space": "Non-Color",
        "alias": "Roughness",
        "suffix": "ROUGH",
        "type": "texture_and_number",
        "editor_level": 0,
        "properties": {
            "constant": ["/constant", 0.5, "U3M_out", "inputs['roughness'].default_value"],
            "texture": ["/texture/image/path", None, "roughness", "image"],
            "factor": ["/texture/factor", 1, "roughness_factor", "inputs[0].default_value"],
            "offset": ["/texture/offset", 0, "roughness_offset", "inputs[0].default_value"]
        }
    },
    "sheen_value": {
        "color-space": "Non-Color",
        "alias": "Sheen",
        "suffix": "SHEEN",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['sheen_value'].default_value"]
        } 
    },
    "sheen_tint": {
        "color-space": "Non-Color",
        "alias": "Sheen Tint",
        "suffix": "SHEEN_TINT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0.5, "sheen_tint_factor", "inputs[0].default_value"]
        }
    },
    "specular_value": {
        "color-space": "Non-Color",
        "alias": "Specular",
        "suffix": "SPECULAR",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0.5, "U3M_out", "inputs['specular_value'].default_value"]
        }
    },
    "specular_tint": {
        "color-space": "Non-Color",
        "alias": "Specular Tint",
        "suffix": "SPECULAR_TINT",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "specular_tint_factor", "inputs[0].default_value"]
        }
    },
    "subsurface_radius": {
        "color-space": "Non-Color",
        "alias": "Subsurface Radius",
        "suffix": "SUBSURFACE_RADIUS",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['subsurface_radius'].default_value[0]"]
        }
    },
    "subsurface_value": {
        "color-space": "Non-Color",
        "alias": "Subsurface",
        "suffix": "SUBSURFACE",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['subsurface_value'].default_value"]
        }
    },
    "ior": {
        "color-space": "Non-Color",
        "alias": "IOR",
        "suffix": "IOR",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 1.45, "U3M_out", "inputs['ior'].default_value"]
        }
    },
    "transmission": {
        "color-space": "Non-Color",
        "alias": "Transmission",
        "suffix": "TRANSMISSION",
        "type": "texture_and_number",
        "editor_level": 1,
        "properties": {
            "constant": ["/constant", 0, "U3M_out", "inputs['transmission'].default_value"]
        }
    }
}
}

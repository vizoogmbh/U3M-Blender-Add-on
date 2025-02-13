import os
import copy
from shutil import copyfile
import bpy
from pathlib import Path
from enum import Enum
from . import utils as Blender
from . import shader_template
from .node_builder import ShaderNodeBuilder

blend_modes = {"multiply": "'MULTIPLY'",
               "add": "'ADD'",
               "subtract": "'SUBTRACT'",
               "divide": "'DIVIDE'",
               "max": "'LIGHTEN'",
               "min": "'DARKEN'",
               "overlay": "'OVERLAY'"}

class MaterialAssignmentMode(Enum):
    ACTIVE_ONLY = 1
    LINKED = 2
    SELECTION = 3

def assign_material(material_name, assignment_mode):
    blender_obj = Blender.get_active_obj()

    for m in Blender.get_materials():
        if m.name == material_name:
            m.name += " (Copy)"

    for t in Blender.get_texts():
        if t.name == "U3M_" + material_name:
            t.name += " (Copy)"

    new_mat = bpy.data.materials.new(material_name)
    new_mat.use_nodes = True
    nodes = new_mat.node_tree.nodes
    nodes.clear()

    create_u3m_metadata_node(new_mat)
    match assignment_mode:
        case MaterialAssignmentMode.LINKED:
            assigned_mat = blender_obj.active_material
            for o in Blender.get_objects():
                if o.active_material == assigned_mat:
                    o.active_material = new_mat if o.active_material else blender_obj.active_material
                    if not o.active_material:
                        break
        case MaterialAssignmentMode.SELECTION:
            for obj in Blender.get_selected_objects():
                obj.active_material = new_mat
        case MaterialAssignmentMode.ACTIVE_ONLY:
            blender_obj.active_material = new_mat

def create_u3m_metadata_node(mat):
    metadata_node = mat.node_tree.nodes.new(
        'ShaderNodeScript')
    metadata_node.label = "Metadata"
    metadata_node.name = "Metadata"
    bpy.data.texts.new("U3M")
    metadata_node.script = bpy.data.texts["U3M"]
    metadata_node.location = (-600, -650)


def fill_shader_nodes(u3m_version, u3m_dict, u3m_dir, error_handler):
    for side in shader_template.u3m_pbr["sides"]:
        if Blender.DictQuery(u3m_dict).get("material/" + side) is None:
            continue
        u3m_template = copy.deepcopy(shader_template.u3m_pbr)
        viz_dict = u3m_template["visualization"]
        for param in viz_dict:
            props = viz_dict[param]["properties"]
            for p in props:
                path_prefix = "material/%s/%s" % (side, param)
                if param == "normal" and p == "factor" and u3m_version == "1.1":
                    path_suffix = "/texture/scale"
                else:
                    path_suffix = props[p][0]
                search_str = path_prefix + path_suffix
                val = Blender.DictQuery(u3m_dict).get(search_str)
                if val is not None:
                    if p == "texture":
                        val = os.path.join(u3m_dir, Path(val).as_posix())
                    if p == "mode":
                        val = blend_modes[val]
                    props[p][1] = val
        apply_u3m(viz_dict, side, error_handler)


def apply_u3m(viz_dict, side, error_handler):
    blender_obj = Blender.get_active_obj()
    active_material = blender_obj.active_material
    Blender.set_material_blend_method(active_material, "HASHED")
    Blender.set_material_shadow_method(active_material, "HASHED")
    builder = ShaderNodeBuilder(viz_dict, side)
    builder.build_shader_nodes(active_material)


def collect_and_copy_u3m_data(side, new_material_folder, new_material_name):
    material = Blender.get_active_material()
    active_material_tree = material.node_tree.nodes
    u3m_pbr = copy.deepcopy(shader_template.u3m_pbr)
    group_node = f"U3M_{side}"
    side_dict = u3m_pbr["sides"][side]
    side_dict["visualization"] = copy.deepcopy(u3m_pbr["visualization"])
    viz_dict = side_dict["visualization"]

    for param, param_dict in viz_dict.items():
        props_dict = param_dict["properties"]
        for prop, prop_list in props_dict.items():
            subnode, node_input = prop_list[2], prop_list[3]
            if not subnode or not node_input:
                continue
            if prop == "texture":
                img = active_material_tree[group_node].node_tree.nodes[subnode].image
                if not img:
                    continue
                texture_path, tex_ext = img.filepath, img.file_format
                tex_suffix = param_dict["suffix"]
                if side == "back":
                    new_texture_name = f"{new_material_name}_{tex_suffix}_BACK.{tex_ext}"
                else:
                    new_texture_name = f"{new_material_name}_{tex_suffix}.{tex_ext}"
                prop_list[1] = f"textures/{new_texture_name}"

                texture_path_dst = os.path.join(
                    new_material_folder, "textures", new_texture_name)
                os.makedirs(os.path.dirname(texture_path_dst), exist_ok=True)

                if texture_path != texture_path_dst:
                    copyfile(texture_path, texture_path_dst)

                img.name, img.filepath = new_texture_name, texture_path_dst
                continue
            node_expr = f"nodes['{group_node}'].node_tree.nodes['{subnode}'].{node_input}"
            prop_list[1] = eval(f"bpy.data.materials['{material.name}'].node_tree.{node_expr}")
            if prop == "mode":
                for mode_u3m, mode_blender in blend_modes.items():
                    if mode_blender == f"'{prop_list[1]}'":
                        prop_list[1] = str(mode_u3m)
                        break
    return viz_dict


def has_side(side):
    active_material = Blender.get_active_material()
    principled_node_name = "Principled_BSDF_" + side
    return principled_node_name in active_material.node_tree.nodes

import os
import copy
from shutil import copyfile
import bpy
from pathlib import Path
from . import utils as Blender
from . import shader_template

blend_modes = {"multiply": "'MULTIPLY'",
               "add": "'ADD'",
               "subtract": "'SUBTRACT'",
               "divide": "'DIVIDE'",
               "max": "'LIGHTEN'",
               "min": "'DARKEN'",
               "overlay": "'OVERLAY'"}


editable = {"alpha": ["factor", "offset"],
            "anisotropy_value": ["offset"],
            "anisotropy_rotation": ["factor", "offset"],
            "clearcoat_value": ["offset"],
            "clearcoat_normal": ["factor", "offset"],
            "clearcoat_roughness": ["factor", "offset"],
            "metalness": ["offset"],
            "normal": ["factor"],
            "displacement": ["factor"],
            "roughness": ["offset"],
            "sheen_value": ["offset"],
            "sheen_tint": ["factor", "offset"],
            "specular_value": ["offset"],
            "specular_tint": ["factor", "offset"],
            "subsurface_radius": ["factor", "offset"],
            "subsurface_value": ["offset"],
            "ior": ["factor", "offset"],
            "transmission": ["factor", "offset"],
            "basecolor": ["factor"],
            "subsurface_color": ["factor"]}


def build_shader_group(texture_nodes):
    shader_group = bpy.data.node_groups.new(
        'U3M', 'ShaderNodeTree')
    group_in = shader_group.nodes.new('NodeGroupInput')
    group_in.location = (-400, 0)
    texture_coords_node = shader_group.nodes.new(
        'ShaderNodeTexCoord')
    texture_coords_node.label = "Texture Coords"
    texture_coords_node.location = (-200, 0)
    global_size_node = shader_group.nodes.new(
        'ShaderNodeMapping')
    global_size_node.label = "global_size"
    global_size_node.name = "global_size"
    global_size_node.vector_type = 'TEXTURE'
    global_size_node.location = (0, 0)
    shader_group.links.new(
        texture_coords_node.outputs[2], global_size_node.inputs[0])
    group_out = shader_group.nodes.new('NodeGroupOutput')
    group_out.label = "U3M_out"
    group_out.location = (1200, 0)
    x_location = 200
    y_location = 2000
    for property in texture_nodes:
        y_location -= 300
        size_node = shader_group.nodes.new('ShaderNodeMapping')
        size_node.label = "{}_size".format(property)
        size_node.name = "{}_size".format(property)
        size_node.location = (x_location+100, y_location)
        texture_node = shader_group.nodes.new('ShaderNodeTexImage')
        texture_node.label = property
        texture_node.name = property
        texture_node.location = (x_location, y_location)
        shader_group.links.new(
            global_size_node.outputs[0], texture_node.inputs[0])
        if property not in ["basecolor", "subsurface_radius", "subsurface_color", "normal", "clearcoat_normal", "displacement"]:
            factor_node = shader_group.nodes.new('ShaderNodeMath')
            factor_node.label = "{}_factor".format(property)
            factor_node.name = "{}_factor".format(property)
            factor_node.operation = 'MULTIPLY'
            factor_node.location = (x_location + 400, y_location)
            shader_group.links.new(
                texture_node.outputs[0], factor_node.inputs[1])
            offset_node = shader_group.nodes.new('ShaderNodeMath')
            offset_node.label = "{}_offset".format(property)
            offset_node.name = "{}_offset".format(property)
            offset_node.location = (x_location + 800, y_location)
            shader_group.links.new(
                factor_node.outputs[0], offset_node.inputs[1])
            shader_group.outputs.new('NodeSocketFloat', property)
            shader_group.links.new(
                offset_node.outputs[0], group_out.inputs[texture_nodes.index(property)])
        elif property in ["basecolor", "subsurface_color"]:
            factor_node = shader_group.nodes.new('ShaderNodeMixRGB')
            factor_node.label = "{}_factor".format(property)
            factor_node.name = "{}_factor".format(property)
            factor_node.blend_type = 'MULTIPLY'
            factor_node.location = (x_location + 400, y_location)
            factor_node.inputs["Fac"].default_value = 1.0
            shader_group.outputs.new('NodeSocketColor', property)
            shader_group.links.new(
                texture_node.outputs[0], factor_node.inputs[2])
            shader_group.links.new(
                factor_node.outputs[0], group_out.inputs[texture_nodes.index(property)])
        elif property == "displacement":
            factor_node = shader_group.nodes.new('ShaderNodeMath')
            factor_node.label = "{}_factor".format(property)
            factor_node.name = "{}_factor".format(property)
            factor_node.operation = 'MULTIPLY'
            factor_node.location = (x_location + 400, y_location)
            offset_node = shader_group.nodes.new('ShaderNodeMath')
            offset_node.label = "{}_offset".format(property)
            offset_node.name = "{}_offset".format(property)
            offset_node.location = (x_location + 800, y_location)
            displacement_node = shader_group.nodes.new(
                'ShaderNodeDisplacement')
            displacement_node.location = (x_location + 900, y_location)
            shader_group.outputs.new('NodeSocketVector', property)
            shader_group.links.new(
                texture_node.outputs[0], displacement_node.inputs[0])
            shader_group.links.new(
                displacement_node.outputs[0], group_out.inputs[texture_nodes.index(property)])
        else:
            factor_node = shader_group.nodes.new('ShaderNodeNormalMap')
            factor_node.label = "{}_factor".format(property)
            factor_node.name = "{}_factor".format(property)
            factor_node.location = (x_location + 400, y_location)
            shader_group.outputs.new('NodeSocketVector', property)
            shader_group.links.new(
                texture_node.outputs[0], factor_node.inputs[1])
            shader_group.links.new(
                factor_node.outputs[0], group_out.inputs[texture_nodes.index(property)])
    return shader_group


def build_shader(material, enable_displacement=False):
    texture_nodes = []
    aliases = []
    viz_dict = shader_template.u3m_pbr["visualization"]
    for param in viz_dict:
        texture_nodes.append(param)
        aliases.append(viz_dict[param]["alias"])
    shader_group = build_shader_group(texture_nodes)
    front_group_node = material.node_tree.nodes.new(
        'ShaderNodeGroup')
    front_group_node.label = "U3M_front"
    front_group_node.name = "U3M_front"
    front_group_node.location = (-180, 0)
    front_group_node.node_tree = shader_group
    back_group_node = material.node_tree.nodes.new(
        'ShaderNodeGroup')
    back_group_node.label = "U3M_back"
    back_group_node.name = "U3M_back"
    back_group_node.location = (-180.0, -800)
    back_group_node.node_tree = shader_group
    principled_front_node = material.node_tree.nodes.new(
        'ShaderNodeBsdfPrincipled')
    principled_front_node.label = "Principled BSDF_front"
    principled_front_node.name = "Principled BSDF_front"
    principled_front_node.distribution = 'MULTI_GGX'
    principled_front_node.location = (200, 0)
    principled_back_node = material.node_tree.nodes.new(
        'ShaderNodeBsdfPrincipled')
    principled_back_node.label = "Principled BSDF_back"
    principled_back_node.name = "Principled BSDF_back"
    principled_back_node.distribution = 'MULTI_GGX'
    principled_back_node.location = (200, -800)
    geometry_node = material.node_tree.nodes.new('ShaderNodeNewGeometry')
    geometry_node.location = (200, 200)
    shader_mix_node = material.node_tree.nodes.new(
        'ShaderNodeMixShader')
    shader_mix_node.label = "Mix_Front_Back"
    shader_mix_node.name = "Mix_Front_Back"
    shader_mix_node.location = (500, 0)
    material_out_node = material.node_tree.nodes.new(
        'ShaderNodeOutputMaterial')
    material_out_node.label = "Material Out"
    material_out_node.name = "Material Out"
    material_out_node.location = (700, 0)
    metadata_node = material.node_tree.nodes.new(
        'ShaderNodeScript')
    metadata_node.label = "Metadata"
    metadata_node.name = "Metadata"
    bpy.data.texts.new("U3M")
    metadata_node.script = bpy.data.texts["U3M"]
    metadata_node.location = (700, -100)
    links = material.node_tree.links
    for group, principled in [(front_group_node, principled_front_node), (back_group_node, principled_back_node)]:
        for socket in texture_nodes:
            if socket != "displacement":
                links.new(group.outputs[socket],
                          principled.inputs[aliases[texture_nodes.index(socket)]])
            else:
                if group == front_group_node and enable_displacement:
                    links.new(group.outputs[socket],
                              material_out_node.inputs[2])
    links.new(principled_front_node.outputs["BSDF"], shader_mix_node.inputs[1])
    links.new(principled_back_node.outputs["BSDF"], shader_mix_node.inputs[2])
    links.new(geometry_node.outputs["Backfacing"],
              shader_mix_node.inputs["Fac"])
    links.new(shader_mix_node.outputs[0], material_out_node.inputs[0])


def assign_material(material_name, use_linked_mat):
    blender_obj = Blender.get_active_obj()
    for m in Blender.get_materials():
        if m.name == material_name:
            m.name = material_name + " (Copy)"
    for t in Blender.get_texts():
        if t.name == "U3M_" + material_name:
            t.name = "U3M_" + material_name + " (Copy)"
    new_mat = bpy.data.materials.new(material_name)
    new_mat.use_nodes = True
    nodes = new_mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    build_shader(new_mat)
    if use_linked_mat is False:
        blender_obj.active_material = new_mat
    else:
        assigned_mat = blender_obj.active_material
        for o in Blender.get_objects():
            if o.active_material == assigned_mat:
                if o.active_material != None:  # has slots
                    # assign to 1st material slot of every object with the same material
                    o.active_material = new_mat
                else:
                    # no slots, assign to active object only.
                    blender_obj.active_material = new_mat
                    break


def fill_shader_nodes(u3m_version, u3m_dict, u3m_dir, error_handler):
    for side in shader_template.u3m_pbr["sides"]:
        is_side = Blender.DictQuery(u3m_dict).get("material/" + side)
        if is_side != None:
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
        else:
            obj = Blender.get_active_obj()
            Blender.remove_side_links(obj, side)


def apply_u3m(viz_dict, side, error_handler):
    blender_obj = Blender.get_active_obj()
    print("Apply to active material: ", blender_obj.active_material)
    active_material = blender_obj.active_material
    Blender.set_material_blend_method(active_material, "HASHED")
    Blender.set_material_shadow_method(active_material, "HASHED")
    active_material_tree = active_material.node_tree.nodes
    node = "U3M_" + side
    for param, param_dict in viz_dict.items():       # e.g. "alpha"
        props_dict = param_dict["properties"]
        for prop, prop_list in props_dict.items():
            val, subnode, node_input = prop_list[1], prop_list[2], prop_list[3]
            if val is None:
                if subnode:
                    try:
                        nt = active_material_tree[node]
                        active_material.node_tree.links.remove(
                            nt.outputs[subnode].links[0])
                    except IndexError:
                        # not part of the shader by default (e.g. Displacement)
                        pass
                else:
                    pass
            else:
                if prop == "texture":
                    Blender.apply_image(
                        val, active_material_tree[node].node_tree, subnode, param_dict, error_handler)
                else:
                    if subnode == "Principled BSDF" and param_dict["principled"] is False:
                        # nothing is currently done with such properties (e.g. Displacement)
                        pass
                    else:
                        # e.g. "bpy.data.materials['Houndstooth'].node_tree."
                        str_tree = "bpy.data.materials['%s'].node_tree." % active_material.name
                        if subnode == "Principled BSDF":
                            principled_node = subnode + "_" + side
                            str_mid = "nodes['%s']" % principled_node
                            if param == "subsurface_radius":
                                # constant is a single value in u3m, but a vector in Blender Principled
                                val = [val]*3
                            # e.g. ".inputs['Normal'].default_value = [1,1,1]"
                            str_end = ".%s = %s" % (node_input, val)
                        else:
                            # e.g. "nodes['U3M_front'].node_tree.nodes['normal']"
                            str_mid = "nodes['%s'].node_tree.nodes['%s']" % (
                                node, subnode)
                            # e.g. ".inputs[0].default_value = 0.5"
                            str_end = ".%s = %s" % (node_input, val)
                        # exec(str_tree + str_mid + str_end)
                        Blender.execute(str_tree + str_mid + str_end)
    blender_obj.select_set(True)


def collect_and_copy_u3m_data(side, new_material_folder, new_material_name):
    material = Blender.get_active_material()
    active_material_tree = material.node_tree.nodes
    u3m_pbr = copy.deepcopy(shader_template.u3m_pbr)
    group_node = "U3M_" + side
    side_dict = u3m_pbr["sides"][side]
    side_dict["visualization"] = copy.deepcopy(u3m_pbr["visualization"])
    viz_dict = side_dict["visualization"]
    for param, param_dict in viz_dict.items():
        props_dict = param_dict["properties"]
        for prop, prop_list in props_dict.items():
            subnode, node_input = prop_list[2], prop_list[3]
            if prop == "texture":   # if texture
                img = active_material_tree[group_node].node_tree.nodes[subnode].image
                if img:
                    texture_path, tex_ext = img.filepath, img.file_format
                    tex_suffix = param_dict["suffix"]
                    new_texture_name = new_material_name + "_" + tex_suffix + "." + tex_ext
                    # write texture name to u3m_dict
                    prop_list[1] = "textures/" + new_texture_name
                    # copy texture file to output path
                    texture_path_dst = os.path.join(
                        new_material_folder, "textures", new_texture_name)
                    texture_path_dst_dirname = os.path.dirname(
                        texture_path_dst)
                    if not os.path.exists(texture_path_dst_dirname):
                        os.makedirs(texture_path_dst_dirname)
                    if not texture_path == texture_path_dst:
                        copyfile(texture_path, texture_path_dst)
                    # update texture name and path in shader nodes
                    img.name, img.filepath = new_texture_name, texture_path_dst
            else:
                # use exec to access shader node values using dict strings
                str_pre = "prop_list[1] = "
                str_tree = "bpy.data.materials['%s'].node_tree." % material.name
                str_end = None
                if subnode == "Principled BSDF":
                    principled_node = subnode + "_" + side
                    if param_dict["principled"] is False:      # e.g. False for Displacement
                        pass
                    else:
                        # e.g. "nodes['normal_factor'].default_value"
                        str_end = "nodes['%s'].%s" % (
                            principled_node, node_input)
                else:
                    str_end = "nodes['%s'].node_tree.nodes['%s'].%s" % (
                        group_node, subnode, node_input)
                if str_end:
                    exec(str_pre + str_tree + str_end)
                    # store mean value of Blender vector as U3M constant value
                    if prop == "constant" and param == "subsurface_radius":
                        prop_list[1] = sum(list(prop_list[1])) / 3
                # translate to u3m schema (MULTIPLY > multiply)
                if prop == "mode":
                    val = prop_list[1]
                    for mode_u3m, mode_blender in blend_modes.items():
                        if mode_blender == "'%s'" % val:
                            prop_list[1] = str(mode_u3m)
                            break
    return viz_dict


def has_side(side):
    active_material = Blender.get_active_material()
    principled_node = "Principled BSDF_" + side
    return active_material.node_tree.nodes[principled_node].outputs["BSDF"].links != ()

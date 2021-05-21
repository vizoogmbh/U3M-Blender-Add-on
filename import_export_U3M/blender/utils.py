import os
from pathlib import Path
import bpy
import math
import sys
import subprocess


class DictQuery(dict):
    def get(self, path, default=None):
        keys = path.split("/")
        val = None
        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)
            if not val:
                break
        return val


def get(str_val):
    val = None
    pre_str = "val = "
    execute(pre_str+str_val)
    return val


def append_item(item="Material", name="U3M"):
    dir_path = Path(__file__).parents[0]  # get path of this file
    if item == "Material":
        scene_mats = bpy.data.materials
        if name in scene_mats:
            return False
    if item == "Collection":
        scene_collections = bpy.data.collections
        if name in scene_collections:
            return False
    if item == "WorkSpace":
        scene_workspaces = bpy.data.workspaces
        if name in scene_workspaces:
            return False
    bpy.ops.wm.append(directory=str(
        dir_path / "source/U3M.blend" / item), filename=name)


def append_u3m_shader():
    scene_mats = bpy.data.materials
    if "U3M" in scene_mats:
        return False
    else:
        dir_path = Path(__file__).parents[0]  # get path of this file
        bpy.ops.wm.append(directory=str(
            dir_path / "source/U3M.blend/Material/"), filename="U3M")
        return True


def get_active_obj():
    return bpy.context.object


def u3m_mats_in_scene():
    try:
        mats = []
        for m in bpy.data.materials:
            if "U3M_front" in m.node_tree.nodes:
                mats.append((m.name, m.name, ""))
        return mats
    except:
        return [("1", "1", "")]


def is_u3m(material):
    for node in material.node_tree.nodes:
        if "U3M_" in node.name:
            return True
    return False


def context_is_u3m(context):
    obj = context.object
    if obj:
        if obj.active_material:
            if "U3M_front" in obj.active_material.node_tree.nodes:
                return True
    return False


def get_u3m_version():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.u3m_version


def get_texture_width():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.texture_width


def get_texture_height():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.texture_height


def get_u3m_dir():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.u3m_dir


def get_u3m_data():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.u3m_data


def get_preview():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.preview


def get_icon():
    blender_obj = get_active_obj()
    metadata = blender_obj.active_material.node_tree.nodes["Metadata"].script.as_module(
    )
    return metadata.icon


def set_area():
    area = next(
        area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    area.spaces[0].region_3d.view_perspective = 'CAMERA'


def render():
    bpy.ops.render.render(write_still=True)


def set_u3m_scale(error_handler):
    version = get_u3m_version()

    if version == "1.1":  # 1.1 texture size is given in mm
        width = float(get_texture_width())
        height = float(get_texture_height())
    elif version == "1.0":  # 1.0 in cm
        width = float(get_texture_width())*10
        height = float(get_texture_height())*10

    bpy.context.scene.u3m_width = width
    bpy.context.scene.u3m_height = height
    uv_dim_x, uv_dim_y = calculate_uv_dimensions(
        bpy.context.object, error_handler)
    if uv_dim_x is not None and uv_dim_y is not None:
        bpy.context.scene.u3m_scale_x = uv_dim_x/(width/1000)
        bpy.context.scene.u3m_scale_y = uv_dim_y/(height/1000)
    else:
        print("Error: couldn't calculate uv dimension, setting shader scale to default...")
        bpy.context.scene.u3m_scale_x = 1
        bpy.context.scene.u3m_scale_y = 1


def calculate_uv_dimensions(obj, error_handler):
    if not obj:
        uv_dim_x = None
        uv_dim_y = None
        error_handler.handle('no_active_object')
    elif obj.type != 'MESH':
        uv_dim_x = None
        uv_dim_y = None
        error_handler.handle('no_mesh')
    else:
        polys = []
        for p in obj.data.polygons:
            if p.material_index == 0:
                polys.append(p)
        no_of_polys = len(polys)

        from random import randint
        random_poly_numbers = []
        for i in range(32):  # check 32 random polys
            random_poly_numbers.append(randint(0, no_of_polys-1))
        uv_dims_x = []
        uv_dims_y = []

        for p in random_poly_numbers:
            poly = polys[p]
            for loop_index in range(poly.loop_start, (poly.loop_start + poly.loop_total)-1):
                vert_index = obj.data.loops[loop_index].vertex_index
                vert_index_n = obj.data.loops[loop_index+1].vertex_index
                vert_co = obj.data.vertices[vert_index].co
                vert_next_co = obj.data.vertices[vert_index_n].co
                v_distance_x = (vert_next_co[0] - vert_co[0]) * obj.scale.x
                v_distance_y = (vert_next_co[1] - vert_co[1]) * obj.scale.y
                v_distance_z = (vert_next_co[2] - vert_co[2]) * obj.scale.z
                v_distance = math.sqrt(math.pow(
                    v_distance_x, 2) + math.pow(v_distance_y, 2) + math.pow(v_distance_z, 2))
                uv = obj.data.uv_layers.active
                uv_co = uv.data[loop_index].uv
                uv_next_co = uv.data[loop_index+1].uv
                uv_distance = math.sqrt(
                    math.pow(uv_next_co[0] - uv_co[0], 2) + math.pow(uv_next_co[1] - uv_co[1], 2))
                uv_scale = v_distance / uv_distance
                if loop_index == poly.loop_start:
                    uv_dims_x.append(uv_scale)
                elif loop_index == poly.loop_start+1:
                    uv_dims_y.append(uv_scale)

        uv_dim_x = sum(uv_dims_x) / len(uv_dims_x)
        uv_dim_y = sum(uv_dims_y) / len(uv_dims_y)

    return uv_dim_x, uv_dim_y


def get_u3m_scale_x():
    return bpy.context.scene.u3m_scale_x


def get_u3m_scale_y():
    return bpy.context.scene.u3m_scale_y


def get_u3m_size():
    return bpy.context.scene.u3m_size


def set_active(obj):
    bpy.context.view_layer.objects.active = obj


def get_all_objects(view_name):
    return bpy.data.collections[view_name].objects


def set_camera(scene, view_name):  # set camera / uses first camera found in the collection
    for o in bpy.data.collections[view_name].objects:
        if o.type == "CAMERA":
            scene.camera = o


def set_collection_visible(scene, view_name):
    views_collection = scene.collection.children[0]
    for cc in views_collection.children:
        if cc.name == view_name:
            cc.hide_viewport, cc.hide_render = False, False
        else:
            cc.hide_viewport, cc.hide_render = True, True


def get_scene():
    return bpy.context.scene


def open_u3m_scene():
    bpy.context.window.scene = bpy.data.scenes["U3M"]


def open_u3m_workspace():
    bpy.data.window_managers['WinMan'].windows[0].workspace = bpy.data.workspaces['U3M']


def get_workspaces():
    return bpy.data.workspaces


def remove_scene(scene):
    bpy.data.scenes.remove(scene)


def get_current_object():
    return bpy.context.object


def new_temp_scene():
    return bpy.data.scenes.new("TEMP")


def remove_texture(node_group, node_name):
    bpy.data.node_groups[node_group].nodes[node_name].image = None


def get_active_material():
    return bpy.context.object.active_material


def set_material_name(material_name):
    bpy.context.object.active_material.name = material_name


def get_material(material):
    return bpy.data.materials[material]


def get_materials():
    return bpy.data.materials


def get_texts():
    return bpy.data.texts


def get_objects():
    return bpy.data.objects


def get_node_groups():
    return bpy.data.node_groups


def get_text(text):
    return bpy.data.texts[text]


def get_images():
    return bpy.data.images


def load_image(filepath, error_handler):
    if not os.path.exists(filepath):
        error_handler.handle('no_texture')
        return None
    else:
        return bpy.data.images.load(filepath)


def execute(str):
    exec(str)


def apply_image(img_path, node_tree, subnode, param_dict, error_handler):
    sn = node_tree.nodes[subnode]
    img = None
    for used_img in get_images():
        if used_img.filepath == img_path:  # if image already exists
            img = used_img
    if img is None:
        img = load_image(img_path, error_handler)
    if img is not None:
        sn.image = img
        if subnode != "basecolor" and subnode != "subsurface_color":
            sn.image.colorspace_settings.name = 'Non-Color'


def remove_side_links(obj, side):
    active_material = obj.active_material
    tree = active_material.node_tree
    tree.links.remove(
        tree.nodes["Principled BSDF_"+side].outputs["BSDF"].links[0])
    try:        # when the function is called from editor, there is no backfacing link
        tree.links.remove(
            tree.nodes["Geometry"].outputs["Backfacing"].links[0])
    except:
        pass
    if side == "back":
        tree.nodes["Mix_Front_Back"].inputs['Fac'].default_value = 0
    if side == "front":
        tree.nodes["Mix_Front_Back"].inputs['Fac'].default_value = 1
    # remove all inputs of Principled BSDF
    for i in tree.nodes["Principled BSDF_"+side].inputs:
        try:  # there can be inputs w/o link
            tree.links.remove(
                tree.nodes["Principled BSDF_"+side].inputs[i.name].links[0])
        except:
            pass


def display_error_confirmation(error_message):
    bpy.context.scene.error_message = error_message
    bpy.ops.wm.error_confirm('INVOKE_DEFAULT')

import os
import math
from pathlib import Path

import bpy


class DictQuery(dict):
    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val is None:
                val = dict.get(self, key, default)
            elif isinstance(val, list):
                val = [
                    item.get(key, default) if isinstance(item, dict) else default
                    for item in val
                ]
            elif isinstance(val, dict):
                val = val.get(key, default)
            else:
                return default

            if val is None:
                break

        return val


def append_item(item="WorkSpace", name="U3M"):
    dir_path = Path(__file__).parent

    if item == "Collection":
        if name in bpy.data.collections:
            return False
    elif item == "WorkSpace":
        if name in bpy.data.workspaces:
            return False

    bpy.ops.wm.append(
        directory=str(dir_path / "source" / "preview_scene.blend" / item),
        filename=name,
    )
    return True


def get_active_obj():
    return bpy.context.object


def u3m_mats_in_scene():
    try:
        mats = []
        for material in bpy.data.materials:
            node_tree = getattr(material, "node_tree", None)
            if node_tree and "U3M_front" in node_tree.nodes:
                mats.append((material.name, material.name, ""))
        return mats
    except Exception:
        return [("1", "1", "")]


def is_u3m(material):
    if material is None or material.node_tree is None:
        return False

    for node in material.node_tree.nodes:
        if "U3M_" in node.name:
            return True
    return False


def context_is_u3m(context):
    obj = context.object
    if obj is None or obj.active_material is None:
        return False

    node_tree = obj.active_material.node_tree
    if node_tree is None:
        return False

    return "U3M_front" in node_tree.nodes


def _get_metadata_module():
    obj = get_active_obj()
    if obj is None or obj.active_material is None:
        return None

    node_tree = obj.active_material.node_tree
    if node_tree is None:
        return None

    metadata_node = node_tree.nodes.get("Metadata")
    if metadata_node is None or metadata_node.script is None:
        return None

    try:
        return metadata_node.script.as_module()
    except Exception:
        return None


def get_u3m_version():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.u3m_version


def get_texture_width():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.texture_width


def get_texture_height():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.texture_height


def get_u3m_dir():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.u3m_dir


def get_u3m_data():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.u3m_data


def get_preview():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.preview


def get_icon():
    metadata = _get_metadata_module()
    return None if metadata is None else metadata.icon


def set_area():
    area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
    area.spaces[0].region_3d.view_perspective = "CAMERA"


def render():
    bpy.ops.render.render(write_still=True)


def set_u3m_scale(error_handler):
    version = get_u3m_version()
    texture_width = get_texture_width()
    texture_height = get_texture_height()

    if version is None or texture_width is None or texture_height is None:
        error_handler.handle("loading_failed")
        bpy.context.scene.u3m_width = 1.0
        bpy.context.scene.u3m_height = 1.0
        bpy.context.scene.u3m_scale_x = 1.0
        bpy.context.scene.u3m_scale_y = 1.0
        return

    if version == "1.1":  # 1.1 texture size is given in mm
        width = float(texture_width)
        height = float(texture_height)
    elif version == "1.0":  # 1.0 in cm
        width = float(texture_width) * 10.0
        height = float(texture_height) * 10.0
    else:
        error_handler.handle("wrong_version")
        bpy.context.scene.u3m_width = 1.0
        bpy.context.scene.u3m_height = 1.0
        bpy.context.scene.u3m_scale_x = 1.0
        bpy.context.scene.u3m_scale_y = 1.0
        return

    bpy.context.scene.u3m_width = width
    bpy.context.scene.u3m_height = height

    uv_dim_x, uv_dim_y = calculate_uv_dimensions(bpy.context.object, error_handler)
    if uv_dim_x is not None and uv_dim_y is not None:
        bpy.context.scene.u3m_scale_x = uv_dim_x / (width / 1000.0)
        bpy.context.scene.u3m_scale_y = uv_dim_y / (height / 1000.0)
    else:
        print(
            "Error: couldn't calculate uv dimension, setting shader scale to default..."
        )
        bpy.context.scene.u3m_scale_x = 1.0
        bpy.context.scene.u3m_scale_y = 1.0


def calculate_uv_dimensions(obj, error_handler):
    if obj is None:
        error_handler.handle("no_active_object")
        return None, None

    if obj.type != "MESH":
        error_handler.handle("no_mesh")
        return None, None

    uv_layer = obj.data.uv_layers.active
    if uv_layer is None:
        error_handler.handle("no_uv_map")
        return None, None

    polys = [poly for poly in obj.data.polygons if poly.material_index == 0]
    no_of_polys = len(polys)

    if no_of_polys == 0:
        error_handler.handle("no_polygons")
        return None, None

    from random import randint

    random_poly_numbers = [
        randint(0, no_of_polys - 1) for _ in range(min(32, no_of_polys))
    ]
    uv_dims_x = []
    uv_dims_y = []

    for poly_index in random_poly_numbers:
        poly = polys[poly_index]

        for loop_index in range(
            poly.loop_start, (poly.loop_start + poly.loop_total) - 1
        ):
            vert_index = obj.data.loops[loop_index].vertex_index
            vert_index_next = obj.data.loops[loop_index + 1].vertex_index

            vert_co = obj.data.vertices[vert_index].co
            vert_next_co = obj.data.vertices[vert_index_next].co

            v_distance_x = (vert_next_co[0] - vert_co[0]) * obj.scale.x
            v_distance_y = (vert_next_co[1] - vert_co[1]) * obj.scale.y
            v_distance_z = (vert_next_co[2] - vert_co[2]) * obj.scale.z

            v_distance = math.sqrt(
                (v_distance_x**2) + (v_distance_y**2) + (v_distance_z**2)
            )

            uv_co = uv_layer.data[loop_index].uv
            uv_next_co = uv_layer.data[loop_index + 1].uv

            uv_distance = math.sqrt(
                ((uv_next_co[0] - uv_co[0]) ** 2) + ((uv_next_co[1] - uv_co[1]) ** 2)
            )

            if uv_distance == 0:
                continue

            uv_scale = v_distance / uv_distance

            if loop_index == poly.loop_start:
                uv_dims_x.append(uv_scale)
            elif loop_index == poly.loop_start + 1:
                uv_dims_y.append(uv_scale)

    if not uv_dims_x or not uv_dims_y:
        error_handler.handle("uv_calc_failed")
        return None, None

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


def set_camera(scene, view_name):
    for obj in bpy.data.collections[view_name].objects:
        if obj.type == "CAMERA":
            scene.camera = obj
            break


def set_collection_visible(scene, view_name):
    views_collection = scene.collection.children[0]
    for child_collection in views_collection.children:
        if child_collection.name == view_name:
            child_collection.hide_viewport = False
            child_collection.hide_render = False
        else:
            child_collection.hide_viewport = True
            child_collection.hide_render = True


def get_scene():
    return bpy.context.scene


def open_u3m_scene():
    bpy.context.window.scene = bpy.data.scenes["U3M"]


def open_u3m_workspace():
    bpy.data.window_managers["WinMan"].windows[0].workspace = bpy.data.workspaces["U3M"]


def get_workspaces():
    return bpy.data.workspaces


def remove_scene(scene):
    bpy.data.scenes.remove(scene)


def get_current_object():
    return bpy.context.object


def remove_texture(node_group, node_name):
    bpy.data.node_groups[node_group].nodes[node_name].image = None


def get_active_material():
    obj = bpy.context.object
    return None if obj is None else obj.active_material


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


def get_selected_objects():
    return bpy.context.selected_objects


def get_node_groups():
    return bpy.data.node_groups


def get_text(text):
    return bpy.data.texts[text]


def get_images():
    return bpy.data.images


def load_image(filepath, error_handler):
    if not os.path.exists(filepath):
        error_handler.handle("no_texture")
        return None
    return bpy.data.images.load(filepath)


def set_material_blend_method(material, blend_method):
    material.blend_method = blend_method


def set_material_shadow_method(material, shadow_method) -> bool:
    if hasattr(material, "shadow_method"):
        material.shadow_method = shadow_method
        return True
    return False


def apply_image(img_path, node_tree, subnode, error_handler):
    node = node_tree.nodes[subnode]
    img = None

    for used_img in get_images():
        if used_img.filepath == img_path:
            img = used_img
            break

    if img is None:
        img = load_image(img_path, error_handler)

    if img is not None:
        node.image = img
        if subnode not in {"basecolor", "subsurface_color"}:
            node.image.colorspace_settings.name = "Non-Color"


def remove_side_links(obj, side):
    active_material = obj.active_material
    tree = active_material.node_tree

    tree.links.remove(tree.nodes[f"Principled_BSDF_{side}"].outputs["BSDF"].links[0])

    try:
        tree.links.remove(tree.nodes["Geometry"].outputs["Backfacing"].links[0])
    except Exception:
        pass

    if side == "back":
        tree.nodes["Mix_Front_Back"].inputs["Fac"].default_value = 0
    if side == "front":
        tree.nodes["Mix_Front_Back"].inputs["Fac"].default_value = 1

    for input_socket in tree.nodes[f"Principled_BSDF_{side}"].inputs:
        try:
            tree.links.remove(
                tree.nodes[f"Principled_BSDF_{side}"].inputs[input_socket.name].links[0]
            )
        except Exception:
            pass


def display_error_confirmation(error_message):
    bpy.context.scene.error_message = error_message
    bpy.ops.wm.error_confirm("INVOKE_DEFAULT")

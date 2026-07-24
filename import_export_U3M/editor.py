from .blender import utils
from .blender.node_builder import ShaderNodeBuilder
from .blender import shader_template


def _get_active_u3m_tree(context):
    obj = context.object
    if obj is None or obj.active_material is None:
        return None

    node_tree = obj.active_material.node_tree
    if node_tree is None:
        return None

    return node_tree


def _get_mix_front_back_node(context):
    tree = _get_active_u3m_tree(context)
    if tree is None:
        return None
    return tree.nodes.get("Mix_Front_Back")


class U3MEditPanelFrontBase(object):
    @classmethod
    def poll(cls, context):
        return utils.context_is_u3m(context)

    def draw(self, context):
        render_edit_subpanel(self, context, "front", 0)


class U3MEditPanelFrontAdvancedBase(object):
    @classmethod
    def poll(cls, context):
        mix_node = _get_mix_front_back_node(context)
        if mix_node is None:
            return False
        return len(mix_node.inputs[1].links) > 0

    def draw(self, context):
        render_edit_subpanel(self, context, "front", 1)


class U3MEditPanelBackBase(object):
    @classmethod
    def poll(cls, context):
        return utils.context_is_u3m(context)

    def draw(self, context):
        render_edit_subpanel(self, context, "back", 0)


class U3MEditPanelBackAdvancedBase(object):
    @classmethod
    def poll(cls, context):
        mix_node = _get_mix_front_back_node(context)
        if mix_node is None:
            return False
        return len(mix_node.inputs[2].links) > 0

    def draw(self, context):
        render_edit_subpanel(self, context, "back", 1)


class AddSideOperatorBase(object):
    id = None

    def execute(self, context):
        add_side(context, self.id)
        return {"FINISHED"}


class RemoveSideOperatorBase(object):
    id = None

    def execute(self, context):
        remove_side(context, self.id)
        return {"FINISHED"}


class ToggleAlphaOperatorBase(object):
    id = None

    def execute(self, context):
        context.scene.u3m_alpha_enabled = not context.scene.u3m_alpha_enabled
        toggle_alpha(context)
        return {"FINISHED"}


def render_edit_subpanel(self, context, side, level):
    layout = self.layout
    obj = context.object
    if obj is None:
        return

    mat = obj.active_material
    if mat is None or mat.node_tree is None:
        return

    tree = mat.node_tree
    mix_node = tree.nodes.get("Mix_Front_Back")
    u3m_group_node = tree.nodes.get("U3M_" + side)

    if mix_node is None or u3m_group_node is None or u3m_group_node.node_tree is None:
        return

    row = layout.row()
    side_id = shader_template.u3m_pbr["sides"][side]["id"]

    if len(mix_node.inputs[side_id].links) < 1:
        row.label(text=f"This material has no {side} side")
        row.operator("myops.u3m_add_side", text="Add").id = side_id
        return

    if level == 0:
        row.operator("myops.u3m_remove_side", text="Remove side", icon="CANCEL").id = (
            side_id
        )

    viz_dict = shader_template.u3m_pbr["visualization"]
    u3m_tree = u3m_group_node.node_tree

    for param in viz_dict:
        editor_level = viz_dict[param]["editor_level"]
        props = viz_dict[param]["properties"]

        if editor_level != level:
            continue

        if editor_level != 0:
            if param == "subsurface_color":
                continue

            if param in ["sheen_tint", "specular_tint", "clearcoat_normal"]:
                node = u3m_tree.nodes[f"{param}_factor"].inputs[0]
            else:
                node = u3m_tree.nodes["U3M_out"].inputs[param]

            row = layout.row(align=True)
            row.label(text=param)
            row.prop(node, "default_value", text="")
            continue

        param_node = u3m_tree.nodes[param]
        pnode = f"{param_node.id_data.name_full}_&_{side}_&_{param_node.name}"
        alias_name = viz_dict[param]["alias"]

        if param_node.image:
            row = layout.row(align=True)
            row.operator("myops.u3m_remove_texture", text="", icon="X").pnode = pnode
            row.label(text=alias_name, icon="TEXTURE", text_ctxt=param_node.image.name)

            if param == "alpha":
                alpha_enabled = context.scene.u3m_alpha_enabled
                icon = "CHECKBOX_HLT" if alpha_enabled else "CHECKBOX_DEHLT"
                text = "ON" if alpha_enabled else "OFF"
                row.operator("myops.u3m_toggle_alpha", text=text, icon=icon)

            for prop_name in props:
                if prop_name == "factor":
                    node = u3m_tree.nodes[f"{param}_factor"]
                    if param in ["normal", "displacement"]:
                        socket = node.inputs[0]
                    else:
                        socket = node.inputs[1]
                    row.prop(socket, "default_value", text="Factor")

                if (
                    prop_name == "constant"
                    and viz_dict[param]["type"] != "texture_and_vector"
                ):
                    node = u3m_tree.nodes[f"{param}_factor"]
                    row.prop(node, "operation", text="")

                if prop_name == "offset":
                    node = u3m_tree.nodes[f"{param}_offset"]
                    row.prop(node.inputs[1], "default_value", text="Offset")

                if prop_name == "mode":
                    node = u3m_tree.nodes[f"{param}_factor"]
                    row.prop(node, "blend_type", text="")
                    row.prop(node.inputs[1], "default_value", text="")

            continue

        row = layout.row(align=True)
        row.operator("myops.u3m_load_texture", text="", icon="FILE_FOLDER").pnode = (
            pnode
        )
        row.label(text=alias_name, icon="FILE_BLANK")

        pnode_name = "U3M_out"
        output_node = u3m_tree.nodes[pnode_name]
        input_type = output_node.inputs[param].type

        if input_type != "VECTOR":
            row.prop(output_node.inputs[param], "default_value", text="")


def add_texture(context, node_group, side, node_name, img_path):
    if not img_path:
        return

    tree = _get_active_u3m_tree(context)
    if tree is None:
        return

    group_node = tree.nodes.get("U3M_" + side)
    if group_node is None or group_node.node_tree is None:
        return

    u3m_node_tree = group_node.node_tree
    utils.apply_image(img_path, u3m_node_tree, node_name, None)

    if node_name in ["basecolor", "normal"]:
        input_node = u3m_node_tree.nodes[node_name + "_factor"].outputs[0]
    elif node_name in ["metalness", "roughness", "alpha"]:
        input_node = u3m_node_tree.nodes[node_name + "_offset"].outputs[0]
    elif node_name == "displacement":
        input_node = u3m_node_tree.nodes[node_name + "_height"].outputs[0]
    else:
        return

    u3m_node_tree.links.new(
        input=input_node,
        output=u3m_node_tree.nodes["U3M_out"].inputs[node_name],
    )


def remove_texture(context, node_group, side, node_name):
    tree = _get_active_u3m_tree(context)
    if tree is None:
        return

    group_node = tree.nodes.get("U3M_" + side)
    if group_node is None or group_node.node_tree is None:
        return

    u3m_node_tree = group_node.node_tree
    utils.remove_texture(node_group, node_name)

    links = u3m_node_tree.nodes["U3M_out"].inputs[node_name].links
    if links:
        u3m_node_tree.links.remove(links[0])


def add_side(context, side_id):
    obj = context.object
    if (
        obj is None
        or obj.active_material is None
        or obj.active_material.node_tree is None
    ):
        return

    mat = obj.active_material
    tree = mat.node_tree
    sides = shader_template.u3m_pbr["sides"]

    for side in sides:
        if sides[side]["id"] == side_id:
            mix_node = tree.nodes.get("Mix_Front_Back")
            geometry_node = tree.nodes.get("Geometry")
            if mix_node is None or geometry_node is None:
                return

            inputs = mix_node.inputs

            if len(inputs[1].links) > 0 or len(inputs[2].links) > 0:
                tree.links.new(
                    input=mix_node.inputs["Fac"],
                    output=geometry_node.outputs["Backfacing"],
                )
            else:
                mix_node.inputs["Fac"].default_value = int(side_id) - 1

            viz_dict = shader_template.u3m_pbr["visualization"]
            builder = ShaderNodeBuilder(viz_dict, side)
            builder.build_shader_nodes(mat)

            tree.links.new(
                input=tree.nodes["Mix_Front_Back"].inputs[side_id],
                output=tree.nodes["Principled_BSDF_" + side].outputs["BSDF"],
            )


def remove_side(context, side_id):
    obj = context.object
    if (
        obj is None
        or obj.active_material is None
        or obj.active_material.node_tree is None
    ):
        return

    mat = obj.active_material
    tree = mat.node_tree
    sides = shader_template.u3m_pbr["sides"]

    for side in sides:
        if sides[side]["id"] == side_id:
            utils.remove_side_links(obj, side)

            group_node = tree.nodes.get("U3M_" + side)
            if group_node is None or group_node.node_tree is None:
                return

            for node in group_node.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    node.image = None


def toggle_alpha(context):
    obj = context.object
    if (
        obj is None
        or obj.active_material is None
        or obj.active_material.node_tree is None
    ):
        return

    mat = obj.active_material
    tree = mat.node_tree
    sides = shader_template.u3m_pbr["sides"]

    for side in sides:
        u3m_node = tree.nodes.get("U3M_" + side)
        principled_node = tree.nodes.get("Principled_BSDF_" + side)

        if not u3m_node or not principled_node:
            continue

        alpha_input = principled_node.inputs.get("Alpha")
        if not alpha_input:
            continue

        u3m_output_alpha = u3m_node.outputs.get("alpha")
        links_to_alpha = [
            link
            for link in tree.links
            if link.to_node == principled_node and link.to_socket == alpha_input
        ]

        if links_to_alpha:
            for link in links_to_alpha:
                tree.links.remove(link)
        elif u3m_output_alpha:
            tree.links.new(u3m_output_alpha, alpha_input)

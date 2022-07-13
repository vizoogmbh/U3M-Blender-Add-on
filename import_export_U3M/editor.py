from import_export_U3M.blender import utils
from import_export_U3M.blender import shader_template


class U3MEditPanelFrontBase(object):

    @classmethod
    def poll(cls, context):
        return utils.context_is_u3m(context)

    def draw(self, context):
        render_edit_subpanel(self, context, "front", 0)


class U3MEditPanelFrontAdvancedBase(object):

    @classmethod
    def poll(cls, context):
        # has front side
        return len(context.object.active_material.node_tree.nodes["Mix_Front_Back"].inputs[1].links) > 0

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
        # has back side
        return len(context.object.active_material.node_tree.nodes["Mix_Front_Back"].inputs[2].links) > 0

    def draw(self, context):
        render_edit_subpanel(self, context, "back", 1)


class AddSideOperatorBase(object):

    id = None

    def execute(self, context):
        add_side(context, self.id)
        return {'FINISHED'}


class RemoveSideOperatorBase(object):

    id = None

    def execute(self, context):
        remove_side(context, self.id)
        return {'FINISHED'}


def render_edit_subpanel(self, context, side, level):
    layout = self.layout
    obj = context.object
    mat = obj.active_material
    if mat:
        tree = mat.node_tree
        mix_front_back = tree.nodes["Mix_Front_Back"]
        side_id = shader_template.u3m_pbr["sides"][side]["id"]
        row = layout.row()
        if len(mix_front_back.inputs[side_id].links) < 1:          # side is null
            row.label(text="This material has no %s side" % side)
            row.operator("myops.u3m_add_side", text="Add").id = side_id
        else:
            if level == 0:
                # operator to remove the side
                row.operator("myops.u3m_remove_side",
                             text="Remove side", icon="CANCEL").id = side_id
            viz_dict = shader_template.u3m_pbr["visualization"]
            for param in viz_dict:
                editor_level = viz_dict[param]["editor_level"]
                props = viz_dict[param]["properties"]
                #props_len = len(props)
                if editor_level != level:
                    pass
                else:
                    alias_name = viz_dict[param]["alias"]
                    # check if there is a texture image
                    u3m_tree = tree.nodes["U3M_" + side].node_tree
                    param_node = u3m_tree.nodes[param]
                    pnode = param_node.id_data.name_full + "_&_" + side + "_&_" + \
                        param_node.name          # e.g. "U3M_front_Material1_&_front_&_displacement"
                    if param_node.image:  # if yes, take the U3M nodes
                        #row = layout.column_flow(columns=min([props_len-2, 4]), align=True)
                        row = layout.row(align=True)
                        # operator to remove a texture
                        row.operator("myops.u3m_remove_texture",
                                     text="", icon="X").pnode = pnode
                        row.label(text=alias_name, icon="TEXTURE",
                                  text_ctxt=param_node.image.name)
                        props = viz_dict[param]["properties"]
                        for p in props:
                            if p == "factor":
                                node = u3m_tree.nodes[param + "_factor"]
                                row.prop(
                                    node.inputs[0], "default_value", text="Factor")
                            # normals have no operation property
                            if p == "constant" and viz_dict[param]["type"] != "texture_and_vector":
                                node = u3m_tree.nodes[param + "_factor"]
                                row.prop(node, "operation", text="")
                            if p == "offset":
                                node = u3m_tree.nodes[param + "_offset"]
                                row.prop(
                                    node.inputs[0], "default_value", text="Offset")
                            if p == "mode":
                                node = u3m_tree.nodes[param + "_factor"]
                                row.prop(node, "blend_type", text="")
                                row.prop(node.inputs[1],
                                         "default_value", text="")
                    else:     # if not, take the principled parameters
                        row = layout.row(align=True)
                        # operator to add a texture
                        row.operator("myops.u3m_load_texture",
                                     text="", icon="FILE_FOLDER").pnode = pnode
                        row.label(text=alias_name, icon="FILE_BLANK")
                        # if parameter is in principled shader
                        # e.g. Displacement is not
                        principled = viz_dict[param]["principled"]
                        if principled is True:
                            pnode_name = "Principled BSDF_" + side
                            pnode = tree.nodes[pnode_name]
                            # VECTOR / RGBA / VALUE
                            input_type = pnode.inputs[alias_name].type
                            if input_type == "VECTOR":
                                # e.g. Normal, cannot be tweaked w/o texture
                                pass
                            else:
                                row.prop(
                                    tree.nodes[pnode_name].inputs[alias_name], "default_value", text="")


def add_texture(context, node_group, side, node_name, img_path):
    node_tree = context.object.active_material.node_tree
    param_dict = shader_template.u3m_pbr["visualization"][node_name]
    u3m_node_tree = node_tree.nodes["U3M_"+side].node_tree
    utils.apply_image(img_path, u3m_node_tree, node_name, param_dict, None)
    principled = param_dict["principled"]
    if principled is True:
        principled_name = param_dict["alias"]
        node_tree.links.new(input=node_tree.nodes["U3M_"+side].outputs[node_name],
                            output=node_tree.nodes["Principled BSDF_"+side].inputs[principled_name])


def remove_texture(context, node_group, side, node_name):
    tree = context.object.active_material.node_tree
    param = shader_template.u3m_pbr["visualization"][node_name]
    utils.remove_texture(node_group, node_name)
    principled = param["principled"]
    if principled is True:
        tree.links.remove(tree.nodes["U3M_"+side].outputs[node_name].links[0])


def add_side(context, side_id):
    obj = context.object
    mat = obj.active_material
    tree = mat.node_tree
    sides = shader_template.u3m_pbr["sides"]
    for side in sides:
        if sides[side]["id"] == side_id:
            print("Adding side:", side)
            inputs = tree.nodes["Mix_Front_Back"].inputs
            # if node is completely disconnected from shaders (both sides removed)
            if inputs[1].links != () or inputs[2].links != ():
                tree.links.new(input=tree.nodes["Mix_Front_Back"].inputs["Fac"],
                               output=tree.nodes["Geometry"].outputs["Backfacing"])
            else:
                tree.nodes["Mix_Front_Back"].inputs["Fac"].default_value = int(
                    side_id) - 1       # 0 for front side, 1 for back side
            tree.links.new(input=tree.nodes["Mix_Front_Back"].inputs[side_id],
                           output=tree.nodes["Principled BSDF_"+side].outputs["BSDF"])


def remove_side(context, side_id):
    obj = context.object
    mat = obj.active_material
    tree = mat.node_tree
    sides = shader_template.u3m_pbr["sides"]
    for side in sides:
        if sides[side]["id"] == side_id:
            print("Removing side:", side)
            # delete links to Principled
            utils.remove_side_links(obj, side)
            for node in tree.nodes["U3M_"+side].node_tree.nodes:        # delete textures
                #C.object.active_material.node_tree.nodes["U3M_front"].node_tree.nodes["normal"].image = None
                if node.type == "TEX_IMAGE" and node.image:
                    node.image = None

import bpy


class ShaderNodeBuilder:
    def __init__(self, viz_dict, side):
        self.node_values = self.parse_node_values(viz_dict)
        self.side = side
        self.group_sockets_info = {
            'uv': ('NodeSocketVector', 'INPUT', None, None),
            'basecolor': ('NodeSocketColor', 'OUTPUT', None, None),
            'metalness': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'roughness': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'ior': ('NodeSocketFloat', 'OUTPUT', 1, 2),
            'alpha': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'normal': ('NodeSocketVector', 'OUTPUT', None, None),
            'subsurface_value': ('NodeSocketFloat', 'OUTPUT', 0, None),
            'subsurface_radius': ('NodeSocketVector', 'OUTPUT', 0, 1),
            'specular_value': ('NodeSocketFloat', 'OUTPUT', 0, 2),
            'specular_tint': ('NodeSocketFloat', 'OUTPUT', None, None),
            'anisotropy_value': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'anisotropy_rotation': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'transmission': ('NodeSocketFloat', 'OUTPUT', 0, None),
            'clearcoat_value': ('NodeSocketFloat', 'OUTPUT', 0, None),
            'clearcoat_roughness': ('NodeSocketFloat', 'OUTPUT', 0, 1),
            'clearcoat_normal': ('NodeSocketVector', 'OUTPUT', None, None),
            'sheen_value': ('NodeSocketFloat', 'OUTPUT', 0, None),
            'sheen_tint': ('NodeSocketFloat', 'OUTPUT', 0, None),
            'displacement': ('NodeSocketVector', 'OUTPUT', 0, None)
        }

    def add_group_sockets(self, node_group):
        for name, (socket_type, in_out, min_value, max_value) in self.group_sockets_info.items():
            socket = node_group.interface.new_socket(
                name=name, socket_type=socket_type, in_out=in_out)
            if in_out == 'OUTPUT' and self.node_values[name]:
                if isinstance(socket.default_value, (list, tuple)):
                    socket.default_value = list(self.node_values[name]['constant'])
                else:
                    socket.default_value = self.node_values[name]['constant']
            if min_value is not None:
                socket.min_value = min_value
            if max_value is not None:
                socket.max_value = max_value
    
    def create_node(self, group, node_type, name=None, label=None, location=(0, 0), parent=None, **kwargs):
        node = group.nodes.new(type=node_type)
        node.name = name or node.name
        node.label = label or node.label
        node.location = location
        if parent:
            node.parent = parent
        for key, value in kwargs.items():
            setattr(node, key, value)
        return node

    def create_group_io_nodes(self, node_group):
        group_in = self.create_node(node_group, 'NodeGroupInput', location=(-600, -600))
        group_out = self.create_node(node_group, 'NodeGroupOutput',
                                name='U3M_out', label='U3M_out', location=(1200, -500))
        return group_in, group_out

    def create_texture_node(self, group, name, label, location_y):
        frame_node = self.create_node(group, "NodeFrame",
                                name=f"{name}Frame", label=label, location=(-50, location_y - 50))
        return self.create_node(group, "ShaderNodeTexImage", name=name, label=label, location=(0, location_y), parent=frame_node)

    def create_texture_and_math_nodes(self, node_group):
        spacing_y = -350
        column_x = {0: 0, 1: 300, 2: 600}

        texture_node_info = [
            ("basecolor", "Base Color"),
            ("metalness", "Metalness"),
            ("roughness", "Roughness"),
            ("alpha", "Alpha"),
            ("normal", "Normal"),
            ("displacement", "Displacement")
        ]

        for i, (name, label) in enumerate(texture_node_info):
            self.create_texture_node(node_group, name, label, spacing_y * i)

        for i, name in enumerate(["metalness", "roughness", "alpha"]):
            self.create_node(node_group, "ShaderNodeMath", name=f"{name}_factor",
                        label=f"{name}_factor", location=(column_x[1], spacing_y * (i + 1)), operation='MULTIPLY')
            self.create_node(node_group, "ShaderNodeMath", name=f"{name}_offset",
                        label=f"{name}_offset", location=(column_x[2], spacing_y * (i + 1)), operation='ADD')

        basecolor_factor_node = self.create_node(node_group, "ShaderNodeMixRGB", name="basecolor_factor",
                                            label="basecolor_factor", blend_type='MULTIPLY', location=(column_x[2], 0))
        basecolor_factor_node.inputs['Fac'].default_value = 1
        self.create_node(node_group, "ShaderNodeNormalMap", name="normal_factor",
                    label="normal_factor", location=(column_x[2], spacing_y * 4), space='TANGENT')
        self.create_node(node_group, "ShaderNodeNormalMap", name="clearcoat_normal_factor",
                    label="clearcoat_normal_factor", location=(column_x[2], spacing_y * 5), space='TANGENT')
        self.create_node(node_group, "ShaderNodeDisplacement", name="displacement_height",
                    label="displacement_height", location=(column_x[2], spacing_y * 6))
        displacement_factor_node = self.create_node(node_group, "ShaderNodeMath", name="displacement_factor",
                                                label="displacement_factor", location=(column_x[1], spacing_y * 6), operation='DIVIDE')
        displacement_factor_node.inputs[1].default_value = 100

    def create_mix_nodes(self, node_group):
        spacing_y = -350
        column_x = {3: 900}
        specular_tint_mix_node = self.create_node(node_group, "ShaderNodeMixRGB", name="specular_tint_factor",
                                            label="specular_tint_factor", location=(column_x[3], spacing_y * 0))
        sheen_tint_mix_node = self.create_node(node_group, "ShaderNodeMixRGB", name="sheen_tint_factor",
                                        label="sheen_tint_factor", location=(column_x[3], spacing_y * 1))
        specular_tint_mix_node.inputs['Color1'].default_value = (1, 1, 1, 1)
        specular_tint_mix_node.inputs['Fac'].default_value = self.node_values['specular_tint']['constant']
        sheen_tint_mix_node.inputs['Color1'].default_value = (1, 1, 1, 1)
        sheen_tint_mix_node.inputs['Fac'].default_value = self.node_values['sheen_tint']['constant']

    def create_links(self, node_group, group_in, group_out):
        links = node_group.links

        texture_nodes = ["basecolor", "metalness",
                        "roughness", "alpha", "normal", "displacement"]
        for tex_node in texture_nodes:
            links.new(group_in.outputs['uv'],
                    node_group.nodes[tex_node].inputs['Vector'])

        connections = [
            ("normal", 'Color', "normal_factor", 'Color'),
            ("normal", 'Color', "clearcoat_normal_factor", 'Color'),
            ("basecolor_factor", 'Color', "specular_tint_factor", 'Color2'),
            ("basecolor_factor", 'Color', "sheen_tint_factor", 'Color2'),
            ("basecolor", 'Color', "basecolor_factor", 'Color2'),
            ("basecolor_factor", 'Color', group_out, 'basecolor'),
            ("metalness", 'Color', "metalness_factor", 'Value'),
            ("metalness_factor", 'Value', "metalness_offset", 'Value'),
            ("metalness_offset", 'Value', group_out, 'metalness'),
            ("roughness", 'Color', "roughness_factor", 'Value'),
            ("roughness_factor", 'Value', "roughness_offset", 'Value'),
            ("roughness_offset", 'Value', group_out, 'roughness'),
            ("alpha", 'Color', "alpha_factor", 'Value'),
            ("alpha_factor", 'Value', "alpha_offset", 'Value'),
            ("alpha_offset", 'Value', group_out, 'alpha'),
            ("normal_factor", 'Normal', group_out, 'normal'),
            ("clearcoat_normal_factor", 'Normal', group_out, 'clearcoat_normal'),
            ("displacement", 'Color', "displacement_height", 'Height'),
            ("displacement_factor", 'Value', "displacement_height", 'Scale'),
            ("displacement_height", 'Displacement', group_out, 'displacement'),
            ("specular_tint_factor", 'Color', group_out, 'specular_tint'),
            ("sheen_tint_factor", 'Color', group_out, 'sheen_tint')
        ]

        for src_name, src_socket, dst_name, dst_socket in connections:
            src_node = node_group.nodes[src_name] if isinstance(
                src_name, str) else src_name
            dst_node = node_group.nodes[dst_name] if isinstance(
                dst_name, str) else dst_name
            links.new(src_node.outputs[src_socket], dst_node.inputs[dst_socket])

    def load_image(self, image_path):
        return bpy.data.images.load(image_path) if image_path else None

    def disconnect(self, node_group, node_name):
        output_socket_name = node_name.split('_')[0]
        for link in node_group.links:
            if link.to_node.name == 'U3M_out' and link.to_socket.name == output_socket_name:
                node_group.links.remove(link)

    def set_node_values(self, node_group):
        for node_name, values in self.node_values.items():
            node = node_group.nodes.get(node_name)
            if node_name == 'clearcoat_normal': node = node_group.nodes.get(node_name + '_factor')
            if not node:
                continue
            for attr, value in values.items():
                try:
                    if attr == 'image':
                        image = self.load_image(value)
                        if image:
                            node.image = image
                            if node_name != "basecolor":
                                node.image.colorspace_settings.name = 'Non-Color'
                        else:
                            self.disconnect(node_group, node_name)
                    elif attr == 'factor':
                        node = node_group.nodes.get(node_name + '_factor')
                        if node_name == 'normal' or node_name == 'displacement' or node_name == 'clearcoat_normal':
                            node.inputs[0].default_value = value
                        else:
                            node.inputs[1].default_value = value
                    elif attr == 'offset':
                        node = node_group.nodes.get(node_name + '_offset')
                        node.inputs[1].default_value = value
                except ValueError:
                    print("VALUEERROR WITH NODE: ", node_name)
                except AttributeError:
                    print("AttributeError WITH NODE: ", node_name)

    def create_node_group(self):
        node_group = bpy.data.node_groups.new('U3M_{}'.format(self.side), 'ShaderNodeTree')
        self.add_group_sockets(node_group)
        group_in, group_out = self.create_group_io_nodes(node_group)
        self.create_texture_and_math_nodes(node_group)
        self.create_mix_nodes(node_group)
        self.create_links(node_group, group_in, group_out)
        self.set_node_values(node_group)
        return node_group

    def parse_node_values(self, viz_dict):
        def create_image_constant(image=None, constant=None, factor=None, offset=None):
            value = {'image': image}
            if constant is not None:
                value['constant'] = constant
            if factor is not None:
                value['factor'] = factor
            if offset is not None:
                value['offset'] = offset
            return value

        def get_property(viz_dict, key, property_name, default=None):
            return viz_dict[key]['properties'].get(property_name, [None, default])[1]

        constant_only_nodes = {
            'ior': ('constant',),
            'subsurface_value': ('constant',),
            'specular_value': ('constant',),
            'specular_tint': ('constant',),
            'anisotropy_value': ('constant',),
            'anisotropy_rotation': ('constant',),
            'transmission': ('constant',),
            'clearcoat_value': ('constant',),
            'clearcoat_roughness': ('constant',),
            'sheen_value': ('constant',),
            'sheen_tint': ('constant',),
        }

        common_keys = ['metalness', 'roughness', 'alpha']

        node_values = {
            'basecolor': create_image_constant(
                image=get_property(viz_dict, 'basecolor', 'texture'),
                constant=(
                    get_property(viz_dict, 'basecolor', 'constant_r'),
                    get_property(viz_dict, 'basecolor', 'constant_g'),
                    get_property(viz_dict, 'basecolor', 'constant_b'),
                    1
                ),
                factor=(
                    get_property(viz_dict, 'basecolor', 'factor_r'),
                    get_property(viz_dict, 'basecolor', 'factor_g'),
                    get_property(viz_dict, 'basecolor', 'factor_b'),
                    1
                )
            ),
            'normal': create_image_constant(
                image=get_property(viz_dict, 'normal', 'texture'),
                constant=(1, 1, 1),
                factor=get_property(viz_dict, 'normal', 'factor')
            ),
            'subsurface_radius': {'constant': (
                get_property(viz_dict, 'subsurface_radius', 'constant'),
                get_property(viz_dict, 'subsurface_radius', 'constant'),
                get_property(viz_dict, 'subsurface_radius', 'constant')
            )},
            'clearcoat_normal': {'factor':  get_property(viz_dict, 'clearcoat_normal', 'factor'), 'constant': (0, 0, 0)},
        }

        for key in constant_only_nodes:
            node_values[key] = {prop: get_property(
                viz_dict, key, prop) for prop in constant_only_nodes[key]}

        for key in common_keys:
            node_values[key] = create_image_constant(
                image=get_property(viz_dict, key, 'texture'),
                constant=get_property(viz_dict, key, 'constant'),
                factor=get_property(viz_dict, key, 'factor'),
                offset=get_property(viz_dict, key, 'offset')
            )

        node_values['displacement'] = create_image_constant(
            image=get_property(viz_dict, 'displacement', 'texture'),
            constant=(0, 0, 0),
            factor=get_property(viz_dict, 'displacement', 'factor')
        )
        return node_values

    def get_or_create_node(self, node_tree, node_type, node_name, label, location, settings=None):
        node = node_tree.nodes.get(node_name)
        if not node:
            node = node_tree.nodes.new(type=node_type)
            node.name = node_name
            if label is not None:
                node.label = label
            node.location = location
            if settings:
                for key, value in settings.items():
                    setattr(node, key, value)
        return node

    def build_shader_nodes(self, material):
        node_tree = material.node_tree
        y_offset = -800 if self.side == 'back' else -200

        nodes_info = [
            ('ShaderNodeTexCoord', "Texture Coords", "Texture Coords", (-600, -350)),
            ('ShaderNodeMapping', "global_size", "global_size",
            (-300, -350), {'vector_type': 'TEXTURE'}),
            ('ShaderNodeGroup', "U3M_{}".format(self.side), None, (0, y_offset),
            {'node_tree': self.create_node_group()}),
            ('ShaderNodeBsdfPrincipled', "Principled_BSDF_{}".format(self.side), "Principled_BSDF_{}".format(self.side), (300, y_offset)),
            ('ShaderNodeMixShader', "Mix_Front_Back", "Mix_Front_Back", (600, -300)),
            ('ShaderNodeOutputMaterial', "Material Output", None, (1200, -450)),
            ('ShaderNodeNewGeometry', "Geometry", "Geometry", (300, y_offset + 250)),
            ('ShaderNodeMix', "Mix_Displacement",
            "Mix Displacement", (600, y_offset - 400))
        ]

        nodes = [self.get_or_create_node(node_tree, *info[:4], settings=(info[4] if len(info) > 4 else None)) for info in nodes_info]
        tex_coord_node, mapping_node, group_node, principled_bsdf_node, mix_shader_node, output_node, geometry_node, mix_displacement_node = nodes
        mix_displacement_node.data_type = 'VECTOR'
        mix_displacement_node.inputs['Factor'].default_value = 0
        mix_shader_node.inputs['Fac'].default_value = 0
        links = node_tree.links
        links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], group_node.inputs['uv'])

        links_info = [
            ('basecolor', 'Base Color'),
            ('metalness', 'Metallic'),
            ('roughness', 'Roughness'),
            ('ior', 'IOR'),
            ('alpha', 'Alpha'),
            ('normal', 'Normal'),
            ('subsurface_value', 'Subsurface Weight'),
            ('subsurface_radius', 'Subsurface Radius'),
            ('specular_value', 'Specular IOR Level'),
            ('specular_tint', 'Specular Tint'),
            ('anisotropy_value', 'Anisotropic'),
            ('anisotropy_rotation', 'Anisotropic Rotation'),
            ('transmission', 'Transmission Weight'),
            ('clearcoat_value', 'Coat Weight'),
            ('clearcoat_roughness', 'Coat Roughness'),
            ('clearcoat_normal', 'Coat Normal'),
            ('sheen_value', 'Sheen Weight'),
            ('sheen_tint', 'Sheen Tint')
        ]

        for src_socket, dst_socket in links_info:
            links.new(group_node.outputs[src_socket],
                    principled_bsdf_node.inputs[dst_socket])
        mix_shader_socket = mix_shader_node.inputs[2] if mix_shader_node.inputs[
            1].is_linked else mix_shader_node.inputs[1]
        links.new(principled_bsdf_node.outputs['BSDF'], mix_shader_socket)
        if mix_shader_node.inputs[1].is_linked and mix_shader_node.inputs[2].is_linked:
            links.new(geometry_node.outputs['Backfacing'],
                    mix_shader_node.inputs['Fac'])
        links.new(mix_shader_node.outputs['Shader'], output_node.inputs['Surface'])
        if not mix_displacement_node.inputs['A'].is_linked:
            links.new(group_node.outputs['displacement'],
                    mix_displacement_node.inputs['A'])
        else:
            links.new(group_node.outputs['displacement'],
                    mix_displacement_node.inputs['B'])
            links.new(geometry_node.outputs['Backfacing'],
                    mix_displacement_node.inputs['Factor'])
        links.new(
            mix_displacement_node.outputs['Result'], output_node.inputs['Displacement'])
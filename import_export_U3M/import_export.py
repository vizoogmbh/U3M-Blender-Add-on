import os
import sys
import json
import platform
import subprocess
from shutil import copyfile
from .u3m.parser import U3MParser
from .errors import U3MErrorHandler
from .blender import utils as Blender
from .blender import shader as Shader


class U3MImporter:
    def __init__(self, filepath, assignment_mode, auto_scale):
        self.error_handler = U3MErrorHandler()
        self.parser = U3MParser()
        self.u3m_dir = filepath.parent
        self.u3m_obj = self.parser.load_u3m_from_path(filepath, self.error_handler)
        self.assignment_mode = assignment_mode
        self.auto_scale = auto_scale

    def import_u3m(self):
        if self.u3m_obj is None:
            self.error_handler.handle("loading_failed")
            return
        self.prepare_material()
        self.write_metadata_text()
        self.fill_shader_nodes()
        if self.auto_scale:
            Blender.set_u3m_scale(self.error_handler)

    def prepare_material(self):
        material_name = self.u3m_obj.get_material().get_name()
        Shader.assign_material(material_name, self.assignment_mode)

    def write_metadata_text(self):
        name = self.u3m_obj.get_material().get_name()
        u3m_version = self.parser.get_u3m_version()
        custom_dict = self.u3m_obj.get_custom()

        if custom_dict is not None:
            icon, preview = self.get_icon_and_preview(u3m_version, custom_dict)
        else:
            icon = None
            preview = None
        u3m_str = self.parser.convert_to_string(
            self.u3m_obj.to_dict(self.error_handler)
        )
        texture_size = self.get_texture_size()
        text_name = f"U3M_{name}"
        blender_obj = Blender.get_active_obj()

        if text_name not in Blender.get_texts():
            text = Blender.get_text("U3M").copy()
            text.name = text_name
            text.write(f"u3m_version = '{u3m_version}'\n")
            text.write(f"texture_width = '{texture_size[0]}'\n")
            text.write(f"texture_height = '{texture_size[1]}'\n")
            text.write(f"u3m_dir = r'{self.u3m_dir}'\n")
            text.write(f"u3m_data = r'{u3m_str}'\n")
            text.write(f"preview = '{preview}'\n")
            text.write(f"icon = '{icon}'\n")
            blender_obj.active_material.node_tree.nodes["Metadata"].script = text

    def get_icon_and_preview(self, u3m_version, custom_dict):
        if u3m_version != "1.0":
            return None, None
        vizoo_section = custom_dict.get("Vizoo")
        if vizoo_section is None:
            vizoo_section = custom_dict.get("vizoo")
        if vizoo_section is None:
            return None, None
        return vizoo_section.get("icon"), vizoo_section.get("preview")

    def get_texture_size(self):
        u3m_mat = self.u3m_obj.get_material()
        side = u3m_mat.front if u3m_mat.has_front() else u3m_mat.back

        properties = [
            side.alpha,
            side.basecolor,
            side.displacement,
            side.metalness,
            side.normal,
            side.roughness,
        ]

        for prop in properties:
            if prop is None:
                continue

            texture = getattr(prop, "texture", None)
            if texture is not None:
                return texture.image.width, texture.image.height

        return 10, 10

    def fill_shader_nodes(self):
        Shader.fill_shader_nodes(
            self.parser.get_u3m_version(),
            self.u3m_obj.to_dict(self.error_handler),
            self.u3m_dir,
            self.error_handler,
        )


class U3MExporter:
    def __init__(self):
        self.error_handler = U3MErrorHandler()
        self.parser = U3MParser()
        self.modified = False

    def export_u3m(self, filepath, create_preview):
        self.modified = False

        new_material_name = os.path.splitext(os.path.basename(filepath))[0]
        new_material_folder = os.path.join(
            os.path.dirname(filepath),
            new_material_name,
        )

        original_u3m_data = Blender.get_u3m_data()
        u3m_obj = self.parser.load_u3m_from_str(
            original_u3m_data,
            self.error_handler,
        )

        if u3m_obj is None:
            self.error_handler.handle("writing_failed")
            return

        for side in ["front", "back"]:
            if Shader.has_side(side):
                shader_side_dict = Shader.collect_and_copy_u3m_data(
                    side,
                    new_material_folder,
                    new_material_name,
                )
                u3m_obj = self.compare_and_update_u3m_values(
                    new_material_name,
                    u3m_obj,
                    side,
                    shader_side_dict,
                )
            elif u3m_obj.get_material().has_side(side):
                u3m_obj.get_material().remove_side(side)

        if u3m_obj.get_schema() == "1.1" and u3m_obj.get_material().physics is not None:
            self.copy_physics_file(
                new_material_folder,
                u3m_obj.get_material().physics.devices.fab,
            )

        if u3m_obj.get_schema() == "1.0":
            self.clear_preview_and_icon_entries(u3m_obj.get_custom())

        self.parser.write_u3m(
            u3m_obj,
            os.path.join(new_material_folder, new_material_name + ".u3m"),
            self.error_handler,
        )

        if create_preview:
            preview = self.create_new_preview_and_icon(
                new_material_folder,
                new_material_name,
            )
        else:
            preview = self.copy_preview_and_icon(
                new_material_folder,
                new_material_name,
            )

        if platform.system() == "Windows" and preview:
            self.set_material_folder_icon(new_material_folder)

    def copy_physics_file(self, new_material_folder, physics_file):
        u3m_dir = Blender.get_u3m_dir()
        physics_src = os.path.join(u3m_dir, physics_file)
        physics_dst = os.path.join(new_material_folder, physics_file)

        if physics_src == physics_dst:
            return

        copyfile(physics_src, physics_dst)

    def clear_preview_and_icon_entries(self, custom_dict):
        try:
            vizoo_section = custom_dict.get("Vizoo")
            if vizoo_section is None:
                # Vizoo section is sometimes stored under "vizoo" instead of "Vizoo"
                vizoo_section = custom_dict.get("vizoo")

            if vizoo_section is None:
                raise Exception("Could not find Vizoo custom section")

            vizoo_section.update({"preview": None, "icon": None})
        except Exception:
            print("U3MExporter.clear_preview_and_icon_entries(): Could not clear")

    def update_preview_and_icon_entries(self, material_folder, material_name):
        u3m_file = os.path.join(material_folder, material_name + ".u3m")
        preview_file = os.path.join(material_folder, material_name + ".png")
        icon_file = os.path.join(material_folder, "icon.ico")

        if (
            not os.path.exists(u3m_file)
            or not os.path.exists(preview_file)
            or not os.path.exists(icon_file)
        ):
            return False

        with open(u3m_file, "r") as file:
            u3m_dict = json.load(file)

        updated = False

        if u3m_dict.get("schema") == "1.1":
            material = u3m_dict.get("material")
            if material.get("front") is not None:
                preview_entry = material.get("front").get("preview")
                preview_entry.update(
                    {
                        "path": os.path.basename(preview_file),
                        "height": 500,
                        "width": 500,
                        "dpi": {
                            "x": 127.0,
                            "y": 127.0,
                        },
                    }
                )
                updated = True

        elif u3m_dict.get("schema") == "1.0":
            vizoo_section = u3m_dict.get("custom").get("Vizoo")
            if vizoo_section is None:
                vizoo_section = u3m_dict.get("custom").get("vizoo")

            if vizoo_section is None:
                return False

            vizoo_section.update(
                {
                    "preview": os.path.basename(preview_file),
                    "icon": os.path.basename(icon_file),
                }
            )
            updated = True

        if updated:
            with open(u3m_file, "w") as outfile:
                json.dump(u3m_dict, outfile, indent=4, sort_keys=True)
            return True

        return False

    def copy_preview_and_icon(self, new_material_folder, new_material_name):
        try:
            u3m_dir = Blender.get_u3m_dir()

            preview = Blender.get_preview()
            preview_src = os.path.join(u3m_dir, preview)

            icon = Blender.get_icon()
            icon_src = os.path.join(u3m_dir, icon)

            if (
                not os.path.exists(icon_src)
                or not os.path.exists(preview_src)
                or not os.path.exists(new_material_folder)
            ):
                raise OSError

            icon_dst = os.path.join(new_material_folder, icon)
            preview_dst = os.path.join(new_material_folder, new_material_name + ".png")

            copyfile(icon_src, icon_dst)
            copyfile(preview_src, preview_dst)

            return self.update_preview_and_icon_entries(
                new_material_folder,
                new_material_name,
            )
        except Exception:
            print("U3MExporter.copy_preview_and_icon(): Could not copy")
            return False

    def create_new_preview_and_icon(self, new_material_folder, new_material_name):
        try:
            create_preview_script = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "blender",
                "create_preview_and_icon_script.py",
            )

            if not os.path.exists(create_preview_script):
                raise OSError

            subprocess.run(
                [
                    sys.argv[0],
                    "--background",
                    "--python",
                    create_preview_script,
                    "--",
                    new_material_folder,
                ]
            )

            return self.update_preview_and_icon_entries(
                new_material_folder,
                new_material_name,
            )
        except Exception:
            print("Could not create preview and icon")
            return False

    def set_material_folder_icon(self, new_material_folder):
        icon_path = os.path.join(new_material_folder, "icon.ico")
        desktop_ini_path = os.path.join(new_material_folder, "desktop.ini")
        attrib_exe = os.path.join(os.environ.get("WINDIR"), "System32", "attrib.exe")

        if os.path.exists(desktop_ini_path):
            subprocess.run(
                [attrib_exe, "-s", "-h", "-r", "desktop.ini"],
                cwd=new_material_folder,
            )

        with open(desktop_ini_path, "w") as desktop_ini:
            desktop_ini.write("[.ShellClassInfo]\n")
            desktop_ini.write(f"IconResource={icon_path},0\n")
            desktop_ini.write("[ViewState]\n")
            desktop_ini.write("Mode=\n")
            desktop_ini.write("Vid=\n")
            desktop_ini.write("FolderType=Pictures\n")

        subprocess.run(
            [attrib_exe, "+s", new_material_folder],
            cwd=os.path.dirname(new_material_folder),
        )
        subprocess.run(
            [attrib_exe, "+s", "+h", "desktop.ini"],
            cwd=new_material_folder,
        )

    def compare_and_update_u3m_values(
        self,
        new_material_name,
        u3m_obj,
        side,
        shader_side_dict,
    ):
        u3m_material = u3m_obj.get_material()

        if u3m_material.has_side(side):
            u3m_side_dict = u3m_material.get_side(side)
        else:
            u3m_material.add_side(side, self.error_handler)
            u3m_side_dict = u3m_material.get_side(side)

        for viz_prop in shader_side_dict:
            prop_type = shader_side_dict.get(viz_prop).get("type")

            if prop_type == "texture_and_number":
                self.compare_and_update_texture_and_number(
                    viz_prop,
                    u3m_side_dict,
                    shader_side_dict,
                )
            elif prop_type == "texture_and_color":
                self.compare_and_update_texture_and_color(
                    viz_prop,
                    u3m_side_dict,
                    shader_side_dict,
                )

        if self.modified:
            u3m_material.update()

        if u3m_material.get_name() != new_material_name:
            u3m_material.set_name(new_material_name)

        return u3m_obj

    def compare_and_update_texture_and_number(
        self,
        viz_prop,
        u3m_side_dict,
        shader_side_dict,
    ):
        try:
            u3m_version = self.parser.get_u3m_version()
            u3m_props = u3m_side_dict.get(viz_prop)
            shader_props = shader_side_dict.get(viz_prop).get("properties")

            self.compare_and_update_constant(viz_prop, u3m_props, shader_props)

            if shader_side_dict.get(viz_prop).get("editor_level") != 0:
                return

            if (
                u3m_props.texture != "null"
                and shader_props.get("texture")[1] is not None
            ):
                self.compare_and_update_texture_factor(
                    viz_prop,
                    u3m_version,
                    u3m_props,
                    shader_props,
                )
                self.compare_and_update_texture_path(u3m_props, shader_props)
                self.compare_and_update_texture_offset(
                    viz_prop,
                    u3m_props,
                    shader_props,
                )
            elif (
                u3m_props.texture == "null"
                and shader_props.get("texture")[1] is not None
            ):
                u3m_props.add_texture(self.error_handler)
                u3m_props.texture.factor = shader_props.get("factor")[1]
                u3m_props.texture.image.path.set_path(
                    shader_props.get("texture")[1],
                    self.error_handler,
                )
                u3m_props.texture.image.offset = shader_props.get("offset")[1]
                self.modified = True
            elif u3m_props.texture != "null" and shader_props.get("texture")[1] is None:
                u3m_props.remove_texture()
                self.modified = True
        except Exception:
            print(
                "U3MExporter.compare_and_update_texture_and_number(): "
                f"Could not update value: {viz_prop}"
            )

    def compare_and_update_constant(self, viz_prop, u3m_props, shader_props):
        if viz_prop in {"normal", "clearcoat_normal", "displacement"}:
            return

        if self.compare_float(u3m_props.constant, shader_props.get("constant")[1]):
            u3m_props.constant = shader_props.get("constant")[1]
            self.modified = True

    def compare_and_update_texture_factor(
        self,
        viz_prop,
        u3m_version,
        u3m_props,
        shader_props,
    ):
        if viz_prop == "normal" and u3m_version == "1.1":
            u3m_props.texture.scale = shader_props.get("factor")[1]
            self.modified = True
        elif self.compare_float(
            u3m_props.texture.factor, shader_props.get("factor")[1]
        ):
            u3m_props.texture.factor = shader_props.get("factor")[1]
            self.modified = True

    def compare_and_update_texture_path(self, u3m_props, shader_props):
        if u3m_props.texture.image.path.get_path() != shader_props.get("texture")[1]:
            u3m_props.texture.image.path.set_path(
                shader_props.get("texture")[1],
                self.error_handler,
            )
            self.modified = True

    def compare_and_update_texture_offset(self, viz_prop, u3m_props, shader_props):
        if viz_prop in {"normal", "clearcoat_normal", "displacement"}:
            return

        if self.compare_float(u3m_props.texture.offset, shader_props.get("offset")[1]):
            u3m_props.texture.offset = shader_props.get("offset")[1]
            self.modified = True

    def compare_and_update_texture_and_color(
        self,
        viz_prop,
        u3m_side_dict,
        shader_side_dict,
    ):
        try:
            shader_props = shader_side_dict.get(viz_prop).get("properties")
            u3m_props = u3m_side_dict.get(viz_prop)

            self.compare_and_update_bgr_constants(u3m_props, shader_props)

            if (
                u3m_props.texture is not None
                and shader_props.get("texture")[1] is not None
            ):
                self.compare_and_update_bgr_factors(u3m_props, shader_props)
                self.compare_and_update_texture_path(u3m_props, shader_props)
            elif (
                u3m_props.texture is None and shader_props.get("texture")[1] is not None
            ):
                u3m_props.add_texture(self.error_handler)
                u3m_props.texture.factor.b = shader_props.get("factor_b")[1]
                u3m_props.texture.factor.g = shader_props.get("factor_g")[1]
                u3m_props.texture.factor.r = shader_props.get("factor_r")[1]
                u3m_props.texture.image.path.set_path(
                    shader_props.get("texture")[1],
                    self.error_handler,
                )
                self.modified = True
            elif (
                u3m_props.texture is not None and shader_props.get("texture")[1] is None
            ):
                u3m_props.remove_texture()
                self.modified = True
        except Exception as ex:
            print(
                "U3MExporter.compare_and_update_texture_and_color(): "
                f"Could not update value {viz_prop}: {ex}"
            )

    def compare_and_update_bgr_constants(self, u3m_props, shader_props):
        if self.compare_float(u3m_props.constant.b, shader_props.get("constant_b")[1]):
            u3m_props.constant.b = shader_props.get("constant_b")[1]
            self.modified = True

        if self.compare_float(u3m_props.constant.g, shader_props.get("constant_g")[1]):
            u3m_props.constant.g = shader_props.get("constant_g")[1]
            self.modified = True

        if self.compare_float(u3m_props.constant.r, shader_props.get("constant_r")[1]):
            u3m_props.constant.r = shader_props.get("constant_r")[1]
            self.modified = True

    def compare_and_update_bgr_factors(self, u3m_props, shader_props):
        if self.compare_float(
            u3m_props.texture.factor.b, shader_props.get("factor_b")[1]
        ):
            u3m_props.texture.factor.b = shader_props.get("factor_b")[1]
            self.modified = True

        if self.compare_float(
            u3m_props.texture.factor.g, shader_props.get("factor_g")[1]
        ):
            u3m_props.texture.factor.g = shader_props.get("factor_g")[1]
            self.modified = True

        if self.compare_float(
            u3m_props.texture.factor.r, shader_props.get("factor_r")[1]
        ):
            u3m_props.texture.factor.r = shader_props.get("factor_r")[1]
            self.modified = True

    def compare_float(self, value_one, value_two):
        precision = 1e-5
        return abs(value_one - value_two) >= precision

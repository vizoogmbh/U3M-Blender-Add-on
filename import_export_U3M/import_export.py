import os
import sys
import json
import platform
import subprocess
from shutil import copyfile
from import_export_U3M.u3m.parser import U3MParser
from import_export_U3M.errors import U3MErrorHandler
from import_export_U3M.blender import utils as Blender
from import_export_U3M.blender import shader as Shader


class U3MImporter:

    def __init__(self, filepath, use_linked_mat, auto_scale, error_handling):
        self.error_handler = U3MErrorHandler(error_handling)
        self.parser = U3MParser()
        self.u3m_dir = filepath.parents[0]
        self.u3m_obj = self.parser.load_u3m_from_path(
            filepath, self.error_handler)
        self.use_linked_mat = use_linked_mat
        self.auto_scale = auto_scale

    def import_u3m(self):
        if self.u3m_obj is not None:
            self.prepare_material()
            self.write_metadata_text()
            self.fill_shader_nodes()
            if self.auto_scale:
                Blender.set_u3m_scale(self.error_handler)
        else:
            self.error_handler.handle('loading_failed')

    def prepare_material(self):
        material_name = self.u3m_obj.get_material().get_name()
        Shader.assign_material(material_name, self.use_linked_mat)

    def write_metadata_text(self):
        name = self.u3m_obj.get_material().get_name()
        u3m_version = self.parser.get_u3m_version()
        custom_dict = self.u3m_obj.get_custom()
        if custom_dict != None:
            icon, preview = self.get_icon_and_preview(u3m_version, custom_dict)
        else:
            icon = None
            preview = None
        u3m_str = self.parser.convert_to_string(
            self.u3m_obj.to_dict(self.error_handler))
        texture_size = self.get_texture_size()
        t_name = "U3M_" + name
        blender_obj = Blender.get_active_obj()
        if t_name not in Blender.get_texts():
            t = Blender.get_text("U3M").copy()
            t.name = t_name
            t.write("u3m_version = '%s'\n" % u3m_version)
            t.write("texture_width = '%s'\n" % str(texture_size[0]))
            t.write("texture_height = '%s'\n" % str(texture_size[1]))
            t.write("u3m_dir = r'%s'\n" % str(self.u3m_dir))
            t.write("u3m_data = '%s'\n" % u3m_str)
            t.write("preview = '%s'\n" % str(preview))
            t.write("icon = '%s'\n" % str(icon))
            blender_obj.active_material.node_tree.nodes["Metadata"].script = t

    def get_icon_and_preview(self, u3m_version, custom_dict):
        icon = None
        preview = None
        if u3m_version != "1.0":
            return icon, preview
        vizoo_section = custom_dict.get("Vizoo")
        if vizoo_section == None:
            # vizoo section sometimes stored under "vizoo" instead of "Vizoo"
            vizoo_section = custom_dict.get("vizoo")
        if vizoo_section == None:
            return icon, preview
        icon = vizoo_section.get("icon")
        preview = vizoo_section.get("preview")
        return icon, preview

    def get_texture_size(self):
        u3m_mat = self.u3m_obj.get_material()
        if u3m_mat.has_front():
            if u3m_mat.front.alpha.texture != None:
                texture_height = u3m_mat.front.alpha.texture.image.height
                texture_width = u3m_mat.front.alpha.texture.image.width
                return (texture_width, texture_height)
            elif u3m_mat.front.basecolor.texture != None:
                texture_height = u3m_mat.front.basecolor.texture.image.height
                texture_width = u3m_mat.front.basecolor.textue.image.width
                return (texture_width, texture_height)
        else:
            if u3m_mat.back.alpha.texture != None:
                texture_height = u3m_mat.back.alpha.texture.image.height
                texture_width = u3m_mat.back.alpha.texture.image.width
                return (texture_width, texture_height)
            elif u3m_mat.front.basecolor.texture != None:
                texture_height = u3m_mat.back.basecolor.texture.image.height
                texture_width = u3m_mat.back.basecolor.texture.image.width
                return (texture_width, texture_height)

    def fill_shader_nodes(self):
        Shader.fill_shader_nodes(self.parser.get_u3m_version(), self.u3m_obj.to_dict(
            self.error_handler), self.u3m_dir, self.error_handler)


class U3MExporter:

    def __init__(self, error_handling):
        self.error_handler = U3MErrorHandler(error_handling)
        self.parser = U3MParser()
        self.modified = False

    def export_u3m(self, filepath, create_preview):
        new_material_name = os.path.splitext(os.path.basename(filepath))[0]
        new_material_folder = os.path.join(
            os.path.dirname(filepath), new_material_name)
        original_u3m_data = Blender.get_u3m_data()
        u3m_obj = self.parser.load_u3m_from_str(
            original_u3m_data, self.error_handler)
        if u3m_obj is not None:
            for side in ["front", "back"]:
                if Shader.has_side(side):
                    shader_side_dict = Shader.collect_and_copy_u3m_data(
                        side, new_material_folder, new_material_name)
                    u3m_obj = self.compare_and_update_u3m_values(
                        new_material_name, u3m_obj, side, shader_side_dict)
                # check if whole side was removed
                elif Shader.has_side(side) == False and u3m_obj.get_material().has_side(side) == True:
                    u3m_obj.get_material().remove_side(side)
            # setting preview and icon to "None" before trying to create or copy preview and icon
            self.clear_preview_and_icon_entries(u3m_obj.get_custom())
            self.parser.write_u3m(u3m_obj, os.path.join(
                new_material_folder, new_material_name + ".u3m"), self.error_handler)
            if create_preview:
                preview = self.create_new_preview_and_icon(
                    new_material_folder, new_material_name)
            else:
                preview = self.copy_preview_and_icon(
                    new_material_folder, new_material_name)
            if platform.system() == "Windows" and preview:
                self.set_material_folder_icon(new_material_folder)
        else:
            self.error_handler('writing_failed')

    def clear_preview_and_icon_entries(self, custom_dict):
        try:
            vizoo_section = custom_dict.get("Vizoo")
            if vizoo_section == None:
                vizoo_section = custom_dict.get("vizoo")
            if vizoo_section == None:
                raise Exception("couldnt find vizoo custom section")
            vizoo_section.update({"preview": None, "icon": None})
        except Exception:
            print("U3M_Exporter.clear_preview_and_icon_entries(): Could not clear!")

    def update_preview_and_icon_entries(self, material_folder, material_name):
        try:
            u3m_file = os.path.join(material_folder, material_name + ".u3m")
            preview_file = os.path.join(
                material_folder, material_name + ".png")
            icon_file = os.path.join(material_folder, "icon.ico")
            if os.path.exists(u3m_file) == False or os.path.exists(preview_file) == False or os.path.exists(icon_file) == False:
                raise OSError
            u3m_dict = json.loads(open(u3m_file, 'r').read())
            vizoo_section = u3m_dict.get("custom").get("Vizoo")
            if vizoo_section == None:
                vizoo_section = u3m_dict.get("custom").get("vizoo")
            if vizoo_section == None:
                raise Exception("couldnt find vizoo custom section")
            vizoo_section.update({"preview": os.path.basename(
                preview_file), "icon": os.path.basename(icon_file)})
            with open(u3m_file, "w") as outfile:
                json.dump(u3m_dict, outfile, indent=4, sort_keys=True)
            return True
        except Exception:
            print("U3M_Exporter.update_preview_and_icon_entries(): Could not update!")
            return False

    def copy_preview_and_icon(self, new_material_folder, new_material_name):
        try:
            u3m_dir = Blender.get_u3m_dir()
            preview = Blender.get_preview()
            preview_src = os.path.join(u3m_dir, preview)
            icon = Blender.get_icon()
            icon_src = os.path.join(u3m_dir, icon)
            if os.path.exists(icon_src) == False or os.path.exists(preview_src) == False or os.path.exists(new_material_folder) == False:
                raise OSError
            icon_dst = os.path.join(new_material_folder, icon)
            preview_dst = os.path.join(
                new_material_folder, new_material_name + ".png")
            copyfile(icon_src, icon_dst)
            copyfile(preview_src, preview_dst)
            return self.update_preview_and_icon_entries(new_material_folder, new_material_name)
        except Exception:
            print("EXCEPTION: U3MExporter.copy_preview_and_icon: couldn't copy!")
            return False

    def create_new_preview_and_icon(self, new_material_folder, new_material_name):
        try:
            create_preview_script = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "blender", "create_preview_and_icon_script.py")
            if os.path.exists(create_preview_script) == False:
                raise OSError
            else:
                subprocess.run([sys.argv[0], "--background", "--python",
                               create_preview_script, "--", new_material_folder])
            return self.update_preview_and_icon_entries(new_material_folder, new_material_name)
        except:
            print("some error occurred: couldnt create preview and icon")
            return False

    def set_material_folder_icon(self, new_material_folder):
        icon_path = os.path.join(new_material_folder, "icon.ico")
        attrib_exe = os.path.join(os.environ.get(
            'WINDIR'), "System32", "attrib.exe")
        if os.path.exists(attrib_exe) == False or os.path.exists(icon_path) == False:
            raise OSError
        else:
            subprocess.Popen([attrib_exe, "+s", new_material_folder],
                             cwd=os.path.dirname(new_material_folder))
        with open(os.path.join(new_material_folder, "desktop.ini"), "w") as desktop_ini:
            desktop_ini.write("[.ShellClassInfo]\n")
            desktop_ini.write("IconResource=" + icon_path + ",0\n")
            desktop_ini.write("[ViewState]\n")
            desktop_ini.write("Mode=\n")
            desktop_ini.write("Vid=\n")
            desktop_ini.write("FolderType=Pictures\n")
        subprocess.Popen(
            [attrib_exe, "+s", "+h", "desktop.ini"], cwd=new_material_folder)

    # compare and update all editable u3m values
    def compare_and_update_u3m_values(self, new_material_name, u3m_obj, side, shader_side_dict):
        u3m_material = u3m_obj.get_material()
        if u3m_material.has_side(side):
            u3m_side_dict = u3m_obj.get_material().get_side(side)
        else:
            u3m_obj.get_material().add_side(side)
            u3m_side_dict = u3m_obj.get_material().get_side(side)

        viz_tan_props = ["alpha", "displacement", "metalness", "normal", "roughness", "anisotropy_rotation", "anisotropy_value",
                         "clearcoat_roughness", "ior", "sheen_tint", "sheen_value", "specular_tint", "specular_value", "specular_value", "transmission"]
        for viz_prop in viz_tan_props:
            self.compare_and_update_texture_and_number(
                viz_prop, u3m_side_dict, shader_side_dict)
        self.compare_and_update_basecolor(u3m_side_dict, shader_side_dict)
        if self.modified:
            u3m_material.update()
        if u3m_material.get_name() != new_material_name:
            u3m_material.set_name(new_material_name)
        return u3m_obj

    def compare_and_update_texture_and_number(self, viz_prop, u3m_side_dict, shader_side_dict):
        try:
            u3m_version = self.parser.get_u3m_version()
            u3m_props = u3m_side_dict.get(viz_prop)
            shader_props = shader_side_dict.get(viz_prop).get("properties")
            self.compare_and_update_constant(viz_prop, u3m_props, shader_props)
            # check if original file and shader have a texture
            if u3m_props.texture != "null" and shader_props.get("texture")[1] != None:
                self.compare_and_update_texture_factor(
                    viz_prop, u3m_version, u3m_props, shader_props)
                self.compare_and_update_texture_path(u3m_props, shader_props)
                self.compare_and_update_texture_offset(
                    viz_prop, u3m_props, shader_props)
            # check if texture was added in editor
            elif u3m_props.texture == "null" and shader_props.get("texture")[1] != None:
                u3m_props.add_texture(self.error_handler)
                u3m_props.texture.factor = shader_props.get("factor")[1]
                u3m_props.texture.image.path.set_path(
                    shader_props.get("texture")[1], self.error_handler)
                u3m_props.texture.image.offset = shader_props.get("offset")[1]
                self.modified = True
            # check if texture was removed in editor
            elif u3m_props.texture != "null" and shader_props.get("texture")[1] == None:
                u3m_props.remove_texture()
                self.modified = True
        except Exception:
            print("EXCEPTION: U3MExporter.compare_and_update_texture_and_number(): Couldn't update value: ", viz_prop)

    def compare_and_update_constant(self, viz_prop, u3m_props, shader_props):
        if viz_prop == "normal" or viz_prop == "displacement":
            pass  # normal and displacement dont have a constant in the shader
        elif self.compare_float(u3m_props.constant, shader_props.get("constant")[1]):
            u3m_props.constant = shader_props.get("constant")[1]
            self.modified = True

    def compare_and_update_texture_factor(self, viz_prop, u3m_version, u3m_props, shader_props):
        if viz_prop == "normal" and u3m_version == "1.1":
            # U3M 1.1 Normal doesnt have factor, but scale
            u3m_props.texture.scale = shader_props.get("factor")[1]
        elif self.compare_float(u3m_props.texture.factor, shader_props.get("factor")[1]):
            u3m_props.texture.factor = shader_props.get("factor")[1]
            self.modified = True

    def compare_and_update_texture_path(self, u3m_props, shader_props):
        if u3m_props.texture.image.path.get_path() != shader_props.get("texture")[1]:
            u3m_props.texture.image.path.set_path(
                shader_props.get("texture")[1], self.error_handler)
            self.modified = True

    def compare_and_update_texture_offset(self, viz_prop, u3m_props, shader_props):
        if viz_prop == "normal" or viz_prop == "displacement":
            pass  # normal and disp doesnt have a offset in the shader
        elif self.compare_float(u3m_props.texture.offset, shader_props.get("offset")[1]):
            u3m_props.texture.offset = shader_props.get("offset")[1]
            self.modified = True

    def compare_and_update_basecolor(self, u3m_side_dict, shader_side_dict):
        try:
            basecolor_props = shader_side_dict.get(
                "basecolor").get("properties")
            self.compare_and_update_bgr_constants(
                u3m_side_dict, basecolor_props)
            # check if original file and shader have a texture
            if u3m_side_dict.basecolor.texture != "null" and basecolor_props.get("texture")[1] != None:
                self.compare_and_update_bgr_factors(
                    u3m_side_dict, basecolor_props)
                self.compare_and_update_texture_path(
                    u3m_side_dict.basecolor, basecolor_props)
            # check if texture was added in editor
            elif u3m_side_dict.basecolor.texture != "null" and basecolor_props.get("texture")[1] != None:
                u3m_side_dict.basecolor.add_texture()
                u3m_side_dict.basecolor.texture.factor.b = basecolor_props.get("factor_b")[
                    1]
                u3m_side_dict.basecolor.texture.factor.g = basecolor_props.get("factor_g")[
                    1]
                u3m_side_dict.basecolor.texture.factor.r = basecolor_props.get("factor_r")[
                    1]
                u3m_side_dict.basecolor.texture.image.path.set_path(
                    basecolor_props.get("texture")[1], self.error_handler)
                self.modified = True
            # check if texture was removed in editor
            elif u3m_side_dict.basecolor.texture != "null" and basecolor_props.get("texture")[1] == None:
                u3m_side_dict.alpha.remove_texture()
                self.modified = True
        except Exception:
            print(
                "EXCEPTION: U3MExporter.compare_and_update_basecolor(): Couldn't update value! ")

    def compare_and_update_bgr_constants(self, u3m_side_dict, basecolor_props):
        if self.compare_float(u3m_side_dict.basecolor.constant.b, basecolor_props.get("constant_b")[1]):
            u3m_side_dict.basecolor.constant.b = basecolor_props.get("constant_b")[
                1]
            self.modified = True
        if self.compare_float(u3m_side_dict.basecolor.constant.g, basecolor_props.get("constant_g")[1]):
            u3m_side_dict.basecolor.constant.g = basecolor_props.get("constant_g")[
                1]
            self.modified = True
        if self.compare_float(u3m_side_dict.basecolor.constant.r, basecolor_props.get("constant_r")[1]):
            u3m_side_dict.basecolor.constant.r = basecolor_props.get("constant_r")[
                1]
            self.modified = True

    def compare_and_update_bgr_factors(self, u3m_side_dict, basecolor_props):
        if self.compare_float(u3m_side_dict.basecolor.texture.factor.b, basecolor_props.get("factor_b")[1]):
            u3m_side_dict.basecolor.texture.factor.b = basecolor_props.get("factor_b")[
                1]
            self.modified = True
        if self.compare_float(u3m_side_dict.basecolor.texture.factor.g, basecolor_props.get("factor_g")[1]):
            u3m_side_dict.basecolor.texture.factor.g = basecolor_props.get("factor_g")[
                1]
            self.modified = True
        if self.compare_float(u3m_side_dict.basecolor.texture.factor.r, basecolor_props.get("factor_r")[1]):
            u3m_side_dict.basecolor.texture.factor.r = basecolor_props.get("factor_r")[
                1]
            self.modified = True

    def compare_float(self, value_one, value_two):
        precision = 10 ^ -5
        return abs(value_one-value_two) >= precision

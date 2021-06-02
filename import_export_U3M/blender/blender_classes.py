
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)
from pathlib import Path

from . import utils
from import_export_U3M.import_export import U3MImporter, U3MExporter
from import_export_U3M.blender import shader_template
from import_export_U3M import editor

from import_export_U3M.editor import (
    U3MEditPanelFrontBase,
    U3MEditPanelFrontAdvancedBase,
    U3MEditPanelBackBase,
    U3MEditPanelBackAdvancedBase,
    AddSideOperatorBase,
    RemoveSideOperatorBase
)

from import_export_U3M.views import (
    ViewOperatorBase,
    RenderPreviewBase,
    InitOperatorBase
)

from import_export_U3M.errors import U3MErrorHandler


class ImportU3M(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.u3m"
    bl_label = "Import U3M"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".u3m"

    filter_glob: StringProperty(
        default="*.u3m;",
        options={'HIDDEN'},
    )

    use_linked_mat: BoolProperty(
        name="Link materials",
        description="Apply the material to the selected object and all other objects with the same material",
        default=True,
    )

    auto_scale: BoolProperty(
        name="Auto scale",
        description="Automatically scale the material",
        default=True,
    )

    error_handling: EnumProperty(
        name="Error Handling",
        description="mode for error handling (STRICT, RELAXED, USER)",
        items={
            ('STRICT', 'strict', 'strict error handling mode'),
            ('RELAXED', 'relaxed', 'relaxed error handling mode'),
            ('USER', 'user', 'user error handling mode')},
        default='USER'
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        filepath = Path(self.as_keywords()['filepath'])
        use_linked_mat = self.as_keywords()['use_linked_mat']
        auto_scale = self.as_keywords()['auto_scale']
        error_handling = self.as_keywords()['error_handling']
        if "U3M" not in bpy.data.scenes:
            print("Loading U3M Scene...")
            bpy.ops.myops.u3m_init()
        importer = U3MImporter(filepath, use_linked_mat,
                               auto_scale, error_handling)
        importer.import_u3m()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "use_linked_mat")
        row = layout.row(align=True)
        row.prop(self, "auto_scale")


class ExportU3M(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.u3m"
    bl_label = "U3M Export"

    filename_ext = ".u3m"

    create_preview: BoolProperty(
        name="create preview and icon",
        description="create a new preview and icon for this material (uncheck this to copy original preview&icon, if there is some)",
        default=True,
    )

    filter_glob: StringProperty(
        default="*.u3m;",
        options={'HIDDEN'},
    )

    error_handling: EnumProperty(
        name="Error Handling",
        description="mode for error handling (STRICT, RELAXED, USER)",
        items={
            ('STRICT', 'strict', 'strict error handling mode'),
            ('RELAXED', 'relaxed', 'relaxed error handling mode'),
            ('USER', 'user', 'user error handling mode')},
        default='USER'
    )

    @classmethod
    def poll(cls, context):
        if context.object:
            return len(context.selected_objects) == 1 and utils.context_is_u3m(context) is True

    def execute(self, context):
        filepath = Path(self.as_keywords()['filepath'])
        preview = self.as_keywords()['create_preview']
        error_handling = self.as_keywords()['error_handling']
        print("Saving... ", filepath)
        exporter = U3MExporter(error_handling)
        exporter.export_u3m(filepath, preview)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class U3MScaleOperator(bpy.types.Operator):
    bl_idname = "object.u3m_scale_operator"
    bl_label = "U3M Calculate UVs Operator"
    bpy.types.Scene.u3m_width = bpy.props.FloatProperty(
        name="Width (mm/repeat)", description="texture width", default=0)
    bpy.types.Scene.u3m_height = bpy.props.FloatProperty(
        name="Height (mm/repeat)", description="texture height", default=0)

    def scale(self, context):
        error_handler = U3MErrorHandler('USER')
        utils.set_u3m_scale(error_handler)

    def set(self, context, obj, scale_x, scale_y, size):
        global_scale_x = 1/scale_x*(size/100)
        global_scale_y = 1/scale_y*(size/100)
        for side in shader_template.u3m_pbr["sides"]:
            try:
                obj.active_material.node_tree.nodes["U3M_" +
                                                    side].node_tree.nodes["global_size"].inputs['Scale'].default_value = global_scale_x, global_scale_y, 1
            except:
                pass

    def execute(self, context):
        self.scale(context)
        return {'FINISHED'}


class U3MEditPanel(bpy.types.Panel):
    bl_label = "U3M Editor"
    bl_idname = "SCENE_PT_U3ME"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'U3M'

    def draw(self, context):
        self.layout.prop_search(
            context.object, "active_material", bpy.data, "materials")


class U3MEditPanelFront(bpy.types.Panel, U3MEditPanelFrontBase):
    bl_label = "Front Side"
    bl_idname = "SCENE_PT_U3MEF"
    bl_parent_id = "SCENE_PT_U3ME"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class U3MEditPanelFrontAdvanced(bpy.types.Panel, U3MEditPanelFrontAdvancedBase):
    bl_label = "Advanced Parameters"
    bl_idname = "SCENE_PT_U3MEFA"
    bl_parent_id = "SCENE_PT_U3MEF"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}


class U3MEditPanelBack(bpy.types.Panel, U3MEditPanelBackBase):
    bl_label = "Back Side"
    bl_idname = "SCENE_PT_U3MEB"
    bl_parent_id = "SCENE_PT_U3ME"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}


class U3MEditPanelBackAdvanced(bpy.types.Panel, U3MEditPanelBackAdvancedBase):
    bl_label = "Advanced Parameters"
    bl_idname = "SCENE_PT_U3MEBA"
    bl_parent_id = "SCENE_PT_U3MEB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}


class U3MToolsPanel(bpy.types.Panel):
    bl_label = "U3M Tools"
    bl_idname = "SCENE_PT_U3MT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        if context.object:
            if len(context.selected_objects) == 1:
                if context.object.active_material:
                    for node in context.object.active_material.node_tree.nodes:
                        if "U3M_" in node.name:
                            return True
        return False

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Scaling")
        box = layout.box()
        box.label(text="Texture Measurements:")
        row = box.row()
        row.prop(context.scene, "u3m_width")
        row.enabled = False
        row = box.row()
        row.prop(context.scene, "u3m_height")
        row.enabled = False
        split = layout.split()
        col = split.column(align=True)
        col.prop(context.scene, "u3m_size")
        col.operator("object.u3m_scale_operator",
                     text="scale to physical size")


class InitOperator(bpy.types.Operator, InitOperatorBase):
    bl_idname = "myops.u3m_init"
    bl_label = "U3M Init Operator"


class U3MViewsPanel(bpy.types.Panel):

    bl_label = "U3M Views"
    bl_idname = "SCENE_PT_U3MV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'U3M'

    @classmethod
    def poll(cls, context):
        return "U3M" in bpy.data.scenes and "Views" in bpy.data.collections

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        split = layout.split()
        col = split.column(align=True)
        for view in bpy.data.collections["Views"].children:
            v = col.operator("myops.u3m_view", text=view.name)
            v.view_name = view.name
        box = layout.box()
        box.label(text="Preview Image")
        row = box.row()
        row.prop(scene.render, "engine", text="Render Engine:")
        row = box.row(align=True)
        row.label(text="Resolution (x/y):")
        row.prop(scene.render, "resolution_x", text="")
        row.prop(scene.render, "resolution_y", text="")
        row = box.row()
        row.prop(scene.render, "filepath")
        row = box.row()
        row.prop(scene.render.image_settings, "file_format")
        row = layout.row()
        row.operator("myops.u3m_render_preview", text="Save Preview Image")


class ViewOperator(bpy.types.Operator, ViewOperatorBase):
    bl_idname = "myops.u3m_view"
    bl_label = "U3M View"

    view_name: StringProperty(default="Standard", options={'HIDDEN'},)


class AddSideOperator(bpy.types.Operator, AddSideOperatorBase):
    bl_idname = "myops.u3m_add_side"
    bl_label = "Add Side"
    id: bpy.props.IntProperty()


class RemoveSideOperator(bpy.types.Operator, RemoveSideOperatorBase):
    bl_idname = "myops.u3m_remove_side"
    bl_label = "Remove Side"
    id: bpy.props.IntProperty()


class RenderPreview(bpy.types.Operator, RenderPreviewBase):
    bl_idname = "myops.u3m_render_preview"
    bl_label = "U3M Render Preview"


class LoadTextureOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "myops.u3m_load_texture"
    bl_label = "Load Texture Operator"
    bl_description = "Opens the file dialogue to load a texture"
    pnode: bpy.props.StringProperty()

    def execute(self, context):
        image_path = self.as_keywords()["filepath"]
        n = self.pnode.split("_&_")
        node_group, side, node_name = n[0], n[1], n[2]
        editor.add_texture(context, node_group, side, node_name, image_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RemoveTextureOperator(bpy.types.Operator):
    bl_idname = "myops.u3m_remove_texture"
    bl_label = "Remove Texture?"
    bl_description = "Removes the texture from the shader"
    pnode: bpy.props.StringProperty()

    def execute(self, context):
        n = self.pnode.split("_&_")
        node_group, side, node_name = n[0], n[1], n[2]
        editor.remove_texture(context, node_group, side, node_name)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class ErrorMessageConfirmation(bpy.types.Operator):
    bl_idname = "wm.error_confirm"
    bl_label = "U3M Error:"
    bpy.types.Scene.error_message = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text=bpy.context.scene.error_message)

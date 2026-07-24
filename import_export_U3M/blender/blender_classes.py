import bpy
from bpy.props import BoolProperty, StringProperty

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)
from pathlib import Path

from . import utils
from ..import_export import U3MImporter, U3MExporter
from .shader import MaterialAssignmentMode
from .. import editor

from ..editor import (
    U3MEditPanelFrontBase,
    U3MEditPanelFrontAdvancedBase,
    U3MEditPanelBackBase,
    U3MEditPanelBackAdvancedBase,
    AddSideOperatorBase,
    RemoveSideOperatorBase,
    ToggleAlphaOperatorBase,
)

from ..views import ViewOperatorBase, RenderPreviewBase, InitOperatorBase

from ..errors import U3MErrorHandler


class ImportU3M(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.u3m"
    bl_label = "Import U3M"
    bl_description = "Load a U3M file"
    bl_options = {"PRESET", "UNDO"}
    filename_ext = ".u3m"

    filter_glob: StringProperty(
        default="*.u3m",
        options={"HIDDEN"},
    )

    use_linked_mat: BoolProperty(
        name="Link Materials",
        description="Apply the material to the active object and all other objects with the same material",
        default=False,
    )

    apply_to_selection: BoolProperty(
        name="Apply to Selection",
        description="Apply the material to all selected objects",
        default=False,
    )

    auto_scale: BoolProperty(
        name="Auto Scale",
        description="Automatically scale the material",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        filepath = Path(self.filepath)

        assignment_mode = (
            MaterialAssignmentMode.LINKED
            if self.use_linked_mat
            else (
                MaterialAssignmentMode.SELECTION
                if self.apply_to_selection
                else MaterialAssignmentMode.ACTIVE_ONLY
            )
        )

        if "U3M" not in bpy.data.workspaces:
            bpy.ops.myops.u3m_init()

        importer = U3MImporter(
            filepath,
            assignment_mode,
            self.auto_scale,
        )
        importer.import_u3m()

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_linked_mat")
        layout.prop(self, "apply_to_selection")
        layout.prop(self, "auto_scale")


class ExportU3M(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.u3m"
    bl_label = "U3M Export"
    bl_description = "Export a U3M file"

    filename_ext = ".u3m"

    create_preview: BoolProperty(
        name="Create Preview and Icon",
        description="Create a new preview and icon for this material. Disable this to copy the existing preview and icon if available",
        default=True,
    )

    filter_glob: StringProperty(
        default="*.u3m",
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and len(context.selected_objects) == 1
            and utils.context_is_u3m(context)
        )

    def execute(self, context):
        try:
            filepath = Path(self.filepath)

            exporter = U3MExporter()
            exporter.export_u3m(filepath, self.create_preview)

            return {"FINISHED"}
        except Exception as ex:
            self.report({"ERROR"}, f"Failed to export U3M: {ex}")
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class U3MScaleOperator(bpy.types.Operator):
    bl_idname = "object.u3m_scale_operator"
    bl_label = "U3M Calculate UVs"
    bl_description = "Scale the material to physical size"

    @classmethod
    def poll(cls, context):
        return context.object is not None and utils.context_is_u3m(context)

    def scale(self, context):
        error_handler = U3MErrorHandler()
        utils.set_u3m_scale(error_handler)

    @staticmethod
    def apply_scale(obj, scale_x, scale_y, size):
        obj.active_material.node_tree.nodes["global_size"].inputs[
            "Scale"
        ].default_value = (
            1 / scale_x * (size / 100),
            1 / scale_y * (size / 100),
            1,
        )

    def execute(self, context):
        self.scale(context)
        return {"FINISHED"}


class U3MEditPanel(bpy.types.Panel):
    bl_label = "U3M Editor"
    bl_idname = "SCENE_PT_U3ME"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "U3M"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj is not None:
            layout.prop_search(
                obj,
                "active_material",
                bpy.data,
                "materials",
            )


class U3MEditPanelFront(bpy.types.Panel, U3MEditPanelFrontBase):
    bl_label = "Front Side"
    bl_idname = "SCENE_PT_U3MEF"
    bl_parent_id = "SCENE_PT_U3ME"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class U3MEditPanelFrontAdvanced(bpy.types.Panel, U3MEditPanelFrontAdvancedBase):
    bl_label = "Advanced Parameters"
    bl_idname = "SCENE_PT_U3MEFA"
    bl_parent_id = "SCENE_PT_U3MEF"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}


class U3MEditPanelBack(bpy.types.Panel, U3MEditPanelBackBase):
    bl_label = "Back Side"
    bl_idname = "SCENE_PT_U3MEB"
    bl_parent_id = "SCENE_PT_U3ME"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}


class U3MEditPanelBackAdvanced(bpy.types.Panel, U3MEditPanelBackAdvancedBase):
    bl_label = "Advanced Parameters"
    bl_idname = "SCENE_PT_U3MEBA"
    bl_parent_id = "SCENE_PT_U3MEB"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}


class U3MToolsPanel(bpy.types.Panel):
    bl_label = "U3M Tools"
    bl_idname = "SCENE_PT_U3MT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "U3M"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and len(context.selected_objects) == 1
            and obj.active_material is not None
            and obj.active_material.node_tree is not None
            and any("U3M_" in node.name for node in obj.active_material.node_tree.nodes)
        )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Scaling")
        box = layout.box()
        box.label(text="Texture Measurements:")
        row = box.row()
        row.prop(context.scene, "u3m_width")
        row.enabled = False
        row = box.row()
        row.prop(context.scene, "u3m_height")
        row.enabled = False
        col = layout.column(align=True)
        col.prop(context.scene, "u3m_size")
        col.operator("object.u3m_scale_operator", text="Scale to Physical Size")


class InitOperator(bpy.types.Operator, InitOperatorBase):
    bl_idname = "myops.u3m_init"
    bl_label = "U3M Init Operator"


class U3MViewsPanel(bpy.types.Panel):

    bl_label = "U3M Views"
    bl_idname = "SCENE_PT_U3MV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "U3M"

    @classmethod
    def poll(cls, context):
        return "U3M" in bpy.data.scenes and "Views" in bpy.data.collections

    def draw(self, context):
        layout = self.layout
        scene = context.scene
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

    view_name: StringProperty(
        default="Standard",
        options={"HIDDEN"},
    )


class AddSideOperator(bpy.types.Operator, AddSideOperatorBase):
    bl_idname = "myops.u3m_add_side"
    bl_label = "Add Side"
    bl_description = "Add Side to Material"
    id: bpy.props.IntProperty()


class RemoveSideOperator(bpy.types.Operator, RemoveSideOperatorBase):
    bl_idname = "myops.u3m_remove_side"
    bl_label = "Remove Side"
    bl_description = "Remove Side from Material"
    id: bpy.props.IntProperty()


class ToggleAlphaOperator(bpy.types.Operator, ToggleAlphaOperatorBase):
    bl_idname = "myops.u3m_toggle_alpha"
    bl_label = "Toggle Alpha"
    bl_description = "Toggle Alpha for current U3M"
    id: bpy.props.IntProperty()


class RenderPreview(bpy.types.Operator, RenderPreviewBase):
    bl_idname = "myops.u3m_render_preview"
    bl_label = "U3M Render Preview"
    bl_description = "Render a Preview"


class LoadTextureOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "myops.u3m_load_texture"
    bl_label = "Load Texture"
    bl_description = "Open a file dialog to load a texture"

    pnode: bpy.props.StringProperty()

    def execute(self, context):
        image_path = self.filepath
        node_group, side, node_name = self.pnode.split("_&_", 2)
        editor.add_texture(context, node_group, side, node_name, image_path)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class RemoveTextureOperator(bpy.types.Operator):
    bl_idname = "myops.u3m_remove_texture"
    bl_label = "Remove Texture?"
    bl_description = "Remove the texture from the shader"

    pnode: bpy.props.StringProperty()

    def execute(self, context):
        node_group, side, node_name = self.pnode.split("_&_", 2)
        editor.remove_texture(context, node_group, side, node_name)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class ErrorMessageConfirmation(bpy.types.Operator):
    bl_idname = "wm.error_confirm"
    bl_label = "U3M Error:"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=context.scene.error_message)

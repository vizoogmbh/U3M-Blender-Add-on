import bpy
from bpy.props import FloatProperty

from .blender.blender_classes import (
    ImportU3M,
    ExportU3M,
    U3MEditPanel,
    U3MEditPanelFront,
    U3MEditPanelFrontAdvanced,
    U3MEditPanelBack,
    U3MEditPanelBackAdvanced,
    U3MToolsPanel,
    U3MViewsPanel,
    U3MScaleOperator,
    RenderPreview,
    ViewOperator,
    AddSideOperator,
    RemoveSideOperator,
    InitOperator,
    LoadTextureOperator,
    RemoveTextureOperator,
    ErrorMessageConfirmation
)


def set_scale(self, context):
    U3MScaleOperator.set(self, context, context.object, context.scene.u3m_scale_x,
                         context.scene.u3m_scale_y, context.scene.u3m_size)


bpy.types.Scene.u3m_scale_x = bpy.props.FloatProperty(
    update=set_scale, name="shader scale x", description="shader scale (x)", min=0.001, max=1000000.0, default=0.01)
bpy.types.Scene.u3m_scale_y = bpy.props.FloatProperty(
    update=set_scale, name="shader scale y", description="shader scale (y)", min=0.001, max=1000000.0, default=0.01)
bpy.types.Scene.u3m_size = bpy.props.FloatProperty(
    update=set_scale, name="Size (%)", description="material size (scaling factor) in percent", min=0.001, max=10000.0, default=100.00)


def menu_func_import(self, context):
    self.layout.operator(ImportU3M.bl_idname,
                         text="Unified 3D Material (.u3m)")


def menu_func_export(self, context):
    self.layout.operator(ExportU3M.bl_idname,
                         text="Unified 3D Material (.u3m)")


classes = (
    ImportU3M,
    ExportU3M,
    U3MEditPanel,
    U3MEditPanelFront,
    U3MEditPanelFrontAdvanced,
    U3MEditPanelBack,
    U3MEditPanelBackAdvanced,
    U3MToolsPanel,
    U3MViewsPanel,
    U3MScaleOperator,
    RenderPreview,
    ViewOperator,
    AddSideOperator,
    RemoveSideOperator,
    InitOperator,
    LoadTextureOperator,
    RemoveTextureOperator,
    ErrorMessageConfirmation
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in classes:
        bpy.utils.unregister_class(cls)

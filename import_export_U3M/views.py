from import_export_U3M.blender import utils as Blender


class InitOperatorBase(object):

    def execute(self, context):
        u3m_init()
        return {'FINISHED'}


class ViewOperatorBase(object):

    view_name = None

    def execute(self, context):
        set_view(self.view_name)
        return {'FINISHED'}


class RenderPreviewBase(object):

    def execute(self, context):
        render_preview()
        return {'FINISHED'}


def u3m_init():
    current_obj = Blender.get_current_object()
    # workaround for append scene bug (scene content being randomly dumped in active scene)
    temp_scene = Blender.new_temp_scene()
    Blender.append_item("Scene", "U3M")
    Blender.remove_scene(temp_scene)  # workaround step 2
    Blender.append_item("WorkSpace", "U3M")
    if "U3M" in Blender.get_workspaces():
        Blender.open_u3m_workspace()
    current_obj.select_set(True)


def set_view(view_name):
    active_mat = Blender.get_active_material()
    Blender.open_u3m_workspace()
    Blender.open_u3m_scene()
    scene = Blender.get_scene()
    Blender.set_collection_visible(scene, view_name)
    Blender.set_camera(scene, view_name)
    for obj in Blender.get_all_objects(view_name):
        if obj.type == "MESH":
            obj.select_set(True)
            Blender.set_active(obj)
            if active_mat:
                if Blender.is_u3m(active_mat) is True and Blender.is_u3m(obj.active_material) is True:
                    obj.active_material = active_mat
                    Blender.set_u3m_scale()
                    break
    Blender.set_area()


def render_preview():
    print("render preview")
    Blender.render()

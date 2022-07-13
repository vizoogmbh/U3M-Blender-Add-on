from . import class_register
bl_info = {
    "name": "Unified 3D Material (U3M) format",
    "author": "vizoo3d.com",
    "version": (1, 1, 1),
    "blender": (2, 93, 9),
    "location": "File > Import-Export",
    "description": "Import-Export U3M",
    "warning": "",
    "doc_url": "https://github.com/vizoogmbh/U3M-Blender-Add-on",
    "category": "Import-Export"}


def register():
    class_register.register()


def unregister():
    class_register.unregister()


if __name__ == "__main__":
    register()

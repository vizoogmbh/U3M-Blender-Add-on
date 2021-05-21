import sys
import os
import tempfile
import bpy


def read_png_data(png_filepath):
    with open(png_filepath, "rb") as png_data:
        content = png_data.read()
    return content


def create_new_icon_from_png(icon_dir_path, png_filepaths, icon_sizes):
    with open(os.path.join(icon_dir_path, "icon.ico"), "w+b") as icon_file:  # create new icon file
        icon_file = write_ico_header_and_image_entries(icon_file, icon_sizes)
        for filepath in png_filepaths:
            png_content = read_png_data(filepath)
            icon_file.write(png_content)


def write_ico_header_and_image_entries(icon_file, icon_sizes):
    # Header: ICONDIR #according to https://en.wikipedia.org/wiki/ICO_(file_format)
    # Offset#0: Reserved. Must always be 0.
    icon_file.write(int.to_bytes(0, length=2, byteorder='little'))
    # Offset#2: Specifies image type: 1 for icon (.ICO) image
    icon_file.write(int.to_bytes(1, length=2, byteorder='little'))
    # Offset#4: Specifies number of images in the file.
    icon_file.write(int.to_bytes(len(icon_sizes),
                    length=2, byteorder='little'))
    # Image entry: ICONDIRENTRY
    offset = None
    for image in range(len(icon_sizes)):
        if icon_sizes[image][0] != 256:
            # Offset#0 Specifies image width in pixels. Can be any number between 0 and 255.
            icon_file.write(int.to_bytes(
                icon_sizes[image][0], length=1, byteorder='little'))
            # Offset#1 Specifies image height in pixels. Can be any number between 0 and 255.
            icon_file.write(int.to_bytes(
                icon_sizes[image][0], length=1, byteorder='little'))
        elif icon_sizes[image][0] == 256:
            # Offset#0: Value 0 means image width is 256 pixels.
            icon_file.write(int.to_bytes(0, length=1, byteorder='little'))
            # Offset#1: Value 0 means image height is 256 pixels.
            icon_file.write(int.to_bytes(0, length=1, byteorder='little'))
        elif icon_sizes[image][0] > 256:
            raise Exception("maximum icon size is 256x256 px")
        # Offset#2: Specifies number of colors in the color palette. Should be 0 if the image does not use a color palette.
        icon_file.write(int.to_bytes(0, length=1, byteorder='little'))
        # Offset#3: Reserved. Should be 0.
        icon_file.write(int.to_bytes(0, length=1, byteorder='little'))
        # Specifies color planes. Should be 0 or 1
        icon_file.write(int.to_bytes(1, length=2, byteorder='little'))
        # Specifies bits per pixel
        icon_file.write(int.to_bytes(32, length=2, byteorder='little'))
        # Specifies the size of the image's data in bytes
        icon_file.write(int.to_bytes(
            icon_sizes[image][1], length=4, byteorder='little'))
        if image == 0:
            # first entrys offset: bytes of header+image entries before first img-data
            offset = (6+len(icon_sizes)*16)
        elif image > 0:
            # any following entries: add last image filesize
            offset += icon_sizes[image-1][1]
        # Specifies the offset PNG data from the beginning of the ICO/CUR file
        icon_file.write(int.to_bytes(offset, length=4, byteorder='little'))
    return icon_file


def main(argv):
    material_dir = os.path.join(argv[0])
    mat_basename = os.path.basename(material_dir)
    preview_scene_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "source", "preview_scene.blend")
    preview_img_path = os.path.join(material_dir, mat_basename+".png")
    bpy.ops.wm.open_mainfile(filepath=preview_scene_path)
    bpy.ops.preferences.addon_enable(module="import_export_U3M")
    bpy.ops.import_scene.u3m(filepath=os.path.join(
        material_dir, mat_basename + ".u3m"))
    bpy.context.scene.render.filepath = preview_img_path
    bpy.ops.render.render(write_still=True)
    preview_img = bpy.data.images.load(preview_img_path, check_existing=True)
    ico_path = os.path.dirname(preview_img_path)
    # mutable list before assigning size in bytes. size = (width/height in pixels, size in bytes)
    icon_sizes = [[256, None], [64, None], [32, None], [16, None]]
    with tempfile.TemporaryDirectory(prefix="tmp_u3m_icodata_") as tmpdirname:
        tmp_png_filepaths = []
        for size in icon_sizes:
            preview_img.scale(size[0], size[0])
            tmp_png_filepath = os.path.join(
                tmpdirname, mat_basename + "_" + str(size[0]) + ".png")
            preview_img.save_render(filepath=tmp_png_filepath)
            size[1] = os.path.getsize(tmp_png_filepath)
            size = tuple(size)  # immutable tuple
            tmp_png_filepaths.append(tmp_png_filepath)
        create_new_icon_from_png(ico_path, tmp_png_filepaths, icon_sizes)
    print("sucessfully created new preview & icon.")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])

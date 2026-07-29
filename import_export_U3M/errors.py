from .blender import utils as Blender


class U3MErrorHandler:
    MESSAGE_MAP = {
        "no_mesh": "U3M can only be applied to mesh objects.",
        "invalid_id": "Invalid material ID.",
        "no_texture": "Texture file could not be found.",
        "wrong_version": "Unsupported U3M version.",
        "loading_failed": "Failed to load U3M data.",
        "writing_failed": "Failed to write U3M data.",
        "invalid_mat_name": "Invalid material name.",
        "no_visualisation": "No visualisation entry was found.",
        "no_active_object": "No active object found.",
        "wrong_date_format": "Invalid date format.",
        "date_parsing_failed": "Failed to parse date.",
        "date_writing_failed": "Failed to write date.",
        "invalid_relative_path": "Invalid relative path.",
        "no_uv_map": "The active mesh has no UV map.",
        "no_polygons": "The active mesh has no matching polygons.",
        "uv_calc_failed": "Could not calculate UV dimensions.",
    }

    def handle(self, error_code):
        message = self.MESSAGE_MAP.get(error_code, str(error_code))
        Blender.display_error_confirmation(message)

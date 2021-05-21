from import_export_U3M.blender import utils as Blender

# exception classes


class U3MError(Exception):
    """Base class for other exceptions"""
    pass


class ActiveObjectError(U3MError):
    """Raise when Active Object is missing (Blender)"""
    pass


class MeshTypeError(U3MError):
    """Raise when active Object is not Type Mesh (Blender)"""
    pass


class LoadingError(U3MError):
    """Raise when U3M file can not be loaded"""
    pass


class WritingError(U3MError):
    """Raise when U3M file can not be written"""
    pass


class MissingTextureError(U3MError):
    """Raise when texture could not be found on the system"""
    pass


class MaterialNameError(U3MError):
    """Raise when material name is invalid"""
    pass


class UUID4Error(U3MError):
    """Raise when UUID4 is invalid"""
    pass


class VisualisationError(U3MError):
    """Raise when the U3M does not contain a visualisation entry (front,back)"""
    pass


class DateFormatError(U3MError):
    """Raise when the date format is invalid."""
    pass


class DateParsingError(U3MError):
    """Raise when the date format can not be parsed."""
    pass


class DateWritingError(U3MError):
    """Raise when the date can not be written."""
    pass


class RelativePathError(U3MError):
    """Raise when relative path is invalid."""
    pass


class VersionError(U3MError):
    """Raise when u3m version is invalid."""
    pass

# error handler class


class U3MErrorHandler:
    def __init__(self, error_handling_enum):
        self.error_handling_mode = error_handling_enum  # 'STRICT', 'RELAXED', 'USER'
        self.error_message = None

    def handle(self, error_message):
        self.error_message = error_message
        if self.error_handling_mode == 'STRICT':
            self.handle_strict()
        elif self.error_handling_mode == 'RELAXED':
            self.handle_relaxed()
        elif self.error_handling_mode == 'USER':
            self.handle_user()

    def handle_strict(self):
        if self.error_message == "no_mesh":
            raise MeshTypeError
        elif self.error_message == "invalid_id":
            raise UUID4Error
        elif self.error_message == "no_texture":
            raise MissingTextureError
        elif self.error_message == "wrong_version":
            raise VersionError
        elif self.error_message == "loading_failed":
            raise LoadingError
        elif self.error_message == "writing_failed":
            raise WritingError
        elif self.error_message == "invalid_mat_name":
            raise MaterialNameError
        elif self.error_message == "no_visualisation":
            raise VisualisationError
        elif self.error_message == "no_active_object":
            raise ActiveObjectError
        elif self.error_message == "wrong_date_format":
            raise DateFormatError
        elif self.error_message == "date_parsing_failed":
            raise DateParsingError
        elif self.error_message == "date_writing_failed":
            raise DateWritingError
        elif self.error_message == "invalid_relative_path":
            raise RelativePathError
        else:
            raise U3MError(self.error_message)

    def handle_relaxed(self):
        if self.error_message == "no_mesh":
            print("MeshTypeError: U3M can only be applied to objects of type mesh.")
        elif self.error_message == "invalid_id":
            print("UUID4Error: Invalid material ID.")
        elif self.error_message == "no_texture":
            print("MissingTextureError")
        elif self.error_message == "wrong_version":
            print("VersionError")
        elif self.error_message == "loading_failed":
            print("LoadingError")
        elif self.error_message == "writing_failed":
            print("WritingError")
        elif self.error_message == "invalid_mat_name":
            print("MaterialNameError")
        elif self.error_message == "no_visualisation":
            print("VisualisationError")
        elif self.error_message == "no_active_object":
            print("ActiveObjectError")
        elif self.error_message == "wrong_date_format":
            print("DateFormatError")
        elif self.error_message == "date_parsing_failed":
            print("DateParsingError")
        elif self.error_message == "date_writing_failed":
            print("DateWritingError")
        elif self.error_message == "invalid_relative_path":
            print("RelativePathError")
        else:
            print(self.error_message)

    def handle_user(self):
        Blender.display_error_confirmation(self.error_message)

    def get_error_message(self):
        return self.error_message

    def print_mode(self):
        print(self.error_handling_mode)

    def set_mode(self, mode):
        self.error_handling_mode = mode

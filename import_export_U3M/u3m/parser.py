import json
from .u3m_1_0 import u3m_1_0
from .u3m_1_1 import u3m_1_1


class U3MParser:
    def __init__(self):
        self.u3m_version = None

    def load_u3m_from_path(self, filepath, error_handler):
        json_string = open(filepath, 'r').read()
        return self.load_u3m_from_str(json_string, error_handler)

    def load_u3m_from_str(self, json_string, error_handler):
        u3m_dict = json.loads(json_string)
        self.u3m_version = str(u3m_dict.get("schema"))
        if self.u3m_version == "1.0":
            return u3m_1_0.U3M_1_0_from_dict(u3m_dict, error_handler)
        elif self.u3m_version == "1.1":
            return u3m_1_1.U3M_1_1_from_dict(u3m_dict, error_handler)
        else:
            error_handler.handle("wrong_version")
            return None

    def write_u3m(self, obj, filepath, error_handler):
        self.u3m_version = obj.get_schema()
        if self.u3m_version == "1.0":
            u3m_dict = u3m_1_0.U3M_1_0_to_dict(obj, error_handler)
        elif self.u3m_version == "1.1":
            u3m_dict = u3m_1_1.U3M_1_1_to_dict(obj, error_handler)
        else:
            error_handler.handle("wrong_version")
            u3m_dict = None
        if u3m_dict != None:
            with open(filepath, "w") as outfile:
                json.dump(u3m_dict, outfile, indent=4, sort_keys=True)
        else:
            error_handler.handle("writing_failed")

    def get_u3m_version(self):
        return self.u3m_version

    def convert_to_string(self, u3m_dict):
        return json.dumps(u3m_dict)

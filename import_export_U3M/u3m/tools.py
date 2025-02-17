import re
import datetime
from enum import Enum
from typing import Any, Dict, TypeVar, Type, cast, Callable, List

import re
import datetime

class DateParser:

    def parse(self, date_time_str, error_handler):
        try:
            if date_time_str is None:
                return None
            if self.check_str_for_zulu_offset(date_time_str):
                try:
                    return datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    return datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%SZ')
            else:
                try:
                    return datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    return datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            error_handler.handle("wrong_date_format")
            return None
        except Exception:
            error_handler.handle("date_parsing_failed")
            return None

    def write(self, date_time_obj, error_handler):
        zulu = self.check_for_zulu_offset(date_time_obj)
        try:
            if zulu:
                return date_time_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                return date_time_obj.strftime('%Y-%m-%dT%H:%M:%S%z')
        except Exception:
            error_handler.handle("date_writing_failed")
            return None

    def check_str_for_zulu_offset(self, date_time_str):
        pattern = r"^(?:[1-9]\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-][01]\d:[0-5]\d)$"
        return re.search(pattern, date_time_str)

    def check_for_zulu_offset(self, date_time_obj):
        try:
            return date_time_obj.utcoffset().total_seconds() == 0
        except Exception:
            return False


date_parser = DateParser()


class RelativeFilePath:
    def __init__(self, path_string, error_handler):
        self.pattern = '^\(\(?!(\\.\\.|\\.|\\~|(([cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[cC][lL][oO][cC][kK]\\$|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(\\.[^\\/]*)?))\\)([^\\x00-\\x1F<>:\"\\/\\\\|\\$\\%]{0,254}[^\\x00-\\x1F<>:\"\\/\\\\|\\$\\%\\.\\x20|]\\))*(?!(\\.\\.|\\.|\\~|(([cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[cC][lL][oO][cC][kK]\\$|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(\\..*)?))$)([^\\x00-\\x1F<>:\"\\/\\\\|]{0,254}[^\\x00-\\x1F<>:\"\\/\\\\\\.\\x20|]$)$'
        self.set_path(path_string, error_handler)

    def set_path(self, path_string, error_handler):
        if self.validate_path(path_string):
            self.path = path_string
        else:
            error_handler.handle("invalid_relative_path")
            self.path = None

    def validate_path(self, path_string):
        result = re.match(self.pattern, path_string)
        return result == None

    def get_path(self):
        return self.path


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def to_class_with_errors(c: Type[T], x: Any, error_handler: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict(error_handler)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_none_with_errors(x: Any, error_handler: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except AssertionError:
            pass


def from_union_with_errors(fs, x, error_handler):
    for f in fs:
        try:
            return f(x, error_handler)
        except AssertionError:
            pass


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any, error_handler: Any) -> datetime:
    return date_parser.parse(x, error_handler)


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return {k: f(v) for (k, v) in x.items()}

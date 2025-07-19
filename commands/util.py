from typing import Union


def parse_bool(value: Union[int, str, bool]) -> bool:
    if isinstance(value, int):
        return value == 1
    elif isinstance(value, str):
        lower_value = value.lower
        return lower_value == "true" or lower_value == "yes"
    elif isinstance(value, bool):
        return value
    return False


def parse_int(value: Union[int, str]) -> int:
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try: 
            return int(value)
        except:
            return -1
    return -1
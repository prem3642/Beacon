# -*- coding: utf-8 -*-


def ordered(obj):
    """
    Method to return sorted dicts, lists, and any combination of their nested structures. Converts all values to
    "Strings" to avoid TypeError while comparison.
    """
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return str(obj)

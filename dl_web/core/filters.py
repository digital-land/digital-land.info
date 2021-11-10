def generate_query_param_str(v, filter_name, current_str):
    query_str = str(current_str)
    if f"{filter_name}={v}" in query_str:
        s = query_str.replace(f"{filter_name}={v}", "")
        return "?" + s.strip("&")
    return "?" + query_str


def is_list(value):
    return isinstance(value, list)


def geometry_reference_count(v):
    if is_list(v):
        return len(v)
    return 1


def hex_to_rgb_string(hex):
    h = hex.lstrip("#")
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"

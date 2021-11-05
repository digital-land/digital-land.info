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

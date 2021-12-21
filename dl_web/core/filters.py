from digital_land_frontend.filters import is_list_filter


def generate_query_param_str(v, filter_name, current_str):
    query_str = str(current_str)
    if f"{filter_name}={v}" in query_str:
        s = query_str.replace(f"{filter_name}={v}", "")
        return "?" + s.strip("&")
    return "?" + query_str


def geometry_reference_count(v):
    if is_list_filter(v):
        return len(v)
    return 1


def make_param_str_filter(exclude_value, exclude_param, all):
    return "&".join(
        [
            "{}={}".format(param[0], param[1])
            for param in all
            if exclude_param != param[0] or exclude_value != param[1]
        ]
    )


def render_markdown(text):
    import markdown
    import markupsafe
    from dl_web.core.markdown_extensions import GovUKStylesExtension

    # register extensions here as well if needed
    html = markdown.markdown(
        text, output_format="html5", extensions=[GovUKStylesExtension()]
    )
    return markupsafe.Markup(html)

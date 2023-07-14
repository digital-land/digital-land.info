import jinja2

from fastapi.templating import Jinja2Templates

import random

from application.core.filters import (
    generate_query_param_str,
    geometry_reference_count,
    make_param_str_filter,
    render_markdown,
    entity_name_filter,
    get_entity_name_filter,
    debug,
    digital_land_to_json,
    uri_encode,
    cacheBust,
    make_url_param_str,
    to_slug,
    extract_component_key,
    is_list_filter,
    hex_to_rgb_string_filter,
    make_link_filter,
    commanum_filter,
)

from application.core.utils import model_dumps


def random_int(n=1):
    return "".join([str(random.randint(0, 9)) for i in range(n)])


templates = Jinja2Templates("application/templates")

templates.env.loader = jinja2.ChoiceLoader(
    [
        jinja2.FileSystemLoader(searchpath=["application/templates"]),
        jinja2.PrefixLoader(
            {
                "govuk_frontend_jinja": jinja2.PackageLoader("govuk_frontend_jinja"),
            }
        ),
    ]
)

# Used to customize jinja tojson filter
templates.env.policies["json.dumps_function"] = model_dumps

templates.env.globals["assetPath"] = "/static"
templates.env.globals["enable_x_ref"] = True
templates.env.globals["includeAutocomplete"] = True
templates.env.globals["random_int"] = random_int
templates.env.globals["templateVar"] = {"email": "digitalland@levellingup.gov.uk"}
templates.env.globals["serviceStatus"] = False

templates.env.filters["is_list"] = is_list_filter
templates.env.filters["commanum"] = commanum_filter
templates.env.filters["make_link"] = make_link_filter
templates.env.filters["geometry_reference_count"] = geometry_reference_count
templates.env.filters["make_query_str"] = generate_query_param_str
templates.env.filters["hex_to_rgb"] = hex_to_rgb_string_filter
templates.env.filters["make_param_str"] = make_param_str_filter
templates.env.filters["render_markdown"] = render_markdown
templates.env.filters["entity_name"] = entity_name_filter
templates.env.filters["get_entity_name"] = get_entity_name_filter
templates.env.filters["debug"] = debug
templates.env.filters["digital_land_to_json"] = digital_land_to_json
templates.env.filters["uri_encode"] = uri_encode
templates.env.globals["cacheBust"] = cacheBust
templates.env.filters["make_url_param_str"] = make_url_param_str
templates.env.filters["slugify"] = to_slug
templates.env.filters["extract_component_key"] = extract_component_key

templates.env.add_extension("jinja2.ext.do")

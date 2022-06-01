import jinja2

from fastapi.templating import Jinja2Templates

from digital_land_frontend.filters import (
    is_list_filter,
    hex_to_rgb_string_filter,
    make_link_filter,
    commanum_filter,
)
from digital_land_frontend.globals import random_int

from application.core.filters import (
    generate_query_param_str,
    geometry_reference_count,
    make_param_str_filter,
    render_markdown,
    entity_name_filter,
    get_entity_name_filter,
    debug,
)

from application.core.utils import model_dumps

templates = Jinja2Templates("application/templates")

templates.env.loader = jinja2.ChoiceLoader(
    [
        jinja2.FileSystemLoader(searchpath=["application/templates"]),
        jinja2.PrefixLoader(
            {
                "govuk_frontend_jinja": jinja2.PackageLoader("govuk_frontend_jinja"),
                "digital-land-frontend": jinja2.PackageLoader("digital_land_frontend"),
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

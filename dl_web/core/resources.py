import jinja2

from fastapi.templating import Jinja2Templates

from digital_land.specification import Specification
from digital_land_frontend.filters import (
    register_basic_filters,
    register_mapper_filters,
)

from dl_web.core.filters import (
    generate_query_param_str,
    is_list,
    geometry_reference_count,
    hex_to_rgb_string,
)

from dl_web.core.utils import model_dumps

specification = Specification("specification/")

templates = Jinja2Templates("dl_web/templates")

templates.env.loader = jinja2.ChoiceLoader(
    [
        jinja2.FileSystemLoader(searchpath=["dl_web/templates"]),
        jinja2.PrefixLoader(
            {
                "govuk-jinja-components": jinja2.PackageLoader(
                    "govuk_jinja_components"
                ),
                "digital-land-frontend": jinja2.PackageLoader("digital_land_frontend"),
            }
        ),
    ]
)

# Used to customize jinja tojson filter
templates.env.policies["json.dumps_function"] = model_dumps

templates.env.globals["staticPath"] = "/static"
templates.env.globals["ASSET_PATH"] = "/static"
templates.env.globals["enable_x_ref"] = True
templates.env.globals["includeAutocomplete"] = True

templates.env.filters["is_list"] = is_list
templates.env.filters["geometry_reference_count"] = geometry_reference_count
templates.env.filters["make_query_str"] = generate_query_param_str
templates.env.filters["hex_to_rgb"] = hex_to_rgb_string

register_basic_filters(templates.env, specification)
register_mapper_filters(templates.env, specification)

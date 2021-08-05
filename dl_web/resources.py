import jinja2
from digital_land_frontend.filters import (
    register_basic_filters,
    register_mapper_filters,
)
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("dl_web/templates")

# app.jinja_loader = jinja2.ChoiceLoader(
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

templates.env.globals["staticPath"] = "https://digital-land.github.io"

register_basic_filters(templates.env)
register_mapper_filters(templates.env, None)  # TODO provide view_model?

import jinja2
from digital_land.specification import Specification
from digital_land.view_model import ViewModelJsonQuery
from digital_land_frontend.filters import (
    register_basic_filters,
    register_mapper_filters,
)
from fastapi.templating import Jinja2Templates


def get_view_model():
    return ViewModelJsonQuery(url_base="http://datasetteawsentityv2-env.eba-gbrdriub.eu-west-2.elasticbeanstalk.com/view_model/")


specification = Specification("specification/")

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

# templates.env.globals["staticPath"] = "https://digital-land.github.io"
templates.env.globals["staticPath"] = "/static"
templates.env.globals["ASSET_PATH"] = "/static"
templates.env.globals["enable_x_ref"] = False # disabled for now

register_basic_filters(templates.env, specification)
register_mapper_filters(templates.env, get_view_model(), specification)

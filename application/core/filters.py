from digital_land_frontend.filters import is_list_filter

from application.data_access.entity_queries import get_entity_query
from jinja2 import pass_eval_context
from markdown import markdown
from markupsafe import Markup
import json
import jsonpickle
from bs4 import BeautifulSoup
from slugify import slugify


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


def render_markdown(text, govAttributes=False):
    soup = BeautifulSoup(markdown(text, output_format="html"), "html.parser")
    if govAttributes:
        _add_html_attrs(soup)
    return Markup(soup.prettify())


def _add_html_attrs(soup):
    for tag in soup.select("p"):
        tag["class"] = "govuk-body"
    for tag in soup.select("h1, h2, h3, h4, h5"):
        tag["id"] = slugify(tag.getText())
    for tag in soup.select("h1"):
        tag["class"] = "govuk-heading-xl"
    for tag in soup.select("h2"):
        tag["class"] = "govuk-heading-l"
    for tag in soup.select("h3"):
        tag["class"] = "govuk-heading-m"
    for tag in soup.select("h4"):
        tag["class"] = "govuk-heading-s"
    for tag in soup.select("ul"):
        tag["class"] = "govuk-list govuk-list--bullet"
    for tag in soup.select("a"):
        tag["class"] = "govuk-link"
    for tag in soup.select("ol"):
        tag["class"] = "govuk-list govuk-list--number"
    for tag in soup.select("hr"):
        tag["class"] = "govuk-section-break govuk-section-break--l"
    for tag in soup.select("code"):
        tag["class"] = "app-code"


def debug(thing):
    dumpee = json.dumps(json.loads(jsonpickle.encode(thing)), indent=2)
    return f"<script>console.log({dumpee});</script>"


@pass_eval_context
def entity_name_filter(eval_ctx, id):
    entity, _, _ = get_entity_query(id)
    if entity:
        anchor = f'<a class="govuk-link" href="/entity/{id}">{id}</a>'
        name = f'<span class="govuk-!-margin-left-1 dl-data-reference">({entity.name})</span>'
        if eval_ctx.autoescape:
            return Markup(anchor + name)
    return id


@pass_eval_context
def get_entity_name_filter(eval_ctx, id):
    entity, _, _ = get_entity_query(id)
    if entity:
        if eval_ctx.autoescape:
            return entity.name
    return id

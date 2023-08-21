from application.data_access.entity_queries import get_entity_query
from application.data_access.digital_land_queries import get_dataset_query
from application.core.utils import NoneToEmptyStringEncoder
from jinja2 import pass_eval_context
from markdown import markdown
from markupsafe import Markup
import json
import jsonpickle
from bs4 import BeautifulSoup
from slugify import slugify
from uritemplate import URITemplate
import urllib.parse as urlparse
from urllib.parse import urlencode
import os
import hashlib
import validators
import numbers


def to_slug(string):
    return slugify(string)


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


def _remove_value_from_list(list_input, values):
    """specific function that returns a new list with values removed,
    allows input of lists and elements"""
    if isinstance(values, list):
        output_list = [val for val in list_input if val not in values]
    else:
        output_list = [val for val in list_input if val != values]
    return output_list


def remove_values_from_param_dict(param_dict, exclude_values):
    # create new dict so that values aren't changed in the original
    new_dict = dict(param_dict)
    for key in exclude_values.keys():
        if new_dict[key]:
            if isinstance(new_dict[key], list):
                new_dict[key] = _remove_value_from_list(
                    new_dict[key], exclude_values[key]
                )
            else:
                if isinstance(exclude_values[key], list):
                    if new_dict[key] in exclude_values[key]:
                        new_dict = remove_param_from_param_dict(new_dict, key)
                else:
                    if new_dict[key] == exclude_values[key]:
                        new_dict = remove_param_from_param_dict(new_dict, key)
    return new_dict


def remove_param_from_param_dict(param_dict, exclude_params):
    if isinstance(exclude_params, list):
        output_dict = {k: v for k, v in param_dict.items() if k not in exclude_params}
    else:
        output_dict = {k: v for k, v in param_dict.items() if k != exclude_params}

    return output_dict


def make_url_param_str(param_dict, exclude_values=None, exclude_params=None):
    """
    A new function to make a parameter string from a dictionary of parameters. Uses url encode
    rather than us formatting a string. We specifically don't want to alter the original dict
    """
    output_dict = dict(param_dict)

    if exclude_values:
        output_dict = remove_values_from_param_dict(output_dict, exclude_values)

    if exclude_params:
        output_dict = remove_param_from_param_dict(output_dict, exclude_params)

    return urlencode(output_dict, doseq=True)


def render_markdown(text, govAttributes=False, makeSafe=True):
    if text is None:
        return ""
    soup = BeautifulSoup(markdown(text), "html.parser")
    if govAttributes:
        _add_html_attrs(soup)
    if makeSafe:
        return Markup(soup)
    else:
        return soup


def _add_html_attrs(soup):
    for tag in soup.select("p"):
        tag["class"] = "govuk-body"
    for tag in soup.select("h1, h2, h3, h4, h5"):
        # sets the id to a 'slugified' version of the text content
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
        if entity.name:
            name = f'<span class="govuk-!-margin-left-1 dl-data-reference">({entity.name})</span>'
        else:
            name = f'<span class="govuk-!-margin-left-1 dl-data-reference">({entity.reference})</span>'

        if eval_ctx.autoescape:
            return Markup(anchor + name)
    return id


@pass_eval_context
def get_entity_name_filter(eval_ctx, id):
    entity, _, _ = get_entity_query(id)
    if entity:
        if eval_ctx.autoescape:
            if entity.name:
                return entity.name
            else:
                return entity.reference
    return id


def get_entity_name(entity):
    if entity.name:
        return entity.name
    else:
        return entity.reference


def digital_land_to_json(dict):
    return json.dumps(dict, default=str, indent=4, cls=NoneToEmptyStringEncoder)


def uri_encode(uri_template, kwarg_list):
    uri = URITemplate(uri_template)
    return uri.expand(**kwarg_list)


# Takes a URI and appends a specified parameter to it
def appendUriParam(uri, param):
    uri_parts = list(urlparse.urlparse(uri))
    query = dict(urlparse.parse_qsl(uri_parts[4]))
    query.update(param)
    uri_parts[4] = urlencode(query)
    return urlparse.urlunparse(uri_parts)


def hash_file(filename):
    # open file for reading in binary mode
    try:
        with open(os.path.dirname(__file__) + "/../../" + filename, "rb") as openedFile:
            content = openedFile.read()
    except FileNotFoundError:
        print("File not found when creating a hash: " + filename)
        return ""

    sha1Hash = hashlib.sha1(content)
    sha1Hashed = sha1Hash.hexdigest()

    # return the hex representation of digest
    return sha1Hashed


# Takes the URI and appends a param containing the current git hash
def cacheBust(uri):
    filename = uri.split("?")[0]
    sha = hash_file(filename)
    return appendUriParam(uri, {"v": sha})


def extract_component_key(json_ref):
    return json_ref.split("/")[-1]


# adding these filters from digital-land-frontend


def is_list_filter(v):
    """
    Check if variable is list
    """
    return isinstance(v, list)


def hex_to_rgb_string_filter(hex):
    """
    Given hex will return rgb string

    E.g. #0b0c0c ==> "11, 12, 12"
    """
    h = hex.lstrip("#")
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"


@pass_eval_context
def make_link_filter(eval_ctx, url, **kwargs):
    """
    Converts a url string into an anchor element.

    Requires autoescaping option to be set to True
    """
    css_classes = "govuk-link"
    if "css_classes" in kwargs:
        css_classes = kwargs.get("css_classes")

    if url is not None:
        if validators.url(str(url)):
            anchor = f'<a class="{css_classes}" href="{url}">{url}</a>'
            if eval_ctx.autoescape:
                return Markup(anchor)
    return url


def get_entity_geometry(entity):
    return {
        "name": get_entity_name(entity),
        "data": entity.geojson.geometry,
        "entity": entity.entity,
    }


def get_entity_paint_options(entity):
    dataset = get_dataset_query(entity.dataset)
    if dataset:
        return dataset.paint_options
    return None


def commanum_filter(v):
    """
    Makes large numbers readable by adding commas

    E.g. 1000000 -> 1,000,000
    """
    if isinstance(v, numbers.Number):
        return "{:,}".format(v)
    return v

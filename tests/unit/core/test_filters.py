from datetime import datetime
from dateutil.relativedelta import relativedelta

import pytest

from application.core.filters import (
    _remove_value_from_list,
    remove_param_from_param_dict,
    remove_values_from_param_dict,
    make_url_param_str,
    make_param_str_filter,
    cacheBust,
    append_uri_param,
    hash_file,
    is_past_date,
    is_safe_url,
    hex_to_rgb_string_filter,
    safe_css_colour_filter,
    safe_opacity_filter,
)


def test__remove_value_from_list_element_to_exclude():
    input_list = ["value_1", "value_2"]
    exclude_value = "value_2"
    expected = ["value_1"]

    result = _remove_value_from_list(input_list, exclude_value)
    assert result == expected


def test__remove_value_from_list_list_to_exclude():
    input_list = ["value_1", "value_2", "value_3"]
    exclude_value_list = ["value_1", "value_3"]
    expected = ["value_2"]

    result = _remove_value_from_list(input_list, exclude_value_list)
    assert result == expected


def test_remove_param_from_param_dict_element_param():
    input_param_dict = {"field": ["point", "typology"], "dataset": "ancient-woodland"}
    exclude_param = "field"
    expected = {"dataset": "ancient-woodland"}
    result = remove_param_from_param_dict(input_param_dict, exclude_param)
    assert result == expected


def test_remove_param_from_param_dict_list_of_param():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    exclude_param = ["field", "test"]
    expected = {"dataset": "ancient-woodland"}
    result = remove_param_from_param_dict(input_param_dict, exclude_param)
    assert result == expected


def test_remove_values_from_param_dict_elements_provided():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    exclude_values = {"field": "point"}
    expected = {
        "field": ["typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    result = remove_values_from_param_dict(input_param_dict, exclude_values)
    assert result == expected


def test_remove_values_from_param_dict_lists_provided():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_1", "test_value_2", "test_value_3"],
    }
    exclude_values = {"field": ["point"], "test": ["test_value_1", "test_value_2"]}
    expected = {
        "field": ["typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_3"],
    }
    result = remove_values_from_param_dict(input_param_dict, exclude_values)
    assert result == expected


def test_cacheBust_no_params():
    input_uri = "static/javascripts/MapController.js"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert input_uri == sections[0]

    hash = sections[1].split("=")[1]
    assert len(hash) == 40


def test_cacheBust_params():
    input_uri = "static/javascripts/MapController.js?fakeParam=myFakeParam"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert "static/javascripts/MapController.js" == sections[0]

    params = sections[1].split("&")
    assert params[0] == "fakeParam=myFakeParam"

    hash = params[1].split("=")[1]
    assert len(hash) == 40


def test_append_uri_param():
    uri = "static/javascript/myCookScript.js"
    param = {"key": "value"}
    result = append_uri_param(uri, param)
    assert result == "static/javascript/myCookScript.js?key=value"

    uri = "static/javascript/myCookScript.js?key=value"
    param = {"differentKey": "differentValue"}
    result = append_uri_param(uri, param)
    assert (
        result
        == "static/javascript/myCookScript.js?key=value&differentKey=differentValue"
    )


def test_hash_file():
    result = hash_file("static/javascripts/MapController.js")
    print(result)
    assert len(result) == 40


def test_make_url_param_str_all_arguements():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_1", "test_value_2", "test_value_3"],
    }
    exclude_params = "dataset"
    exclude_values = {"field": "point"}
    expected = "field=typology&test=test_value_1&test=test_value_2&test=test_value_3"
    result = make_url_param_str(input_param_dict, exclude_values, exclude_params)
    assert result == expected


def test_make_param_str_filter_url_encoding():
    """Tests that special characters are properly URL encoded."""
    params = [
        ("dataset", "planning-application"),
        ("entity", "123;456"),
        ("field", "test&value"),
    ]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)

    assert "dataset=planning-application" in result
    assert "entity=123%3B456" in result  # ; becomes %3B
    assert "field=test%26value" in result  # & becomes %26


def test_make_param_str_filter_with_empty_params():
    """Tests passing empty parameter list to `make_param_str_filter` returns empty string."""
    params = []
    exclude_value = "test"
    exclude_param = "test"

    result = make_param_str_filter(exclude_value, exclude_param, params)
    assert result == ""


def test_make_param_str_filter_no_exclusions():
    """Tests no parameters match the exclusion criteria."""
    params = [("dataset", "test"), ("entity", "123")]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)
    assert "dataset=test" in result
    assert "entity=123" in result


def test_make_param_str_filter_prevents_malformed_urls():
    """Tests that make_param_str_filter prevents creation of malformed URLs like &amp;entity=."""
    params = [("dataset", "planning"), ("entity", "115;00041"), ("field", "entry-date")]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)

    assert "115%3B00041" in result  # Semicolon is enconded
    assert ";" not in result  # Raw semicoln does not leak through
    assert "amp;" not in result  # No amp; prefixes
    assert "&amp;" not in result  # No HTML-encoded ampersands
    assert (
        "%3B" not in result or ";" not in result
    )  # Either encoded or unencoded, not mixed

    expected_parts = ["dataset=planning", "entity=115%3B00041", "field=entry-date"]
    for part in expected_parts:
        assert part in result


def test_is_past_date():
    """
    Tests `is_past_date()` only returns True when a date object passed
    as an argument is in the past.
    """
    today = datetime.today()

    # Assert with a end-date in the future
    end_date_two_years_in_future = (today + relativedelta(years=2)).date()
    result = is_past_date(end_date_two_years_in_future)
    assert result is False

    # Assert with today's date
    end_date_is_today = today.date()
    result = is_past_date(end_date_is_today)
    assert result is False

    # Assert with a end-date in the past
    end_date_three_years_in_past = (today - relativedelta(years=3)).date()
    result = is_past_date(end_date_three_years_in_past)
    assert result is True


def test_render_markdown_strips_script_and_handlers():
    """Regression: render_markdown must sanitise embedded HTML/script."""
    from application.core.filters import render_markdown

    out = str(
        render_markdown("ok <script>alert(1)</script> <img src=x onerror=alert(1)>")
    )
    assert "<script>" not in out
    assert "onerror" not in out
    assert "alert(1)" not in out or "<script>" not in out


def test_render_markdown_keeps_safe_formatting():
    from application.core.filters import render_markdown

    out = str(render_markdown("**bold** and [a link](https://example.com)"))
    assert "<strong>bold</strong>" in out
    assert 'href="https://example.com"' in out


@pytest.mark.parametrize(
    "value",
    [
        "http://example.com",
        "https://example.com/path?q=1",
        "HTTPS://EXAMPLE.COM",
        "  https://example.com  ",
    ],
)
def test_is_safe_url_accepts_http_and_https(value):
    assert is_safe_url(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        " javascript:alert(1)",
        "java\tscript:alert(1)",
        "java\nscript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:msgbox(1)",
        "//evil.example.com",
        "/relative/path",
        "example.com",
        "https://",
        "",
        None,
        123,
    ],
)
def test_is_safe_url_rejects_everything_else(value):
    assert is_safe_url(value) is False


def _render_entity_value(field, value, field_spec=None):
    from application.core.templates import templates

    template = templates.env.from_string(
        '{% from "components/entity-value/macro.jinja" import entityValue %}'
        "{{ entityValue(field, value, field_spec, [], None, {}, None) }}"
    )
    return template.render(field=field, value=value, field_spec=field_spec)


@pytest.mark.parametrize(
    "field,value,field_spec",
    [
        ("website", "javascript:alert(1)", None),
        ("documentation-url", "javascript:alert(1)", None),
        ("thing-uri", "javascript:alert(1)", None),
        ("evidence-urls", "javascript:alert(1)", None),
        (
            "homepage",
            "javascript:alert(1)",
            {"homepage": {"typology": "value", "datatype": "url"}},
        ),
    ],
)
def test_entity_value_does_not_link_unsafe_urls(field, value, field_spec):
    html = _render_entity_value(field, value, field_spec)
    assert 'href="javascript:' not in html
    assert "javascript:alert(1)" in html


@pytest.mark.parametrize(
    "field,field_spec",
    [
        ("website", None),
        ("evidence-urls", None),
        ("homepage", {"homepage": {"typology": "value", "datatype": "url"}}),
    ],
)
def test_entity_value_still_links_safe_urls(field, field_spec):
    html = _render_entity_value(field, "https://example.com/ok", field_spec)
    assert 'href="https://example.com/ok"' in html


def test_entity_value_urls_list_links_only_safe_items():
    html = _render_entity_value(
        "evidence-urls", "javascript:alert(1); https://example.com/ok"
    )
    assert 'href="https://example.com/ok"' in html
    assert 'href="javascript:' not in html
    assert "javascript:alert(1)" in html


def test_get_entity_geometry_logs_cleanly_when_entity_has_no_geometry(caplog):
    """A geography entity without geometry must log a warning, not raise a
    logging format error (pytest's log capture raises on those)."""
    from application.core.filters import get_entity_geometry
    from application.core.models import EntityModel

    entity = EntityModel(
        entity=900903,
        name="No geometry",
        dataset="greenspace",
        typology="geography",
        reference="NO-GEOM",
        prefix="greenspace",
        entry_date="2022-01-01",
    )

    with caplog.at_level("WARNING"):
        result = get_entity_geometry(entity)

    assert result["data"] is None
    assert result["entity"] == 900903
    assert "No geojson for entity that has a typology of geography: 900903" in (
        caplog.text
    )


@pytest.mark.parametrize(
    "value",
    ["#AABBCC", "#abc", "#AABBCCDD", "#abcd", "red", "DarkBlue"],
)
def test_safe_css_colour_accepts_hex_and_named_colours(value):
    assert safe_css_colour_filter(value) == value


@pytest.mark.parametrize(
    "value",
    [
        'red;" onmouseover="alert(1)',
        "red; background: url(https://evil.example)",
        "javascript:alert(1)",
        "#003078; background-image: url(https://evil.example)",
        None,
        123,
    ],
)
def test_safe_css_colour_rejects_unsafe_values(value):
    """Regression: paint_options.colour comes from dataset data and gets
    written into a style attribute - anything that isn't a plain hex/named
    colour must fall back rather than being passed through."""
    assert safe_css_colour_filter(value, fallback="#003078") == "#003078"


@pytest.mark.parametrize("value,expected", [(0.5, 0.5), ("0.5", 0.5), (0, 0), (1, 1)])
def test_safe_opacity_accepts_valid_numbers(value, expected):
    assert safe_opacity_filter(value) == expected


def test_safe_opacity_clamps_out_of_range_values():
    assert safe_opacity_filter(2) == 1
    assert safe_opacity_filter(-1) == 0


@pytest.mark.parametrize("value", ['0.5;" onclick="alert(1)', "x", None, ""])
def test_safe_opacity_rejects_unsafe_or_invalid_values(value):
    assert safe_opacity_filter(value, fallback=0.6) == 0.6


def test_hex_to_rgb_converts_valid_hex():
    assert hex_to_rgb_string_filter("#0b0c0c") == "11,12,12"


def test_hex_to_rgb_converts_shorthand_hex():
    """Regression: safe_css_colour allows 3/4-digit shorthand hex (#rgb,
    #rgba) through as safe, so hex_to_rgb must expand it rather than
    falling back to the default colour."""
    assert hex_to_rgb_string_filter("#0bc") == "0,187,204"
    assert hex_to_rgb_string_filter("#0bcf") == "0,187,204"


def test_hex_to_rgb_falls_back_rather_than_raising_on_non_hex():
    """Regression: safe_css_colour allows a plain colour name (e.g. "red")
    through as safe, but hex_to_rgb can only parse hex - it must fall back
    cleanly rather than raising when fed one, since the two are chained
    together wherever a colour is rendered."""
    assert hex_to_rgb_string_filter("red", fallback="0,48,120") == "0,48,120"


def test_safe_css_colour_and_safe_opacity_defaults_match_the_map_fill_defaults():
    """Guards against the colour/opacity defaults drifting out of sync with
    the map's own fill defaults (assets/javascripts/defaultPaintOptions.js)."""
    import re

    js_source = open("assets/javascripts/defaultPaintOptions.js").read()
    js_colour = re.search(r"'fill-color':\s*'([^']+)'", js_source).group(1)
    js_opacity = float(re.search(r"'fill-opacity':\s*([0-9.]+)", js_source).group(1))

    assert safe_css_colour_filter(None) == js_colour
    assert safe_opacity_filter(None) == js_opacity


def test_layer_control_item_escapes_name_and_rejects_unsafe_paint_options():
    """paint_options/name come from dataset data and are written into
    data-style-options/HTML, so they aren't trusted as CSS/markup."""
    from application.core.templates import templates

    env = templates.env
    layer_control_item = env.get_template(
        "components/map/macro.jinja"
    ).module.layerControlItem

    unsafe_layer = {
        "dataset": "greenspace",
        "name": "<img src=x onerror=alert(1)>",
        "paint_options": {
            "type": "fill",
            "colour": "red; background: url(https://evil.example)",
            "opacity": '0.5;" onclick="alert(1)',
        },
        "checked": False,
    }

    item_html = str(layer_control_item(unsafe_layer))
    assert "<img" not in item_html
    # Escaped to inert text, not a live tag/attribute - the substring
    # "onerror" legitimately appears here, harmlessly, as part of that text.
    assert "&lt;img src=x onerror=alert(1)&gt;" in item_html
    assert "evil.example" not in item_html


def test_layer_key_symbol_escapes_name_and_rejects_unsafe_paint_options():
    from application.core.templates import templates

    env = templates.env
    layer_key_symbol = env.get_template(
        "components/map/macro.jinja"
    ).module.layerKeySymbol

    unsafe_layer = {
        "dataset": "greenspace",
        "name": "<img src=x onerror=alert(1)>",
        "paint_options": {
            "type": "fill",
            "colour": "red; background: url(https://evil.example)",
            "opacity": '0.5;" onclick="alert(1)',
        },
        "checked": False,
    }

    symbol_html = str(layer_key_symbol(unsafe_layer))
    assert "evil.example" not in symbol_html
    assert "onclick" not in symbol_html
    assert "border-color: #003078;" in symbol_html


def test_layer_key_symbol_point_type_rejects_unsafe_colour():
    from application.core.templates import templates

    env = templates.env
    layer_key_symbol = env.get_template(
        "components/map/macro.jinja"
    ).module.layerKeySymbol

    unsafe_layer = {
        "dataset": "greenspace",
        "name": "Greenspace",
        "paint_options": {
            "type": "point",
            "colour": "red; background: url(https://evil.example)",
        },
    }

    symbol_html = str(layer_key_symbol(unsafe_layer))
    assert "evil.example" not in symbol_html
    assert "fill: #003078;" in symbol_html


def test_layer_control_item_renders_when_paint_options_omits_opacity():
    """Regression: a dataset's paint_options commonly has no explicit
    opacity/colour key at all - Jinja gives an Undefined sentinel for that,
    not None, which float(Undefined) used to raise on (500 on every /map/
    load, since layerControlItem renders unconditionally for every layer)."""
    from application.core.templates import templates

    env = templates.env
    layer_control_item = env.get_template(
        "components/map/macro.jinja"
    ).module.layerControlItem

    layer_without_opacity = {
        "dataset": "greenspace",
        "name": "Greenspace",
        "paint_options": {"type": "fill"},
        "checked": False,
    }

    html = str(layer_control_item(layer_without_opacity))
    assert 'data-style-options="#003078,0.6"' in html

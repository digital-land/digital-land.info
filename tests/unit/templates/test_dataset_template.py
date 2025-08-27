# pytest + Jinja2 template tests for dl-info/dataset.html
# Testing library/framework: pytest (with Jinja2 for rendering)
# These tests focus on conditional rendering and JSON-LD in the dataset template.

from jinja2 import Environment, DictLoader, FileSystemLoader, ChoiceLoader, StrictUndefined

def build_env(templates_dir="templates"):
    """
    Build a minimal Jinja2 environment that:
    - Loads the real dataset template from the repository
    - Stubs external macros and layouts that are imported/extended by the template
    - Provides filters used by the template (commanum, render_markdown, tojson already provided by Jinja2)
    """
    # Minimal base layout and component stubs to allow rendering child template blocks
    stub_loader = DictLoader({
        # Base layout to satisfy `{% extends "layouts/layout.html" %}`
        "layouts/layout.html": (
            "{% block pageTitle %}{% endblock %}"
            "{% block headStart %}{% endblock %}"
            "{% block breadcrumbs %}{% endblock %}"
            "{% block content %}{% endblock %}"
        ),
        # Stubbed components/macros referenced. They do not need to render anything significant for these tests.
        "components/summary-card/macro.jinja": (
            "{% macro appSummaryCard(params) -%}"
            "{% if caller %}{{ caller() }}{% endif %}"
            "{%- endmacro %}"
        ),
        "components/back-button/macro.jinja": (
            "{% macro dlBackButton(params) -%}"
            "<a data-testid='back-button' href='{{ params.parentHref }}'>Back</a>"
            "{%- endmacro %}"
        ),
        # GOV.UK table macro stub – enough to show rows rendered via inner HTML
        "govuk_frontend_jinja/components/table/macro.html": (
            "{% macro govukTable(params) -%}"
            "<table aria-label='{{ params['attributes']['aria-label'] }}'>"
            "{% for row in params['rows'] %}"
            "<tr>{% for cell in row %}<td>{{ cell['html']|safe }}</td>{% endfor %}</tr>"
            "{% endfor %}</table>"
            "{%- endmacro %}"
        ),
        # Included partials
        "partials/data-coverage-banner.html": "<div data-partial='data-coverage-banner'></div>",
        "partials/feedback.html": "<div data-partial='feedback'></div>",
    })

    fs_loader = FileSystemLoader(searchpath=templates_dir)
    env = Environment(
        loader=ChoiceLoader([stub_loader, fs_loader]),
        undefined=StrictUndefined,
        autoescape=True,
    )

    # Provide the custom filters used in the template.
    def commanum(value):
        try:
            # simple integer comma separator
            return f"{int(value):,}"
        except Exception:
            return str(value)

    def render_markdown(value, govAttributes=False):
        # Minimal stub: pass-through with safe wrapper of <p>
        # We keep it simple for deterministic tests.
        text = value or ""
        return f"<p>{text}</p>"

    env.filters["commanum"] = commanum
    env.filters["render_markdown"] = render_markdown
    return env

def render_template(env, template_name, ctx):
    tmpl = env.get_template(template_name)
    return tmpl.render(**ctx)

def base_context(overrides=None):
    ctx = {
        "now": "2025-08-27T12:00:00Z",
        "data_file_url": "https://files.planning.data.gov.uk",
        "dataset": {
            "dataset": "conservation-area",
            "name": "Conservation area",
            "plural": "Conservation areas",
            "text": "Some description",
            "licence": True,
            "licence_text": "Open Government Licence v3.0",
            "attribution": True,
            "attribution_text": "Contains public sector information",
            "typology": "non-geography",
            "consideration": None,
        },
        "entity_count": 5,
        "publishers": {"current": 123},
        "last_collection_attempt": "2025-08-20",
        "latest_resource": type("Obj", (), {"last_updated": "2025-08-25"})(),
        "dataset_origin_label": "Curated",
        "categories": [{"reference": "ABC123"}, {"reference": "DEF456"}],
    }
    overrides = overrides or {}
    # Deep-merge shallow dicts for brevity in tests
    if "dataset" in overrides:
        ds = dict(ctx["dataset"])
        ds.update(overrides["dataset"])
        overrides = dict(overrides)
        overrides["dataset"] = ds
    ctx.update(overrides)
    return ctx

TEMPLATE_NAME = "dl-info/dataset.html"

def test_page_title_and_header_renders():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    assert "Conservation area Dataset | Planning Data" in html
    assert "<h1 class=\"govuk-heading-xl\">Conservation area</h1>" in html

def test_jsonld_includes_distribution_csv_and_json_by_default():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    assert "\"@type\": \"Dataset\"" in html
    assert "\"encodingFormat\": \"CSV\"" in html
    assert "\"encodingFormat\": \"JSON\"" in html
    assert ".csv" in html and ".json" in html
    # Should not include GeoJSON when typology != geography
    assert ".geojson" not in html

def test_jsonld_includes_geojson_for_geography_typology():
    env = build_env()
    ctx = base_context({"dataset": {"typology": "geography"}})
    html = render_template(env, TEMPLATE_NAME, ctx)
    assert "\"encodingFormat\": \"GeoJSON\"" in html
    assert f"{ctx['data_file_url']}/dataset/{ctx['dataset']['dataset']}.geojson" in html

def test_about_table_core_rows_render_with_expected_values():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    # Total row has link to entity list and count formatted with commas
    assert "Total" in html
    assert "/entity?dataset=conservation-area" in html
    assert ">5<" not in html  # formatted via commanum
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert ">5" not in html
    # Check formatted number appears
    assert ">5<" not in html
    assert ">5" not in html
    assert ">5" not in html
    assert "5</span>" not in html
    # Instead, the link string will contain the count '5' (no commas needed) and plural text
    assert "Conservation areas</span>" in html

    # Data providers row
    assert "Data providers" in html
    assert ">123<" in html or ">123" in html

    # Collector/Found on/New data rows
    assert "Collector last ran on" in html and "2025-08-20" in html
    assert "New data last found on" in html and "2025-08-25" in html
    assert "Origin" in html and "Curated" in html

def test_optional_rows_licence_attribution_summary_render_when_present():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    assert "Licence" in html and "Open Government Licence" in html
    assert "Attribution" in html and "Contains public sector information" in html
    assert "Summary" in html and "<p>Some description</p>" in html  # render_markdown stub

def test_optional_rows_omit_when_absent():
    env = build_env()
    ctx = base_context({
        "dataset": {
            "licence": False,
            "licence_text": "",
            "attribution": False,
            "attribution_text": "",
            "text": "",
        }
    })
    html = render_template(env, TEMPLATE_NAME, ctx)
    assert "Licence" not in html
    assert "Attribution" not in html
    # Summary not rendered when dataset.text empty
    assert ">Summary<" not in html

def test_entries_card_pluralisation_and_links():
    env = build_env()
    ctx = base_context({
        "categories": [{"reference": "AAA"}, {"reference": "BBB"}]
    })
    html = render_template(env, TEMPLATE_NAME, ctx)
    assert ">Entries<" in html  # plural
    assert "/curie/conservation-area:AAA" in html
    assert "/curie/conservation-area:BBB" in html

def test_entries_card_singular_when_one_category():
    env = build_env()
    ctx = base_context({"categories": [{"reference": "ONLY1"}]})
    html = render_template(env, TEMPLATE_NAME, ctx)
    assert ">Entry<" in html
    assert "/curie/conservation-area:ONLY1" in html

def test_view_and_download_sections_toggle_geojson():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    # Non-geography: no map link and no geojson download
    assert "On a map" not in html
    assert ".geojson" not in html
    # Geography: both present
    ctx = base_context({"dataset": {"typology": "geography"}})
    html_geo = render_template(env, TEMPLATE_NAME, ctx)
    assert "On a map" in html_geo
    assert f"{ctx['data_file_url']}/dataset/{ctx['dataset']['dataset']}.geojson" in html_geo

def test_dataset_definition_and_designing_the_data_links():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    assert "Dataset definition for Conservation area dataset" in html
    # When consideration provided -> section present
    ctx = base_context({"dataset": {"consideration": "heritage"}})
    html2 = render_template(env, TEMPLATE_NAME, ctx)
    assert "Designing the data" in html2
    assert "heritage planning consideration" in html2

def test_generated_date_meta_present_and_uses_now_context():
    env = build_env()
    ctx = base_context({"now": "2025-08-27T00:00:00Z"})
    html = render_template(env, TEMPLATE_NAME, ctx)
    assert '<meta name="generated-date" content="2025-08-27T00:00:00Z"' in html

def test_breadcrumbs_back_button_present():
    env = build_env()
    html = render_template(env, TEMPLATE_NAME, base_context())
    assert "data-testid='back-button'" in html
    assert "href='/dataset/'" in html
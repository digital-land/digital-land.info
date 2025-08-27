# Test framework: pytest + Jinja2
# These tests focus on the dataset template behaviour described in the PR diff.
# We render the template in isolation with stubbed dependencies/macros/filters to ensure hermetic unit tests.

import json
import re
from dataclasses import dataclass
from typing import Any, Dict

import pytest
from jinja2 import Environment, DictLoader
from markupsafe import Markup

# ---- Stubs for dependent templates/macros the template extends/includes/calls ----

LAYOUT_STUB = """
<!doctype html>
<html lang="en">
  <head>
    <title>{% block pageTitle %}{% endblock %}</title>
    {% block headStart %}{% endblock %}
  </head>
  <body>
    <nav id="breadcrumbs">{% block breadcrumbs %}{% endblock %}</nav>
    <main id="content">{% block content %}{% endblock %}</main>
  </body>
</html>
"""

SUMMARY_CARD_MACRO = """
{% macro appSummaryCard(params) -%}
<div class="app-summary-card {{ params.classes|default('') }}">
  {% if params.titleText %}<h2 class="govuk-heading-m">{{ params.titleText }}</h2>{% endif %}
  {{ caller() }}
</div>
{%- endmacro %}
"""

BACK_BUTTON_MACRO = """
{% macro dlBackButton(params) -%}
<a class="app-back-button" href="{{ params.parentHref }}">Back</a>
{%- endmacro %}
"""

GOVUK_TABLE_MACRO = """
{% macro govukTable(args) -%}
<table class="govuk-table" aria-label="{{ args.attributes['aria-label'] }}">
  <tbody class="govuk-table__body">
  {%- for row in args.rows %}
    <tr class="govuk-table__row">
    {%- for cell in row %}
      <td class="govuk-table__cell app-table__cell">{{ cell.html | safe }}</td>
    {%- endfor %}
    </tr>
  {%- endfor %}
  </tbody>
</table>
{%- endmacro %}
"""

INCLUDE_DATA_COVERAGE_BANNER = '<div id="data-coverage-banner"></div>'
INCLUDE_FEEDBACK = '<div id="feedback"></div>'

# ---- Template under test (captured from PR diff) ----
TEMPLATE_NAME = "dl-info/dataset.html"
TEMPLATE_UNDER_TEST = r"""{% extends "layouts/layout.html" %}
{% from 'components/summary-card/macro.jinja' import appSummaryCard %}
{% set templateName = 'dl-info/dataset.html' %}
{%- from "components/back-button/macro.jinja" import dlBackButton %}
{% from 'govuk_frontend_jinja/components/table/macro.html' import govukTable %}

{% block pageTitle %}{{ dataset["name"] }} Dataset | Planning Data{% endblock %}

{% block headStart %}
  <meta name="generated-date" content="{{ now }}"/>
  <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Dataset",
      "name": {{ dataset["name"]|tojson }},
      "description": {{ dataset["text"]|default('')|striptags|trim|tojson}},
      "url": {{ ("https://planning.data.gov.uk/dataset/" ~ dataset["dataset"])|tojson }},
      "license": {{ dataset["licence_text"]|default('')|tojson}},
      "isAccessibleForFree": true,
      "creator": {
        "@type": "Organization",
        "name": "Ministry of Housing, Communities and Local Government",
        "url": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government"
      },
      "distribution": [
        {
          "@type": "DataDownload",
          "encodingFormat": "CSV",
          "contentUrl": {{ (data_file_url ~ '/dataset/' ~ dataset["dataset"] ~ '.csv')|tojson}},
        },
        {
          "@type": "DataDownload",
          "encodingFormat": "JSON",
          "contentUrl": {{ (data_file_url ~ '/dataset/' ~ dataset["dataset"] ~ '.json')|tojson}}
        }{% if dataset['typology'] == 'geography' %},
        {
          "@type": "DataDownload",
          "encodingFormat": "GeoJSON",
          "contentUrl": {{ (data_file_url ~ '/dataset/' ~ dataset["dataset"] ~ '.geojson')|tojson}}
        }
        {% endif %}
      ]
    }
  </script>
{% endblock headStart %}

{%- block breadcrumbs -%}
    {{ dlBackButton({
      "parentHref": '/dataset/'
    })}}
{%- endblock -%}

{% block content %}

  <div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">
      <span class="govuk-caption-xl">Dataset</span>
      <h1 class="govuk-heading-xl">{{ dataset["name"] }}</h1>
      {% include 'partials/data-coverage-banner.html' %}
    </div>
  </div>
  <!-- /.govuk-grid-row -->

  <div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">

     {% call appSummaryCard({
        'classes': 'govuk-!-margin-bottom-0',
        'titleText': 'About this dataset'
      }) %}

      {%
        set rows = [
          [
            {
              'html': '<b>Total</b>',
              'attributes': {
                'style': 'width: 35%'
              }
            },
            {
              'html': '<a class="govuk-link" href="/entity?dataset=' + dataset["dataset"] + '">' + entity_count|commanum + '<br><span class="govuk-!-font-size-14">' + (dataset["name"] if entity_count <= 1 else dataset["plural"]) +'</span></a>'
            },
          ],
          [
            {
              'html': '<b>Data providers</b>',
            },
            {
              'html': publishers['current']|commanum,
            },
          ],
          [
            {
              'html': '<b>Collector last ran on</b>'
            },
            {
              'html': last_collection_attempt if last_collection_attempt else 'no attempt'
            },
          ],
          [
            {
              'html': '<b>New data last found on</b>'
            },
            {
              'html': latest_resource.last_updated if latest_resource.last_updated else 'N/A'
            },
          ],
          [
            {
              'html': '<b>Origin</b>'
            },
            {
              'html': dataset_origin_label
            }
          ]
        ]
      %}

      {% if dataset.licence %}
        {{
          rows.append([
            {
              'html': '<b>Licence</b>'
            },
            {
              'html': dataset.licence_text | render_markdown(govAttributes=True)
            },
          ]) or ''
        }}
      {% endif %}

      {% if dataset.attribution %}
        {{
          rows.append([
            {
              'html': '<b>Attribution</b>'
            },
            {
              'html': dataset.attribution_text | render_markdown(govAttributes=True) if dataset.attribution else ''
            },
          ]) or ''
        }}
      {% endif %}

      {% if dataset.text %}
        {{
          rows.append([
            {
              'html': '<b>Summary</b>'
            },
            {
              'html': dataset.text | render_markdown(govAttributes=True)
            },
          ]) or ''
        }}
      {% endif %}

      {{
        govukTable({
          'attributes': {
            'aria-label': 'About the dataset'
          },
          'rows': rows
        })
      }}

      {% endcall %}

      {% if categories %}
        {% call appSummaryCard({
          'classes': 'govuk-!-margin-top-6 govuk-!-margin-bottom-0',
          'titleText': 'Entries' if categories| length > 1 else 'Entry'
        }) %}
          <table class="govuk-table">
            <thead class="govuk-table__head">
              <tr class="govuk-table__row">
                <th scope="col" class="govuk-table__header">
                  Reference
                </th>
              </tr>
            </thead>
            <tbody class="govuk-table__body">
              {% for category in categories %}
                <tr class="govuk-table__row">
                  <td class="govuk-table__cell app-table__cell">
                      <a class="govuk-link"  href="/curie/{{dataset['dataset']}}:{{category['reference']}}">{{category['reference']}}</a>
                  </td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        {% endcall %}
      {% endif %}

    </div>
    <!-- /. govuk-grid-column -->

    <div class="govuk-grid-column-one-third">

      <aside class="app-related-items" role="complementary">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="view-the-data">
          View the data
        </h2>
        <p class="govuk-hint govuk-!-font-size-14">You can explore this data</p>
        <nav role="navigation" aria-labelledby="view-the-data">
          <ul class="govuk-list govuk-!-font-size-16">
            {% if dataset['typology'] == 'geography' %}
              <li>
                <a class="govuk-link" href='/map?dataset={{dataset["dataset"]}}'>On a map</a>
              </li>
            {% endif %}
            <li>
              <a class="govuk-link" href="/entity?dataset={{dataset["dataset"]}}">As a list</a>
            </li>
          </ul>
        </nav>
        <hr class="govuk-section-break govuk-section-break--m">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="download-the-data">
          Download the data
        </h2>
        <p class="govuk-hint govuk-!-font-size-14">You can take a copy of this data as</p>
        <nav role="navigation" aria-labelledby="download-the-data">
          <ul class="govuk-list govuk-!-font-size-16">
            <li>
              <a class="govuk-link" href="{{ data_file_url }}/dataset/{{ dataset["dataset"] }}.csv">CSV</a>
            </li>
            <li>
              <a class="govuk-link" href="{{ data_file_url }}/dataset/{{ dataset['dataset'] }}.json">JSON</a>
            </li>
            {% if dataset['typology'] == 'geography' %}
            <li>
              <a class="govuk-link" href="{{ data_file_url }}/dataset/{{ dataset["dataset"] }}.geojson">GeoJSON</a>
            </li>
            {% endif %}
          </ul>
        </nav>
        <hr class="govuk-section-break govuk-section-break--m">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="specification">
          Dataset definition
        </h2>
        <p class="govuk-hint govuk-!-font-size-14">You can view the definition of this dataset including the list of fields</p>
        <nav role="navigation" aria-labelledby="specification">
          <ul class="govuk-list govuk-!-font-size-16">
            <li>
              <a class="govuk-link" href="https://digital-land.github.io/specification/dataset/{{ dataset["dataset"] }}">Dataset definition for {{ dataset["name"] }} dataset</a>
            </li>
          </ul>
        </nav>
        {% if dataset['consideration'] %}
        <hr class="govuk-section-break govuk-section-break--m">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="data-design">
          Designing the data
        </h2>
        <p class="govuk-hint govuk-!-font-size-14">You can see details about how this dataset has been designed for planning.data.gov.uk</p>
        <nav role="navigation" aria-labelledby="specification">
          <ul class="govuk-list govuk-!-font-size-16">
            <li>
              <a class="govuk-link" href="https://design.planning.data.gov.uk/planning-consideration/{{ dataset['consideration'] }}">{{ dataset['consideration'] }} planning consideration</a>
            </li>
          </ul>
        </nav>
        {% endif %}
      </aside>

    </div>

  </div>

  {% include "partials/feedback.html" %}
{% endblock %}
"""

# ---- Helpers / fixtures ----

def _tojson_filter(value):
    return Markup(json.dumps(value, ensure_ascii=False))

def _render_markdown(value, govAttributes=False):
    # Minimal pass-through "renderer" for tests, marking safe to avoid escaping
    return Markup(str(value))

def _commanum(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

@dataclass
class LatestResource:
    last_updated: Any = None

@pytest.fixture()
def jinja_env(tmp_path):
    """
    Create a hermetic Jinja2 environment with:
    - The template under test
    - Stubbed dependencies/macros/includes
    - Custom filters used by the template
    """
    stubs = {
        "layouts/layout.html": LAYOUT_STUB,
        "components/summary-card/macro.jinja": SUMMARY_CARD_MACRO,
        "components/back-button/macro.jinja": BACK_BUTTON_MACRO,
        "govuk_frontend_jinja/components/table/macro.html": GOVUK_TABLE_MACRO,
        "partials/data-coverage-banner.html": INCLUDE_DATA_COVERAGE_BANNER,
        "partials/feedback.html": INCLUDE_FEEDBACK,
        TEMPLATE_NAME: TEMPLATE_UNDER_TEST,
    }
    env = Environment(
        loader=DictLoader(stubs),
        autoescape=True,
    )
    env.filters["tojson"] = _tojson_filter
    env.filters["render_markdown"] = _render_markdown
    env.filters["commanum"] = _commanum
    return env

def render(env, context: Dict[str, Any]) -> str:
    tpl = env.get_template(TEMPLATE_NAME)
    return tpl.render(**context)

def extract_jsonld(html: str) -> Dict[str, Any]:
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
    assert m, "JSON-LD script block not found"
    return json.loads(m.group(1))

# ---- Base context factory ----

def make_base_context(**overrides) -> Dict[str, Any]:
    ctx = {
        "now": "2025-08-27T00:00:00Z",
        "data_file_url": "https://files.example.test",
        "dataset": {
            "dataset": "brownfield-land",
            "name": "Brownfield land",
            "plural": "Brownfield land sites",
            "typology": "geography",
            "licence": True,
            "licence_text": "Open Government Licence v3.0",
            "attribution": True,
            "attribution_text": "Contains data © contributors",
            "text": "This is a summary.",
            "consideration": "brownfield-land",
        },
        "entity_count": 12345,
        "publishers": {"current": 6789},
        "latest_resource": LatestResource(last_updated="2025-08-20"),
        "last_collection_attempt": "2025-08-21",
        "dataset_origin_label": "Curated",
        "categories": [{"reference": "ABC-123"}, {"reference": "XYZ-999"}],
    }
    # Deep update for 'dataset' if provided
    if "dataset" in overrides:
        ctx["dataset"].update(overrides.pop("dataset"))
    ctx.update(overrides)
    return ctx

# ---- Tests ----

def test_meta_generated_date_present(jinja_env):
    html = render(jinja_env, make_base_context())
    assert 'meta name="generated-date"' in html
    assert 'content="2025-08-27T00:00:00Z"' in html

def test_jsonld_core_fields_and_geojson_when_geography(jinja_env):
    ctx = make_base_context()
    html = render(jinja_env, ctx)
    data = extract_jsonld(html)
    assert data["@type"] == "Dataset"
    assert data["name"] == ctx["dataset"]["name"]
    assert data["url"].endswith("/dataset/brownfield-land")
    # Distributions include CSV, JSON, GeoJSON when typology=geography
    encs = [d["encodingFormat"] for d in data["distribution"]]
    assert "CSV" in encs and "JSON" in encs and "GeoJSON" in encs
    # Links point at data_file_url with dataset slug
    hrefs = [d["contentUrl"] for d in data["distribution"]]
    assert f"{ctx['data_file_url']}/dataset/brownfield-land.csv" in hrefs
    assert f"{ctx['data_file_url']}/dataset/brownfield-land.json" in hrefs
    assert f"{ctx['data_file_url']}/dataset/brownfield-land.geojson" in hrefs

def test_jsonld_excludes_geojson_for_non_geography(jinja_env):
    ctx = make_base_context(dataset={"typology": "dataset"})
    html = render(jinja_env, ctx)
    data = extract_jsonld(html)
    encs = [d["encodingFormat"] for d in data["distribution"]]
    assert "GeoJSON" not in encs

def test_about_table_core_rows_render_and_commanum_filter(jinja_env):
    ctx = make_base_context(entity_count=10000, publishers={"current": 2500000})
    html = render(jinja_env, ctx)
    # Total row: anchor to /entity?dataset=slug and number comma formatted and pluralisation
    assert f'href="/entity?dataset={ctx["dataset"]["dataset"]}"' in html
    assert ">10,000<" in html
    assert ctx["dataset"]["plural"] in html
    # Data providers uses commanum
    assert ">2,500,000<" in html
    # Origin label present
    assert "<b>Origin</b>" in html
    assert ctx["dataset_origin_label"] in html

def test_collector_last_ran_and_new_data_last_found_fallbacks(jinja_env):
    ctx = make_base_context(last_collection_attempt=None, latest_resource=LatestResource(last_updated=None))
    html = render(jinja_env, ctx)
    assert ">no attempt<" in html
    assert ">N/A<" in html

def test_licence_row_rendered_when_licence_true(jinja_env):
    ctx = make_base_context(dataset={"licence": True, "licence_text": "OGL v3"})
    html = render(jinja_env, ctx)
    assert "<b>Licence</b>" in html
    assert "OGL v3" in html

def test_licence_row_not_rendered_when_licence_false(jinja_env):
    ctx = make_base_context(dataset={"licence": False})
    html = render(jinja_env, ctx)
    assert "<b>Licence</b>" not in html

def test_attribution_row_rendered_when_present_else_not(jinja_env):
    ctx = make_base_context(dataset={"attribution": True, "attribution_text": "CC-BY"})
    html = render(jinja_env, ctx)
    assert "<b>Attribution</b>" in html
    assert "CC-BY" in html

    ctx2 = make_base_context(dataset={"attribution": False})
    html2 = render(jinja_env, ctx2)
    assert "<b>Attribution</b>" not in html2

def test_summary_row_rendered_when_dataset_text_present(jinja_env):
    ctx = make_base_context(dataset={"text": "Summary markdown"})
    html = render(jinja_env, ctx)
    assert "<b>Summary</b>" in html
    assert "Summary markdown" in html

def test_entries_section_pluralisation_and_links(jinja_env):
    # Plural
    ctx = make_base_context(categories=[{"reference": "ABC"}, {"reference": "DEF"}])
    html = render(jinja_env, ctx)
    assert ">Entries<" in html
    assert f'href="/curie/{ctx["dataset"]["dataset"]}:ABC"' in html
    assert f'href="/curie/{ctx["dataset"]["dataset"]}:DEF"' in html
    # Singular
    ctx_single = make_base_context(categories=[{"reference": "ONE"}])
    html_single = render(jinja_env, ctx_single)
    assert ">Entry<" in html_single
    assert f'href="/curie/{ctx_single["dataset"]["dataset"]}:ONE"' in html_single
    # Absent when no categories
    ctx_none = make_base_context(categories=[])
    html_none = render(jinja_env, ctx_none)
    assert ">Entry<" not in html_none and ">Entries<" not in html_none

def test_view_the_data_links_conditionals(jinja_env):
    # geography -> includes map + list
    ctx = make_base_context(dataset={"typology": "geography"})
    html = render(jinja_env, ctx)
    assert f"href='/map?dataset={ctx['dataset']['dataset']}'" in html
    assert f'href="/entity?dataset={ctx["dataset"]["dataset"]}"' in html
    # non-geography -> only list
    ctx2 = make_base_context(dataset={"typology": "dataset"})
    html2 = render(jinja_env, ctx2)
    assert "href='/map?dataset=" not in html2
    assert f'href="/entity?dataset={ctx2["dataset"]["dataset"]}"' in html2

def test_download_the_data_links_and_geojson_condition(jinja_env):
    ctx = make_base_context(dataset={"typology": "geography"})
    html = render(jinja_env, ctx)
    base = ctx["data_file_url"]
    slug = ctx["dataset"]["dataset"]
    assert f'href="{base}/dataset/{slug}.csv"' in html
    assert f'href="{base}/dataset/{slug}.json"' in html
    assert f'href="{base}/dataset/{slug}.geojson"' in html

    ctx2 = make_base_context(dataset={"typology": "dataset"})
    html2 = render(jinja_env, ctx2)
    assert f'href="{base}/dataset/{slug}.csv"' in html2
    assert f'href="{base}/dataset/{slug}.json"' in html2
    assert f'href="{base}/dataset/{slug}.geojson"' not in html2

def test_dataset_definition_and_designing_the_data_sections(jinja_env):
    ctx = make_base_context(dataset={"name": "Brownfield land", "dataset": "brownfield-land", "consideration": "brownfield-land"})
    html = render(jinja_env, ctx)
    assert 'href="https://digital-land.github.io/specification/dataset/brownfield-land"' in html
    assert ">Dataset definition for Brownfield land dataset<" in html
    assert 'href="https://design.planning.data.gov.uk/planning-consideration/brownfield-land"' in html
    assert ">brownfield-land planning consideration<" in html

    # When consideration absent, section hidden
    ctx2 = make_base_context(dataset={"consideration": None})
    html2 = render(jinja_env, ctx2)
    assert "planning-consideration" not in html2

def test_back_button_points_to_dataset_root(jinja_env):
    html = render(jinja_env, make_base_context())
    assert 'class="app-back-button"' in html
    assert 'href="/dataset/"' in html

def test_page_title_includes_dataset_name_and_suffix(jinja_env):
    ctx = make_base_context(dataset={"name": "Conservation areas"})
    html = render(jinja_env, ctx)
    # Extract the <title> content
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    assert m
    assert m.group(1) == "Conservation areas Dataset | Planning Data"
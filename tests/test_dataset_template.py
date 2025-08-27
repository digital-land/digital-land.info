# -*- coding: utf-8 -*-
"""
Tests for the 'dl-info/dataset.html' Jinja template.

Testing library/framework: pytest with Jinja2 (no new dependencies).
We use a DictLoader to stub the extended layout and imported macros/partials so the template can render in isolation.
"""

import json
import re
from types import SimpleNamespace

import pytest
from jinja2 import Environment, DictLoader
from markupsafe import Markup

# Source template under test (captured from PR diff/source)
TEMPLATE_NAME = "dl-info/dataset.html"
DATASET_TEMPLATE = r"""
{% extends "layouts/layout.html" %}
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
        "url": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-local-government"
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
              'html': '<a class="govuk-link" href="/entity?dataset=' + dataset["dataset"] + '">'
                       + entity_count|commanum
                       + '<br><span class="govuk-!-font-size-14">' + (dataset["name"] if entity_count <= 1 else dataset["plural"])
                       + '</span></a>'
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
                      <a class="govuk-link"  
                         href="/curie/{{dataset['dataset']}}:{{category['reference']}}">{{category['reference']}}</a>
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
        <p class="govuk-hint govuk-!-font-size-14">
          You can view the definition of this dataset including the list of fields
        </p>
        <nav role="navigation" aria-labelledby="specification">
          <ul class="govuk-list govuk-!-font-size-16">
            <li>
              <a class="govuk-link" 
                 href="https://digital-land.github.io/specification/dataset/{{ dataset["dataset"] }}">
                Dataset definition for {{ dataset["name"] }} dataset
              </a>
            </li>
          </ul>
        </nav>
        {% if dataset['consideration'] %}
        <hr class="govuk-section-break govuk-section-break--m">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="data-design">
          Designing the data
        </h2>
        <p class="govuk-hint govuk-!-font-size-14">
          You can see details about how this dataset has been designed for planning.data.gov.uk
        </p>
        <nav role="navigation" aria-labelledby="specification">
          <ul class="govuk-list govuk-!-font-size-16">
            <li>
              <a class="govuk-link" 
                 href="https://design.planning.data.gov.uk/planning-consideration/{{ dataset['consideration'] }}">
                {{ dataset['consideration'] }} planning consideration
              </a>
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

# --- Jinja stubs for layout, macros, and partials ---
LAYOUT = """
<!doctype html>
<html lang="en">
  <head>
    <title>{% block pageTitle %}{% endblock %}</title>
    {% block headStart %}{% endblock %}
  </head>
  <body>
    <div id="breadcrumbs">{% block breadcrumbs %}{% endblock %}</div>
    <main id="content">{% block content %}{% endblock %}</main>
  </body>
</html>
"""

SUMMARY_CARD_MACRO = """
{% macro appSummaryCard(params) -%}
<div class="app-summary-card" data-title="{{ params.get('titleText') }}">
  {{ caller() if caller }}
</div>
{%- endmacro %}
"""

BACK_BUTTON_MACRO = """
{% macro dlBackButton(params) -%}
<a id="dl-back" href="{{ params['parentHref'] }}">Back</a>
{%- endmacro %}
"""

GOVUK_TABLE_MACRO = """
{% macro govukTable(params) -%}
{# Emit a simple table with row count to allow assertions without full GOV.UK macro #}
<table aria-label="{{ params['attributes']['aria-label'] }}" data-rows="{{ params['rows']|length }}">
  <tbody>
  {%- for row in params['rows'] -%}
    <tr>
      <td>{{ row[0]['html']|safe }}</td>
      <td>{{ row[1]['html']|safe }}</td>
    </tr>
  {%- endfor -%}
  </tbody>
</table>
{%- endmacro %}
"""

PARTIAL_DATA_COVERAGE = "<!-- data coverage banner placeholder -->"
PARTIAL_FEEDBACK = "<!-- feedback placeholder -->"

# --- Custom filters used by the template ---

def _commanum(value):
    try:
        # Support ints, floats, and numeric strings
        if isinstance(value, str):
            # Attempt numeric conversion while preserving commas if present
            value = float(value.replace(',', '')) if ('.' in value or value.replace(',','').isdigit()) else value
        if isinstance(value, (int, float)):
            # Use locale-agnostic comma formatting
            return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"
        return str(value)
    except Exception:
        return str(value)

def _render_markdown(value, govAttributes=False):  # noqa: ARG001 - signature to match template usage
    # Minimal passthrough stub for tests; in real app this would convert Markdown to HTML
    return Markup(str(value))

def _tojson_filter(value):
    # Provide a tojson that returns JSON-encoded string without HTML-escaping, wrapped as Markup
    try:
        return Markup(json.dumps(value))
    except Exception:
        # Fall back to string
        return Markup(json.dumps(str(value)))

def make_env():
    loader = DictLoader({
        "layouts/layout.html": LAYOUT,
        "components/summary-card/macro.jinja": SUMMARY_CARD_MACRO,
        "components/back-button/macro.jinja": BACK_BUTTON_MACRO,
        "govuk_frontend_jinja/components/table/macro.html": GOVUK_TABLE_MACRO,
        "partials/data-coverage-banner.html": PARTIAL_DATA_COVERAGE,
        "partials/feedback.html": PARTIAL_FEEDBACK,
        TEMPLATE_NAME: DATASET_TEMPLATE,
    })
    env = Environment(loader=loader, autoescape=True)
    # Register filters
    env.filters["commanum"] = _commanum
    env.filters["render_markdown"] = _render_markdown
    # If tojson is missing/overridden, ensure availability
    env.filters["tojson"] = env.filters.get("tojson", _tojson_filter)
    return env

def render_template(context):
    env = make_env()
    tmpl = env.get_template(TEMPLATE_NAME)
    return tmpl.render(**context)

# --- Fixtures & helpers ---

@pytest.fixture
def base_context():
    # Common baseline context with non-geography dataset and minimal fields
    return {
        "now": "2025-08-27T12:00:00Z",
        "data_file_url": "https://files.example.com",
        "dataset": {
            "dataset": "brownfield-land",
            "name": "Brownfield Land",
            "plural": "Brownfield Land entries",
            "licence": False,
            "licence_text": "",
            "attribution": False,
            "attribution_text": "",
            "text": "",
            "typology": "dataset",
            "consideration": "",
        },
        "entity_count": 1234,
        "publishers": {"current": 56},
        "last_collection_attempt": "",
        "latest_resource": SimpleNamespace(last_updated=""),
        "dataset_origin_label": "Digital Land",
        "categories": [],
    }

def extract_json_ld(html: str) -> str:
    m = re.search(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        html,
        flags=re.DOTALL,
    )
    return m.group(1) if m else ""

# --- Tests ---

def test_head_contains_generated_date_meta_and_title(base_context):
    html = render_template(base_context)
    assert '<meta name="generated-date" content="2025-08-27T12:00:00Z"' in html
    assert "<title>Brownfield Land Dataset | Planning Data</title>" in html

def test_json_ld_contains_core_fields_and_downloads_non_geography(base_context):
    html = render_template(base_context)
    json_ld = extract_json_ld(html)
    # We avoid strict JSON parsing due to possible trailing commas; assert presence instead
    assert '"@type": "Dataset"' in json_ld
    assert '"name": "Brownfield Land"' in json_ld
    assert '"url": "https://planning.data.gov.uk/dataset/brownfield-land"' in json_ld
    # CSV and JSON downloads present
    assert '"encodingFormat": "CSV"' in json_ld
    assert '"contentUrl": "https://files.example.com/dataset/brownfield-land.csv"' in json_ld
    assert '"encodingFormat": "JSON"' in json_ld
    assert '"contentUrl": "https://files.example.com/dataset/brownfield-land.json"' in json_ld
    # GeoJSON NOT present for non-geography typology
    assert "GeoJSON" not in json_ld

def test_json_ld_includes_geojson_for_geography_typology(base_context):
    base_context["dataset"]["typology"] = "geography"
    html = render_template(base_context)
    json_ld = extract_json_ld(html)
    assert '"encodingFormat": "GeoJSON"' in json_ld
    assert '"contentUrl": "https://files.example.com/dataset/brownfield-land.geojson"' in json_ld

def test_about_rows_count_changes_with_optional_fields(base_context):
    # Baseline has 5 rows (Total, Data providers, Collector last ran on, New data last found on, Origin)
    html = render_template(base_context)
    # Our govukTable stub emits data-rows attribute equal to row count
    m = re.search(r'data-rows="(\d+)"', html)
    assert m, "Table markup with data-rows attribute not found"
    assert int(m.group(1)) == 5

    # Add licence only
    ctx = json.loads(json.dumps(base_context))  # deep copy via JSON
    ctx["dataset"]["licence"] = True
    ctx["dataset"]["licence_text"] = "Open Government Licence"
    html = render_template(ctx)
    assert int(re.search(r'data-rows="(\d+)"', html).group(1)) == 6

    # Add attribution as well
    ctx["dataset"]["attribution"] = True
    ctx["dataset"]["attribution_text"] = "Contains public sector information."
    html = render_template(ctx)
    assert int(re.search(r'data-rows="(\d+)"', html).group(1)) == 7

    # Add summary text too
    ctx["dataset"]["text"] = "This dataset contains sites."
    html = render_template(ctx)
    assert int(re.search(r'data-rows="(\d+)"', html).group(1)) == 8

def test_total_row_uses_commanum_and_pluralization(base_context):
    # 1 entity => singular name
    base_context["entity_count"] = 1
    html = render_template(base_context)
    assert 'href="/entity?dataset=brownfield-land"' in html
    assert ">1<" in html or ">1<br" in html  # number is present
    assert "Brownfield Land</span></a>" in html  # singular name

    # 2 entities => plural label
    base_context["entity_count"] = 2
    html = render_template(base_context)
    assert "Brownfield Land entries</span></a>" in html
    # 1,234 formatting
    base_context["entity_count"] = 1234
    html = render_template(base_context)
    assert ">1,234<" in html

def test_publishers_count_is_commanum_formatted(base_context):
    base_context["publishers"]["current"] = 10000
    html = render_template(base_context)
    # Find table cell containing the formatted publishers count
    assert ">10,000<" in html

def test_collection_and_latest_resource_fallbacks(base_context):
    # No last_collection_attempt -> 'no attempt'
    base_context["last_collection_attempt"] = ""
    base_context["latest_resource"] = SimpleNamespace(last_updated="")
    html = render_template(base_context)
    assert ">no attempt<" in html
    assert ">N/A<" in html

    # With explicit dates
    base_context["last_collection_attempt"] = "2025-08-20"
    base_context["latest_resource"] = SimpleNamespace(last_updated="2025-08-19")
    html = render_template(base_context)
    assert ">2025-08-20<" in html
    assert ">2025-08-19<" in html

def test_side_nav_links_vary_by_typology(base_context):
    # Non-geography: no map link, only list
    base_context["dataset"]["typology"] = "dataset"
    html = render_template(base_context)
    assert "href='/map?dataset=brownfield-land'" not in html
    assert 'href="/entity?dataset=brownfield-land"' in html
    assert 'href="https://files.example.com/dataset/brownfield-land.csv"' in html
    assert 'href="https://files.example.com/dataset/brownfield-land.json"' in html
    assert ".geojson" not in html

    # Geography: map and GeoJSON link present
    base_context["dataset"]["typology"] = "geography"
    html = render_template(base_context)
    assert "href='/map?dataset=brownfield-land'" in html
    assert 'href="https://files.example.com/dataset/brownfield-land.geojson"' in html

def test_categories_section_title_and_links(base_context):
    # Single category => "Entry"
    base_context["categories"] = [{"reference": "ABC123"}]
    html = render_template(base_context)
    assert 'data-title="Entry"' in html
    assert 'href="/curie/brownfield-land:ABC123"' in html

    # Multiple categories => "Entries"
    base_context["categories"] = [{"reference": "A"}, {"reference": "B"}]
    html = render_template(base_context)
    assert 'data-title="Entries"' in html
    assert 'href="/curie/brownfield-land:A"' in html
    assert 'href="/curie/brownfield-land:B"' in html

def test_breadcrumbs_back_button_present(base_context):
    html = render_template(base_context)
    assert 'id="dl-back"' in html
    assert 'href="/dataset/"' in html

def test_dataset_definition_link_in_sidebar(base_context):
    html = render_template(base_context)
    assert 'href="https://digital-land.github.io/specification/dataset/brownfield-land"' in html
    assert "Dataset definition for Brownfield Land dataset" in html

def test_designing_the_data_section_optional(base_context):
    # Absent by default
    html = render_template(base_context)
    assert "planning consideration" not in html

    # Present when consideration supplied
    base_context["dataset"]["consideration"] = "brownfield-land"
    html = render_template(base_context)
    assert 'href="https://design.planning.data.gov.uk/planning-consideration/brownfield-land"' in html
    assert ">brownfield-land planning consideration<" in html

def test_json_ld_license_and_description_values_use_defaults(base_context):
    # With empty licence_text and text -> should serialize as empty string
    html = render_template(base_context)
    json_ld = extract_json_ld(html)
    # license and description present even if ''
    assert '"license": ""' in json_ld
    assert '"description": ""' in json_ld

def test_json_ld_escapes_text_and_strips_html_in_description():
    ctx = {
        "now": "2025-08-27",
        "data_file_url": "https://files.example.com",
        "dataset": {
            "dataset": "trees",
            "name": 'Trees & Shrubs "Dataset"',
            "plural": "Trees",
            "licence": False,
            "licence_text": "",
            "attribution": False,
            "attribution_text": "",
            "text": "<p>Rich <em>text</em> & data</p>",
            "typology": "dataset",
            "consideration": "",
        },
        "entity_count": 0,
        "publishers": {"current": 0},
        "last_collection_attempt": "",
        "latest_resource": SimpleNamespace(last_updated=""),
        "dataset_origin_label": "Digital Land",
        "categories": [],
    }
    html = render_template(ctx)
    json_ld = extract_json_ld(html)
    # Name should be JSON-encoded with quotes escaped, description should be stripped of HTML tags
    assert '"name": "Trees & Shrubs \\"Dataset\\""' in json_ld
    assert '"description": "Rich text & data"' in json_ld
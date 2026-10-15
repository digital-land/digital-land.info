from types import SimpleNamespace

import pytest

from application.data_access.fact_queries import (
    get_fact_query,
    get_search_facts_query,
)


@pytest.fixture(params=["single", "search"])
def query_facts(request, mocker):
    mocker.patch(
        "application.data_access.fact_queries.get_settings",
        return_value=SimpleNamespace(DATASETTE_URL="https://datasette.example"),
    )
    response = mocker.Mock()
    http = mocker.patch("application.data_access.fact_queries.get_datasette_http")
    http.return_value.get.return_value = response

    def query(rows):
        response.json.return_value = rows
        if request.param == "single":
            fact = get_fact_query(rows[0]["fact"], "listed-building")
            return None if fact is None else [fact]
        return get_search_facts_query(
            {"dataset": "listed-building", "entity": 1, "field": []}
        )

    return query


def fact_row(value, **overrides):
    return {
        "fact": "a" * 64,
        "entity": 1,
        "field": "end-date",
        "value": value,
        "reference_entity": "",
        "entity_name": "",
        "earliest_entry_date": "",
        "latest_entry_date": "",
        **overrides,
    }


@pytest.mark.parametrize("value", ["", "2026-10-15", "0"])
def test_fact_values_are_preserved(query_facts, value, caplog):
    facts = query_facts([fact_row(value)])

    assert facts is not None
    assert facts[0].value == value
    assert facts[0].reference_entity is None
    assert facts[0].entity_name is None
    assert facts[0].earliest_entry_date is None
    assert facts[0].latest_entry_date is None
    assert not caplog.records


def test_zero_reference_entity_is_preserved(query_facts):
    facts = query_facts([fact_row("", reference_entity=0)])

    assert facts is not None
    assert facts[0].reference_entity == 0


def test_null_fact_value_still_fails_validation(query_facts, caplog):
    assert query_facts([fact_row(None)]) is None
    assert "Input should be a valid string" in caplog.text


def test_search_keeps_other_facts_when_end_date_is_empty(mocker, caplog):
    mocker.patch(
        "application.data_access.fact_queries.get_settings",
        return_value=SimpleNamespace(DATASETTE_URL="https://datasette.example"),
    )
    http = mocker.patch("application.data_access.fact_queries.get_datasette_http")
    http.return_value.get.return_value.json.return_value = [
        fact_row("Example building", fact="b" * 64, field="name"),
        fact_row(""),
    ]

    facts = get_search_facts_query(
        {"dataset": "listed-building", "entity": 1, "field": []}
    )

    assert facts is not None
    assert [(fact.field, fact.value) for fact in facts] == [
        ("name", "Example building"),
        ("end-date", ""),
    ]
    assert not caplog.records

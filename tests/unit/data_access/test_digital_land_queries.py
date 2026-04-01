from application.core.models import DatasetModel
from application.data_access.digital_land_queries import (
    get_dataset_filter_fields,
    get_dataset_quality_values,
)
from application.db.models import EntityOrm


def test_get_dataset_filter_fields():
    dataset = DatasetModel(
        collection="ancient-woodland",
        dataset="ancient-woodland-status",
        name="Ancient woodland status",
        plural="Ancient woodlands status",
        typology="category",
    )

    result = get_dataset_filter_fields(dataset, ["name", "dataset"])

    assert "name" in result
    assert "dataset" in result
    assert result["name"] == "Ancient woodland status"


def test_get_dataset_quality_values(db_session):
    """Test that get_dataset_quality_values returns correct quality data for datasets."""

    test_entities = [
        EntityOrm(entity=1, dataset="local-authority", quality="authoritative"),
        EntityOrm(entity=2, dataset="local-authority", quality="usable"),
        EntityOrm(
            entity=3, dataset="air-quality-management-area", quality="authoritative"
        ),
        EntityOrm(entity=4, dataset="planning-application", quality=None),
    ]

    for entity in test_entities:
        db_session.add(entity)
    db_session.commit()

    result = get_dataset_quality_values(
        db_session,
        ["local-authority", "air-quality-management-area", "planning-application"],
    )
    # result will have the following structure:
    # {
    #   'air-quality-management-area': ['authoritative'],
    #   'local-authority': ['authoritative', 'usable'],
    #   'planning-application': [None]
    # }

    assert "local-authority" in result
    assert "air-quality-management-area" in result
    assert "planning-application" in result
    assert sorted(result["local-authority"]) == ["authoritative", "usable"]
    assert result["air-quality-management-area"] == ["authoritative"]
    assert result["planning-application"] == [None]  # None values should be included


def test_get_dataset_quality_values_no_datasets_filter(db_session):
    """Test that get_dataset_quality_values works without dataset filter."""

    entity = EntityOrm(entity=1, dataset="local-authority", quality="trustworthy")
    db_session.add(entity)
    db_session.commit()

    result = get_dataset_quality_values(db_session)
    assert "local-authority" in result
    assert result["local-authority"] == ["trustworthy"]


def test_get_dataset_quality_values_empty_result(db_session):
    """Test that get_dataset_quality_values returns empty dict when no data."""
    result = get_dataset_quality_values(db_session, ["non-existent"])
    assert result == {}

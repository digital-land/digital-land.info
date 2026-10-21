from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_typology,
    get_datasets_with_data_by_geography,
    get_all_datasets_with_entities,
)
from application.db.models import DatasetOrm, EntityOrm
from application.db.session import SESSION_CACHE, DbSession


def test_get_datasets_with_data_by_typology_finds_if_typology_correct_and_entities_exist(
    db_session,
):
    # add a dataset with a typology geography and one entity
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    entity = EntityOrm(
        entity=1,
        dataset="test-dataset",
        typology="geography",
    )

    db_session.add(dataset)
    db_session.add(entity)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 1


def test_get_datasets_with_data_by_typology_does_not_find_if_typology_incorrect(
    db_session,
):
    # add a dataset with a typology geography and one entity with a different dataset
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    entity = EntityOrm(
        entity=1,
        dataset="a-different-dataset",
        typology="geography",
    )

    db_session.add(dataset)
    db_session.add(entity)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 0


def test_get_datasets_with_data_by_typology_does_not_find_if_no_entities_exist(
    db_session,
):
    # add a dataset with a typology geography and no entities
    dataset = DatasetOrm(
        dataset="test-dataset",
        typology="geography",
    )

    db_session.add(dataset)

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert len(datasets) == 0


def test_get_datasets_with_data_by_geography(db_session):
    SESSION_CACHE.clear()

    dataset = DatasetOrm(
        dataset="cached-test-dataset",
        typology="geography",
    )
    entity = EntityOrm(
        entity=1,
        dataset="cached-test-dataset",
        typology="geography",
    )
    db_session.add(dataset)
    db_session.add(entity)

    datasets1 = get_datasets_with_data_by_geography(
        DbSession(session=db_session, redis=None)
    )
    assert len(datasets1) == 1


def test_get_datasets_with_data_by_typology_returns_each_matching_dataset_once(
    db_session,
):
    db_session.add_all(
        [
            DatasetOrm(dataset="matching", typology="geography"),
            DatasetOrm(dataset="empty", typology="geography"),
            DatasetOrm(dataset="other-typology", typology="category"),
            EntityOrm(entity=1, dataset="matching"),
            EntityOrm(entity=2, dataset="matching"),
            EntityOrm(entity=3, dataset="other-typology"),
        ]
    )

    datasets = get_datasets_with_data_by_typology(db_session, "geography")

    assert [dataset.dataset for dataset in datasets] == ["matching"]


def test_get_all_datasets_with_entities_spans_typologies_and_excludes_empty(
    db_session,
):
    db_session.add_all(
        [
            DatasetOrm(dataset="geography-with-data", typology="geography"),
            DatasetOrm(dataset="category-with-data", typology="category"),
            DatasetOrm(dataset="empty", typology="geography"),
            DatasetOrm(dataset="spec", typology="specification"),
            EntityOrm(entity=1, dataset="geography-with-data"),
            EntityOrm(entity=2, dataset="category-with-data"),
            EntityOrm(entity=3, dataset="spec"),
        ]
    )

    datasets = get_all_datasets_with_entities(DbSession(session=db_session, redis=None))

    assert sorted(dataset.dataset for dataset in datasets) == [
        "category-with-data",
        "geography-with-data",
    ]

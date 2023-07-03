from sqlalchemy.orm import Query
from application.data_access.entity_queries import (
    _apply_limit_and_pagination_filters,
    get_entity_search,
)
from application.db.session import get_context_session
from application.db.models import EntityOrm


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


dataset_name = "test-dataset"
base_id = 1000


def tidy():
    with get_context_session() as session:
        session.query(EntityOrm).filter(EntityOrm.dataset == dataset_name).delete()
        session.commit()


def setupDB():
    """
    Create a dataset with
    + a discontinuous series of IDs (entity column)
    + and the rows not all inserted in increasing order
    """

    with get_context_session() as session:

        for num in range(1, 24):
            e1 = EntityOrm(
                entity=base_id + num, name=f"S01Entity{num+1:04}", dataset=dataset_name
            )
            session.add(e1)

        for num in range(73, 95):
            e2 = EntityOrm(
                entity=base_id + num, name=f"S02Entity{num+1:04}", dataset=dataset_name
            )
            session.add(e2)

        for num in range(43, 55):
            e3 = EntityOrm(
                entity=base_id + num, name=f"S03Entity{num+1:04}", dataset=dataset_name
            )
            session.add(e3)

        session.commit()


def test__apply_limit_and_pagination_filters_only():
    """
    Create a dataset, and page through it, gathering the entity values (IDs) for each row.
    Make sure no values are seen twice.
    Make sure all values in db are actually collected in paged data.
    """
    tidy()
    setupDB()

    allSeen = []  # Add the entities we have seen whilst paging through the dataset
    last = 0  # tracks the last entity id we got. Used in get_entity_search below.

    search = get_entity_search(
        parameters={"dataset": [dataset_name], "offset": last, "limit": 10}
    )
    entities = search.get(
        "entities"
    )  # there are also count and params in the returned search object.

    while len(entities) == 10:
        search = get_entity_search(
            parameters={"dataset": [dataset_name], "offset": last, "limit": 10}
        )
        entities = search.get("entities")

        newValues = [x.entity for x in entities]

        # Make sure no values are seen twice.
        for value in newValues:
            assert value not in allSeen

        allSeen = allSeen + newValues
        assert len(allSeen) > 0

        allSeen.sort()

        last = entities[-1].entity

    # Make sure all values in db are actually collected in paged data.
    with get_context_session() as session:
        allEntities = (
            session.query(EntityOrm.entity)
            .filter(EntityOrm.dataset == dataset_name)
            .all()
        )

        allEntityIds = [x.entity for x in allEntities]

    diffs = list(set(allEntityIds).difference(allSeen))
    assert len(diffs) == 0
    assert len(allEntityIds) == len(allSeen)

    tidy()

from application.db.models import LookupOrm, EntityOrm
from application.data_access.curie_queries import (
    get_lookup_by_curie,
    get_entity_by_curie,
)


class TestGetLookupByCurie:
    def test_returns_empty_list_when_no_lookup_found(self, db_session):
        """Test that empty list is returned when no lookup matches the CURIE"""
        result = get_lookup_by_curie(
            session=db_session, prefix="nonexistent", reference="ref"
        )
        assert result == []

    def test_returns_single_entity_id_when_one_lookup_found(self, db_session):
        """Test that a single entity ID is returned when one lookup matches"""
        db_session.add(
            LookupOrm(
                id=1,
                entity=100,
                prefix="conservation-area",
                reference="CA001",
            )
        )
        db_session.flush()

        result = get_lookup_by_curie(
            session=db_session, prefix="conservation-area", reference="CA001"
        )

        assert result == [100]
        assert len(result) == 1

    def test_returns_multiple_entity_ids_when_duplicates_exist(self, db_session):
        """Test that multiple entity IDs are returned when duplicates exist"""
        db_session.add(
            LookupOrm(
                id=1,
                entity=100,
                prefix="conservation-area",
                reference="CA002",
            )
        )
        db_session.add(
            LookupOrm(
                id=2,
                entity=200,
                prefix="conservation-area",
                reference="CA002",
            )
        )
        db_session.flush()

        result = get_lookup_by_curie(
            session=db_session, prefix="conservation-area", reference="CA002"
        )

        assert len(result) == 2
        assert 100 in result
        assert 200 in result

    def test_does_not_return_lookups_with_different_prefix(self, db_session):
        """Test that entities with different prefix are not returned"""
        db_session.add(
            LookupOrm(
                id=1,
                entity=100,
                prefix="conservation-area",
                reference="CA003",
            )
        )
        db_session.flush()

        result = get_lookup_by_curie(
            session=db_session, prefix="different-prefix", reference="CA003"
        )

        assert result == []

    def test_does_not_return_lookups_with_different_reference(self, db_session):
        """Test that entities with different reference are not returned"""
        db_session.add(
            LookupOrm(
                id=1,
                entity=100,
                prefix="conservation-area",
                reference="CA004",
            )
        )
        db_session.flush()

        result = get_lookup_by_curie(
            session=db_session, prefix="conservation-area", reference="different-ref"
        )

        assert result == []

    def test_limit_is_two(self, db_session):
        """Test that query limits results to 2 even when more duplicates exist"""
        for i in range(5):
            db_session.add(
                LookupOrm(
                    id=i + 1,
                    entity=100 + i,
                    prefix="conservation-area",
                    reference="CA005",
                )
            )
        db_session.flush()

        result = get_lookup_by_curie(
            session=db_session, prefix="conservation-area", reference="CA005"
        )

        assert len(result) == 2


class TestGetEntityByCurie:
    def test_returns_empty_list_when_no_entity_found(self, db_session):
        """Test that empty list is returned when no entity matches the CURIE"""
        result = get_entity_by_curie(
            session=db_session, prefix="nonexistent", reference="ref"
        )
        assert result == []

    def test_returns_single_entity_id_when_one_entity_found(self, db_session):
        """Test that a single entity ID is returned when only one entity matches"""
        db_session.add(
            EntityOrm(
                entity=1001,
                prefix="local-authority-district",
                reference="LAD001",
                dataset="local-authority-district",
            )
        )
        db_session.flush()

        result = get_entity_by_curie(
            session=db_session, prefix="local-authority-district", reference="LAD001"
        )

        assert result == [1001]
        assert len(result) == 1

    def test_returns_multiple_entity_ids_when_duplicates_exist(self, db_session):
        """Test that multiple entity IDs are returned when multiple duplicates exist"""
        db_session.add(
            EntityOrm(
                entity=1001,
                prefix="local-authority-district",
                reference="LAD002",
                dataset="local-authority-district",
            )
        )
        db_session.add(
            EntityOrm(
                entity=1002,
                prefix="local-authority-district",
                reference="LAD002",
                dataset="local-authority-district",
            )
        )
        db_session.flush()

        result = get_entity_by_curie(
            session=db_session, prefix="local-authority-district", reference="LAD002"
        )

        assert len(result) == 2
        assert 1001 in result
        assert 1002 in result

    def test_does_not_return_entities_with_different_prefix(self, db_session):
        """Test that entities with different prefix are not returned"""
        db_session.add(
            EntityOrm(
                entity=1003,
                prefix="local-authority-district",
                reference="LAD003",
                dataset="local-authority-district",
            )
        )
        db_session.flush()

        result = get_entity_by_curie(
            session=db_session, prefix="different-prefix", reference="LAD003"
        )

        assert result == []

    def test_does_not_return_entities_with_different_reference(self, db_session):
        """Test that entities with different reference are not returned"""
        db_session.add(
            EntityOrm(
                entity=1004,
                prefix="local-authority-district",
                reference="LAD004",
                dataset="local-authority-district",
            )
        )
        db_session.flush()

        result = get_entity_by_curie(
            session=db_session,
            prefix="local-authority-district",
            reference="different-ref",
        )

        assert result == []

    def test_limit_is_two(self, db_session):
        """Test that query limits results to 2 even when more duplicates exist"""
        for i in range(5):
            db_session.add(
                EntityOrm(
                    entity=2000 + i,
                    prefix="local-authority-district",
                    reference="LAD005",
                    dataset="local-authority-district",
                )
            )
        db_session.flush()

        result = get_entity_by_curie(
            session=db_session, prefix="local-authority-district", reference="LAD005"
        )

        assert len(result) == 2

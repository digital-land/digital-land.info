import logging
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from application.data_access.curie_queries import (
    get_lookup_by_curie,
    get_entity_by_curie,
)


class TestGetLookupByCurie:
    def test_returns_empty_list_when_no_lookup_found(self):
        """Test that empty list is returned when no entity matches the CURIE"""
        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        result = get_lookup_by_curie(
            session=mock_session, prefix="test-prefix", reference="test-reference"
        )
        assert result == []

    def test_returns_single_entity_id_when_one_lookup_found(self):
        """Test that a single entity ID is returned when one lookup matches"""
        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = [123]

        result = get_lookup_by_curie(
            session=mock_session, prefix="test-prefix", reference="test-reference"
        )

        assert result == [123]
        assert len(result) == 1

    def test_returns_multiple_entity_ids_when_duplicates_exist(self, caplog):
        """Test that multiple entity IDs are returned when duplicates exist"""
        caplog.set_level(logging.INFO, logger="application.data_access.curie_queries")

        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = [
            123,
            456,
        ]

        result = get_lookup_by_curie(mock_session, "test-prefix", "test-reference")

        assert result == [123, 456]
        assert len(result) == 2
        assert (
            "Lookup with CURIE 'test-prefix:test-reference' is a duplicate"
            in caplog.messages
        )


class TestGetEntityByCurie:
    def test_returns_empty_list_when_no_entity_found(self):
        """Test that empty list is returned when no entity matches the CURIE"""
        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        result = get_entity_by_curie(mock_session, "test-prefix", "test-reference")

        assert result == []

    def test_returns_single_entity_id_when_one_entity_found(self):
        """Test that a single entity ID is returned when one entity matches"""
        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = [789]

        result = get_entity_by_curie(mock_session, "test-prefix", "test-reference")

        assert result == [789]
        assert len(result) == 1

    def test_returns_multiple_entity_ids_when_duplicates_exist(self, caplog):
        """Test that multiple entity IDs are returned when duplicates exist"""
        caplog.set_level(logging.INFO, logger="application.data_access.curie_queries")

        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalars.return_value.all.return_value = [
            789,
            101,
        ]

        result = get_entity_by_curie(mock_session, "test-prefix", "test-reference")

        assert result == [789, 101]
        assert len(result) == 2
        assert (
            "Entity with CURIE 'test-prefix:test-reference' is a duplicate"
            in caplog.messages
        )

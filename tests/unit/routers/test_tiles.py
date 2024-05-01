from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from application.routers.tiles_ import (
    read_tiles_from_postgres,
    tile_is_valid,
    build_db_query,
    sql_to_pbf,
)

# Constants for Testing
VALID_TILE_INFO = {
    "x": 512,
    "y": 512,
    "zoom": 10,
    "format": "pbf",
    "dataset": "example-dataset",
}
INVALID_TILE_INFO = {
    "x": -1,
    "y": 512,
    "zoom": 10,
    "format": "jpg",
    "dataset": "example-dataset",
}


@pytest.fixture
def valid_tile():
    return VALID_TILE_INFO.copy()


@pytest.fixture
def invalid_tile():
    return INVALID_TILE_INFO.copy()


@pytest.fixture
def mock_build_db_query():
    with patch("application.routers.tiles_.build_db_query") as mock:
        yield mock


@pytest.fixture
def mock_sql_to_pbf():
    with patch("application.routers.tiles_.sql_to_pbf") as mock:
        mock.return_value = b"sample_pbf_data"
        yield mock


def test_tile_is_valid(valid_tile):
    assert tile_is_valid(valid_tile), "Tile should be valid with correct parameters"


def test_tile_is_invalid(invalid_tile):
    assert not tile_is_valid(
        invalid_tile
    ), "Tile should be invalid with incorrect parameters"


def test_build_db_query(valid_tile):
    query = build_db_query(valid_tile)
    assert (
        "SELECT" in query and "FROM" in query
    ), "SQL query should be properly formed with SELECT and FROM clauses"


@patch("application.routers.tiles_.psycopg2.connect")
def test_sql_to_pbf(mock_connect, valid_tile):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = [b"test_pbf_data"]

    sql = build_db_query(valid_tile)
    pbf_data = sql_to_pbf(sql)

    assert pbf_data == b"test_pbf_data", "Should return binary PBF data"
    mock_cursor.execute.assert_called_with(sql)
    mock_cursor.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_read_tiles_from_postgres_invalid_tile(invalid_tile):
    with pytest.raises(HTTPException) as excinfo:
        await read_tiles_from_postgres(
            invalid_tile["dataset"],
            invalid_tile["zoom"],
            invalid_tile["x"],
            invalid_tile["y"],
            invalid_tile["format"],
        )
    assert (
        excinfo.value.status_code == 400
    ), "Should raise HTTP 400 for invalid tile parameters"


@pytest.mark.asyncio
async def test_read_tiles_from_postgres_valid_tile(
    mock_build_db_query, mock_sql_to_pbf, valid_tile
):
    mock_build_db_query.return_value = "SELECT * FROM tiles"
    response = await read_tiles_from_postgres(
        valid_tile["dataset"],
        valid_tile["zoom"],
        valid_tile["x"],
        valid_tile["y"],
        valid_tile["format"],
    )

    assert isinstance(response, StreamingResponse), "Should return a StreamingResponse"
    assert (
        response.status_code == 200
    ), "Response status should be 200 for valid requests"
    mock_build_db_query.assert_called_once_with(valid_tile)
    mock_sql_to_pbf.assert_called_once_with("SELECT * FROM tiles")

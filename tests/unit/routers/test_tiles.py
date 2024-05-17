# import pytest
# from unittest.mock import patch, AsyncMock
# from fastapi import HTTPException
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from sqlalchemy.future import select

# from application.routers.tiles import read_tiles_from_postgres, tile_is_valid
# from application.db.models import EntityOrm
# from application.db.session import get_session

# # Constants for Testing
# VALID_TILE_INFO = {
#     "x": 512,
#     "y": 512,
#     "zoom": 10,
#     "format": "pbf",
#     "dataset": "example-dataset",
# }
# INVALID_TILE_INFO = {
#     "x": -1,
#     "y": 512,
#     "zoom": 10,
#     "format": "jpg",
#     "dataset": "example-dataset",
# }


# @pytest.fixture
# def valid_tile():
#     return VALID_TILE_INFO.copy()


# @pytest.fixture
# def invalid_tile():
#     return INVALID_TILE_INFO.copy()


# @pytest.fixture
# def mock_session_maker():
#     with patch("db.session._get_fastapi_sessionmaker") as mock:
#         mock.return_value = AsyncMock(get_db=AsyncMock())
#         yield mock


# def test_tile_is_valid(valid_tile):
#     assert tile_is_valid(valid_tile), "Tile should be valid with correct parameters"


# def test_tile_is_invalid(invalid_tile):
#     assert not tile_is_valid(
#         invalid_tile
#     ), "Tile should be invalid with incorrect parameters"


# @pytest.mark.asyncio
# @patch("application.routers.tiles.build_db_query", return_value=b"sample_pbf_data")
# async def test_read_tiles_from_postgres_valid_tile(
#     mock_build_db_query, valid_tile, mock_session_maker
# ):
#     session = (
#         mock_session_maker.return_value.get_db.return_value.__aenter__.return_value
#     )
#     response = await read_tiles_from_postgres(
#         valid_tile["dataset"],
#         valid_tile["zoom"],
#         valid_tile["x"],
#         valid_tile["y"],
#         valid_tile["format"],
#         session,
#     )

#     assert isinstance(response, StreamingResponse), "Should return a StreamingResponse"
#     assert (
#         response.status_code == 200
#     ), "Response status should be 200 for valid requests"
#     mock_build_db_query.assert_called_once_with(valid_tile, session)


# @pytest.mark.asyncio
# async def test_read_tiles_from_postgres_invalid_tile(invalid_tile, mock_session_maker):
#     session = (
#         mock_session_maker.return_value.get_db.return_value.__aenter__.return_value
#     )
#     with pytest.raises(HTTPException) as excinfo:
#         await read_tiles_from_postgres(
#             invalid_tile["dataset"],
#             invalid_tile["zoom"],
#             invalid_tile["x"],
#             invalid_tile["y"],
#             invalid_tile["format"],
#             session,
#         )
#     assert (
#         excinfo.value.status_code == 400
#     ), "Should raise HTTP 400 for invalid tile parameters"

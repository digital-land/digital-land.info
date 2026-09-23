import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import application.db.session as session


def _read_engine(create_db, mocker, timeout_ms):
    settings = mocker.Mock(
        READ_DATABASE_URL=create_db,
        DB_POOL_SIZE=1,
        DB_POOL_MAX_OVERFLOW=0,
        DB_STATEMENT_TIMEOUT_MS=timeout_ms,
        ENVIRONMENT="test",
    )
    mocker.patch.object(session, "get_settings", return_value=settings)
    return session._create_engine()


def test_read_engine_connections_carry_the_timeout(create_db, mocker):
    engine = _read_engine(create_db, mocker, 4321)
    try:
        with engine.connect() as conn:
            # 4321 is deliberately not a round number - Postgres normalises
            # 120000 to '2min', which makes the assertion indirect.
            assert conn.execute(text("show statement_timeout")).scalar() == "4321ms"
            assert (
                conn.execute(text("show application_name")).scalar()
                == "digital-land.info-test"
            )
    finally:
        engine.dispose()


def test_read_engine_cancels_a_query_that_exceeds_the_timeout(create_db, mocker):
    engine = _read_engine(create_db, mocker, 250)
    try:
        with engine.connect() as conn:
            with pytest.raises(OperationalError, match="statement timeout"):
                conn.execute(text("select pg_sleep(5)"))
    finally:
        engine.dispose()

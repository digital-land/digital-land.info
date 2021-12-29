def test_entity(db_session):
    from dl_web.db.models import Entity

    entities = db_session.query(Entity).all()
    assert len(entities) == 0

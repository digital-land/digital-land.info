def test_entity(db_session):
    from application.db.models import Entity

    entities = db_session.query(Entity).all()
    assert len(entities) == 0

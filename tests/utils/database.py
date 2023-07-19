from application.db.models import EntityOrm, DatasetOrm, TypologyOrm
from application.db.session import get_session
from tests.test_data import datasets, entities


def add_entity_to_database(entity: EntityOrm):
    session = next(get_session())
    session.add(entity)
    session.commit()
    return entity


def add_entities_to_database(entities: list[EntityOrm]):
    session = next(get_session())
    for entity in entities:
        session.add(EntityOrm(**entity))
    session.commit()
    return entities


# this function adds the base entities to the database
def add_base_entities_to_database():
    session = next(get_session())
    for entity in entities:
        session.add(EntityOrm(**entity))
    session.commit()


# this function adds the base datasets to the database
def add_base_datasets_to_database():
    session = next(get_session())
    for dataset in datasets:
        session.add(DatasetOrm(**dataset))
    session.commit()


# this function adds the base typology to the database
def add_base_typology_to_database():
    session = next(get_session())
    typologies = [
        {
            "typology": "geography",
            "name": "geography",
            "description": "This is an example typology.",
            "entry_date": "2022-01-01",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "plural": "Example Typologies",
            "text": "This is some example text.",
            "wikidata": "Q12345",
            "wikipedia": "en:Example_Typology",
        },
        {
            "typology": "organisation",
            "name": "organisation",
            "description": "This is an example typology.",
            "entry_date": "2022-01-01",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "plural": "Example Typologies",
            "text": "This is some example text.",
            "wikidata": "Q12345",
            "wikipedia": "en:Example_Typology",
        },
    ]
    for typology in typologies:
        session.add(TypologyOrm(**typology))
    session.commit()


# a function to reset the database
def reset_database():
    session = next(get_session())
    session.query(EntityOrm).delete()
    session.query(DatasetOrm).delete()
    session.query(TypologyOrm).delete()
    session.commit()


# a function to fetch an entity from the database
def fetch_entity_from_database(entity_id):
    session = next(get_session())
    return session.query(EntityOrm).filter(EntityOrm.entity == entity_id).first()

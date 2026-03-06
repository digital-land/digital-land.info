#!/usr/bin/env bash

docker-compose exec web python -c "
from application.db.models import DatasetOrm, EntityOrm, OrganisationOrm
from application.db.session import get_session
from tests.test_data import datasets, entities, organisations

session = next(get_session())
for dataset in datasets:
    themes = dataset.pop('themes')
    session.add(DatasetOrm(**dataset, themes=themes.split(',')))
for entity in entities:
    session.add(EntityOrm(**entity))
for organisation in organisations:
    session.add(OrganisationOrm(**organisation))
session.commit()
"

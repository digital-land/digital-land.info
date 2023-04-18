#!/usr/bin/env bash

docker-compose exec web python -c "
from application.db.models import DatasetOrm, EntityOrm
from application.db.session import get_session
from tests.test_data import datasets, entities

session = next(get_session())
for dataset in datasets:
    themes = dataset.pop('themes')
    session.add(DatasetOrm(**dataset, themes=themes.split(',')))
for entity in entities:
    session.add(EntityOrm(**entity))
session.commit()
"

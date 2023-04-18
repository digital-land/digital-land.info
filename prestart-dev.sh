#!/bin/bash

while [[ ! cat < /dev/tcp/db/5432 ]]; do
    sleep 1;
done

python -m alembic upgrade head

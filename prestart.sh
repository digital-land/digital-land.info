#!/bin/sh

# TODO - move this into a script that locks on dynamodb table for e.g. so only
# one app in cluster will apply migrations on startup, subsequent apps can call this but
# it will be no-op.

echo "Trying to execute alembic upgrade head"
python -m alembic upgrade head
echo "Finished executing alembic upgrade head"

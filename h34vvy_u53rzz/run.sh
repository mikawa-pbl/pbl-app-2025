#!/bin/sh

set -e

uv run python manage.py makemigrations
uv run python manage.py migrate --database=h34vvy_u53rzz
uv run python manage.py runserver

#!/bin/sh

set -e

uv run manage.py makemigrations h34vvy_u53rzz
uv run manage.py migrate --database default
uv run manage.py migrate --database h34vvy_u53rzz
uv run manage.py runserver

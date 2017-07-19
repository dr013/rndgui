#!/usr/bin/env bash

source /Users/krukov/projects/rndgui/venv/bin/activate
celery beat -A rndgui -l info -S django
celery -A rndgui worker -l info

#!/bin/bash
gunicorn backend.app:app --workers 4 --bind 0.0.0.0:$PORT --timeout 600

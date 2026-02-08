#!/usr/bin/env bash
gunicorn core.wsgi:application
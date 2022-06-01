# script_base
api for users scripts

    c django нужно запускать celery
    все запускается от туда где manage.py

    celery -A scripts_base worker

    celery -A scripts_base flower script_base

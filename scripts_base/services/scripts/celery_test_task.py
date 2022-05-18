import datetime

from scripts_base.celery import app


@app.task
def my_task(value_str: str, value_int: int) -> dict:
    x = 10**value_int**5
    return {'str': value_str, 'int': x, 'time': datetime.datetime.now()}

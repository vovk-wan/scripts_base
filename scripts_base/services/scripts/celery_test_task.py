from scripts_base.celery import app


@app.task
def my_task(value_str: str, value_int:int) -> dict:
    return {'str': value_str, 'int': value_int}

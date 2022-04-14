from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


class Client(models.Model):
    name = models.CharField(max_length=30, verbose_name='name user')
    status = models.CharField(max_length=10, verbose_name='status user')  # BAN
    chat_user = models.CharField(max_length=10, verbose_name='Chat user')  # пользователи чата доступ ко всем серверам
    expiration_date = models.DateTimeField(blank=False, verbose_name='Expiration date')
    telegram_id = models.IntegerField(verbose_name='telegram id')
    description = models.TextField()

    class Meta:
        db_table = 'clients'


class License(models.Model):
    client = models.ForeignKey(Client, related_name='license', verbose_name='Client', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name='Name license')
    secret = models.CharField(max_length=100, verbose_name='Secret key')
    created = models.DateTimeField(auto_now=True, verbose_name='Created')
    expiration_date = models.DateTimeField(blank=False, verbose_name='Expiration date')

    class Meta:
        db_table = 'client_licenses'

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser


class Status(models.Model):
    name = models.CharField(max_length=10, verbose_name=_('User status'))  # BAN

    class Meta:
        db_table = 'client_status'


class Client(models.Model):
    # BAN
    name = models.CharField(max_length=50, verbose_name=_('name user'))
    telegram_id = models.IntegerField(verbose_name=_('telegram id'))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Client added'))
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    status = models.ForeignKey(
        Status,
        related_name='client',
        verbose_name=_('status user'),
        on_delete=models.CASCADE
    )
    # пользователи чата доступ ко всем серверам
    chat_user = models.BooleanField(default=False, verbose_name=_('Chat user'))
    expiration_date = models.DateTimeField(blank=False, verbose_name=_('Expiration date'))
    description = models.TextField(max_length='1500', verbose_name=_('Description'))

    class Meta:
        db_table = 'clients'
        ordering = ('expiration_date',)


class Script(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Script name'))
    description = models.TextField(max_length=1000, verbose_name=_('Description'))

    class Meta:
        db_table = 'scripts'


class License(models.Model):
    client = models.ForeignKey(
        Client,
        related_name='license',
        verbose_name=_('Client'),
        on_delete=models.CASCADE
    )
    script = models.ForeignKey(
        Script, related_name='license', verbose_name=_('Client'), on_delete=models.CASCADE)
    licence_key = models.CharField(max_length=100, verbose_name=_('Secret key'))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Created'))
    expiration_date = models.DateTimeField(blank=False, verbose_name=_('Expiration date'))

    class Meta:
        db_table = 'client_licenses'

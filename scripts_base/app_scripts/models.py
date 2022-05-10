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
    telegram_id = models.BigIntegerField(unique=True, verbose_name=_('telegram id'))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Client added'))
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    status = models.ForeignKey(
        Status,
        related_name='client',
        blank=True,
        null=True,
        default=None,
        verbose_name=_('status user'),
        on_delete=models.CASCADE
    )
    # пользователи чата доступ ко всем серверам
    chat_user = models.BooleanField(default=False, verbose_name=_('Chat user'))
    expiration_date = models.DateTimeField(blank=False, verbose_name=_('Expiration date'))
    description = models.TextField(default="", max_length='1500', verbose_name=_('Description'))

    class Meta:
        db_table = 'clients'
        ordering = ('expiration_date',)


class Product(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name=_('Script name'))
    description = models.TextField(max_length=1000, verbose_name=_('Description'))
    filename = models.CharField(max_length=1000, verbose_name=_('Description'))

    class Meta:
        db_table = 'products'


class LicenseKey(models.Model):
    client = models.ForeignKey(
        Client,
        related_name='licensekey',
        verbose_name=_('Client'),
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name='license', verbose_name=_('Client'), on_delete=models.CASCADE)
    license_key = models.CharField(unique=True, max_length=100, verbose_name=_('Secret key'))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Created'))
    expiration_date = models.DateTimeField(auto_now=True, blank=False, verbose_name=_('Expiration date'))

    class Meta:
        db_table = 'license_keys'

    @classmethod
    def check_license(cls, license_key):
        return bool(LicenseKey.objects.filter(license_key=license_key).count())


class LicenseStatus(models.Model):
    class Status(models.IntegerChoices):
        YES = 1
        NO = 0
        WAIT = -1
    licensekey = models.OneToOneField(
        LicenseKey,
        related_name='licensestatus',
        verbose_name=_('License key'),
        on_delete=models.CASCADE
    )
    status = models.IntegerField(default=-1, choices=Status.choices)
    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Created'))

    class Meta:
        db_table = 'licenses_status'

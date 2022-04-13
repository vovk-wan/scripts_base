from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=30, verbose_name='name user')
    login = models.CharField(max_length=30, verbose_name='name user')
    email_address = models.EmailField(verbose_name='name user')
    status = models.CharField(max_length=10, verbose_name='status user')

    class Meta:
        db_table = 'client'


class License(models.Model):
    client = models.ForeignKey(Client, related_name='license', verbose_name='Client', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name='Name license')
    secret = models.CharField(max_length=100, verbose_name='Secret key')
    created = models.DateTimeField(auto_now=True, verbose_name='Created')
    expiration_date = models.DateTimeField(blank=False, verbose_name='Expiration date')

    class Meta:
        db_table = 'clients_license'

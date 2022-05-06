import json

from django.shortcuts import render
import logging

from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.http import JsonResponse, Http404, HttpResponse

from app_scripts.models import License, Client
from app_scripts.scripts import BASE
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):

    def post(self, request, *args, **kwargs):
        print(request.POST)
        response = request.body.decode('utf-8')
        try:
            data = json.loads(response)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logging.info(exc)
            return 'Error decode', 400
        name = data.get('name')
        params = data.get('params')
        kw = data.get('kwargs')
        result = BASE(name, params, **kw)
        return JsonResponse(data=result)

    def get(self):
        return Http404('Error, this page not found')


class CheckLicenseView(View):
    def post(self, request, *args, **kwargs):
        response = request.body.decode('utf-8')
        try:
            data = json.loads(response)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logging.info(exc)
            return 'Error decode', 400
        secret = data.get('secret')
        lic = License.objects.get(secret=secret)
        if lic:
            return 'ok', 205
        return 'Error decode', 400


class RegistrationView(View):
    def post(self, request, *args, **kwargs):
        response = request.body.decode('utf-8')
        try:
            data = json.loads(response)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logging.info(exc)
            return 'Error decode', 400
        token = data.get('token')
        user_data = data.get('user')
        user_license = data.get('license')
        client = Client(**user_data)
        client.save()
        if not client:
            return 'error', 412
        client_license = License(client=client, **user_license)
        client_license.save()
        if not client_license:
            client.delete()
            return 'error', 415
        return 'ok', 200


class MyIpView(View):
    def get(self, request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR')
        return HttpResponse(ip)


class SecondaryMarketView(View):

    def post(self, request, *args, **kwargs):
        pass

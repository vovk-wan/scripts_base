import json

# from django.shortcuts import render
import logging

from django.views import View
from django.http import JsonResponse, Http404
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


class CheckLicense(View):
    pass


class Registration(View):
    def post(self,request, *args, **kwargs):
        pass
import json

from django.shortcuts import render
# import logging


from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.http import JsonResponse, Http404, HttpResponse, response

from app_scripts.models import License, Client
from app_scripts.scripts import BASE
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from services.service_license import LicenseChecker
from services.scripts.secondary_server import SecondaryManager

from config import logger

# Create your views here.


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):

    def post(self, request, *args, **kwargs):
        pass
    # print(request.POST)
        # response = request.body.decode('utf-8')
        # try:
        #     data = json.loads(response)
        # except (AttributeError, json.decoder.JSONDecodeError) as exc:
        #     logging.info(exc)
        #     return HttpResponse(b'Error request', response.
        # name = data.get('name')
        # params = data.get('params')
        # kw = data.get('kwargs')
        # result = BASE(name, params, **kw)
        # return JsonResponse(data=result)

    def get(self):
        return Http404('Error, this page not found')


@method_decorator(csrf_exempt, name='dispatch')
class CheckLicenseView(View):
    def post(self, request, *args, **kwargs):
        """
        Проверяет лицензию если есть записывает какой-то идентификатор запроса и отправляет
        пользователю запрос на подтверждение.
        :param request:
        :return:
        """
        request_data = request.body.decode('utf-8')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logger.info(exc)
            return HttpResponse('error', status=401)
        result_data: dict = LicenseChecker(**data).check_license()
        logger.info(f"Result_data: {result_data}")
        if result_data.get("success"):
            return JsonResponse(result_data, status=200)
        return JsonResponse(result_data, status=401)

        # response = request.body.decode('utf-8')
        # try:
        #     data = json.loads(response)
        # except (AttributeError, json.decoder.JSONDecodeError) as exc:
        #     logging.info(exc)
        #     return Http404'Error decode', 400
        # secret = data.get('secret')
        # lic = License.objects.get(secret=secret)
        # if lic:
        #     return 'ok', 205
        # return 'Error decode', 400


class RegistrationView(View):
    def post(self, request, *args, **kwargs):
        response = request.body.decode('utf-8')
        try:
            data = json.loads(response)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logger.error(exc)
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
        ip = get_client_ip(request)
        return HttpResponse(ip)


@method_decorator(csrf_exempt, name='dispatch')
class LicenseApproveView(View):
    def post(self, request, *args, **kwargs):
        # Проверять - подтвердили ли в телеграме запуск лизензии.
        result_data: dict = {"success": True}
        logger.info(f"Result_data: {result_data}")

        return JsonResponse(result_data, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SecondaryMarketView(View):
    def post(self, request, *args, **kwargs):
        request_data = request.body.decode('utf-8')
        logger.info(f' before json request_data {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as exc:
            logger.error(exc)
            return JsonResponse({'error': 'error'}, status=401)
        logger.info("start script")
        result_data: dict = SecondaryManager(**data).main()
        logger.info(f"Result_data: {result_data}")

        if result_data.get("success"):
            return JsonResponse(result_data, status=200)
        return JsonResponse(result_data, status=401)

    #
    # request_data = request.get_json()
    # result_data: dict = await SecondaryManager(**request_data).main()
    # logger.info(f"Result_data: {result_data}")
    # if result_data.get("success"):
    #     return make_response(result_data, 200)
    # return make_response(result_data, 401)

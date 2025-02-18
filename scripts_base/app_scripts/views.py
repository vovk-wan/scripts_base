import datetime
import json

import django.conf
import redis
from celery.bin.control import inspect as celery_inspect
from scripts_base.celery import app
from django.forms import model_to_dict
from django.views import View
# from django.views.generic.detail import SingleObjectMixin
from django.http import JsonResponse, Http404, HttpResponse

from app_scripts.models import LicenseKey, Client, Product, Status, LicenseStatus
# from app_scripts.scripts import BASE
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from scripts_base.settings import DB_KEY_VALIDATION
from services.service_license import LicenseChecker
from services.scripts.secondary_server import SecondaryManager, main
from datastructurepack import DataStructure

from config import logger

from services.scripts.celery_test_task import my_task

@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):

    def post(self, request, *args, **kwargs):
        pass
    # print(request.POST)
        # response = request.body.decode('utf-8')
        # try:
        #     data = json.loads(response)
        # except (AttributeError, json.decoder.JSONDecodeError) as err:
        #     logging.info(err)
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
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.info(f'{self.__class__.__qualname__} exception: {err}')
            return HttpResponse('JSON error', status=400)

        result_data: dict = LicenseChecker(**data).check_license()
        logger.info(f"{self.__class__.__qualname__}, Result_data: {result_data}")

        return JsonResponse(result_data, status=result_data.get('status'))


class RegistrationView(View):
    def post(self, request, *args, **kwargs):
        response = request.body.decode('utf-8')
        try:
            data = json.loads(response)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.info(f'{self.__class__.__qualname__} exception: {err}')
            return 'Error decode', 400
        token = data.get('token')
        user_data = data.get('user')
        user_license = data.get('license')
        client = Client(**user_data)
        client.save()
        if not client:
            return 'error', 412
        client_license = LicenseKey(client=client, **user_license)
        client_license.save()
        if not client_license:
            client.delete()
            return 'error', 415
        return 'ok', 200


class MyIpView(View):
    def get(self, request, *args, **kwargs):
        ip = request.headers.get('X_FORWARDED_FOR', 'NO ADDRESS, ').split(',')[0]
        return HttpResponse(ip)


@method_decorator(csrf_exempt, name='dispatch')
class LicenseApproveView(View):
    def post(self, request, *args, **kwargs):
        result: DataStructure = DataStructure()
        # Проверять - подтвердили ли в телеграме запуск лизензии.
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=result.status)
        result.status = 401
        result.success = False
        license_key_secret = data.get('license_key')
        license_key: LicenseKey = LicenseKey.objects.filter(license_key=license_key_secret).first()
        check_status_id: int = data.get('check_status_id')
        license_status: LicenseStatus = LicenseStatus.objects.filter(licensekey=license_key).filter(id=check_status_id).first()
        if license_status:
            # TODO присылать данные result_data?
            result.success = True if license_status.status == 1 else False
            result.status = 200 if license_status.status == 1 else 401
            result.message = '' if license_status.status == 1 else 'Access denied'
        logger.info(f"{self.__class__.__qualname__}, Result: {result}")

        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class AddLicenseKeyView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__}, token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=401)

        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=result.status)

        product_id = data.get('product_id')
        # FIXME частично перенести в бизнес
        client = Client.objects.filter(telegram_id=data.get('telegram_id')).first()
        client_created = False
        if not client:
            client_data = ({
                    'name': data.get('telegram_id'),
                    'telegram_id': data.get('telegram_id'),
                    'expiration_date': datetime.datetime.now()
                }
            )
            client = Client.objects.create(**client_data)
            client_created = True
        product = Product.objects.filter(id=product_id).first()
        if client and product:
            license_key_created = False
            license_key = data.get('license_key')
            license_key_obj = LicenseKey.objects.filter(license_key=license_key).first()
            if not license_key_obj:
                license_data = {
                    'client': client, 'product': product, 'license_key': license_key}
                logger.info(f"{self.__class__.__qualname__}  product: {product}")

                license_key_obj = LicenseKey.objects.create(**license_data)
                license_key_created = True

            if license_key:
                license_key_data = model_to_dict(
                    license_key_obj, fields=[field.name for field in license_key_obj._meta.fields])  # data.to_dict()
                result.data = {'client_created': client_created, 'license_key': license_key_data}
                result.success = True
                result.status = 200
                if not license_key_created:
                    result.message = 'license alrtady exists'
                    result.status = 208
                return JsonResponse(result.as_dict(), status=result.status)
            if client_created:
                client.delete() # FIXME  возможно не удалит если не будет продукта важно или нет не ясно
        result.status = 400
        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class AddProductView(View):
    def post(self, request, *args, **kwargs):
        result: DataStructure = DataStructure()
        token = request.headers.get('token')
        # TODO снести секрет в ENV
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__} token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=401)

        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=result.status)
        product_name = data.get('name')
        product = Product.objects.filter(name=product_name).first()
        product_created = False
        if not product:
            product = Product.objects.create(**data)
            product_created = True
        logger.info(f"{self.__class__.__qualname__}  product: {product}")

        if product:
            product_data = model_to_dict(product, fields=[field.name for field in product._meta.fields])  # data.to_dict()
            result.data = product_data
            result.success = True
            result.status = 200
            if not product_created:
                result.message = 'product already exists'
                result.status = 208
            return JsonResponse(result.as_dict(), status=result.status)

        result.status = 400
        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class GetAllProductsView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__} token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=result.status)

        products = Product.objects.all()

        logger.info(f"{self.__class__.__qualname__}  product: {products}")

        if products:
            product_data = []
            for product in products:
                product_data.append(model_to_dict(product, fields=[field.name for field in
                                                          product._meta.fields]))  # data.to_dict()
            result.data = product_data
            result.success = True
            result.status = 200
            return JsonResponse(result.as_dict(), status=result.status)

        result.status = 400
        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmLicense(View):
    ## TODO тут данные согласовать
    ## TODO Уязвимость подмена id  запроса
    ## TODO нужно проверять телеграм id отправителя
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__} token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=401)
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=result.status)

        license_status_id = data.get('license_status_id')
        license_status: LicenseStatus = LicenseStatus.objects.filter(id=license_status_id).first()
        if license_status:
            license_status.status = 1
            # FIXME test
            result_data = license_status.save(force_update=True)
            # license_data = model_to_dict(product, fields=[field.name for field in product._meta.fields])  # data.to_dict()
            # result.data = product_data
            result.status = 200
            result.success = True
            return JsonResponse(result.as_dict(), status=result.status)

        result.status = 400
        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class NotConfirmLicense(View):
    def post(self, request, *args, **kwargs):
        result: DataStructure = DataStructure()
        token = request.headers.get('token')
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__} token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=result.status)
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 200
            return JsonResponse(result.as_dict(), status=result.status)

        license_status_id = data.get('license_status_id')
        count, result_data = LicenseStatus.objects.filter(id=license_status_id).delete()

        result.status = 400
        result.data = {'count': count, 'result': result_data}
        return JsonResponse(result.as_dict(), status=result.status)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteProductView(View):
    def post(self, request, *args, **kwargs):
        result: DataStructure = DataStructure()
        token = request.headers.get('token')
        if not token == DB_KEY_VALIDATION:
            logger.info(f'{self.__class__.__qualname__} token: {token}')
            result.status = 401
            result.message = 'Access is denied'
            return JsonResponse(result.as_dict(), status=401)

        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=result.status)

        product_id = data.get('product_id')
        deleted, count = Product.objects.filter(id=product_id).delete()
        result.status = 200 if deleted else 208
        result.message = '' if deleted else 'deletion error '
        result.data = {'deleted': deleted}
        return JsonResponse(result.as_dict(), status=result.status)


#  ********************** Secondary Market  *******************************

@method_decorator(csrf_exempt, name='dispatch')
class SecondaryMarketResponseView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__}, before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            result.message = str(err)
            logger.info(f'{self.__class__.__qualname__}, exception: {err}')
            return JsonResponse(result.as_dict(), status=result.status)

        logger.info(f'{self.__class__.__qualname__}, start script')

        result_data = main.delay(**data)
        logger.info(f'{self.__class__.__qualname__}, Result_data: {result_data.id}')

        result.success = True
        result.status = 200
        result.data = {'request_id': result_data.id}
        return JsonResponse(result.as_dict(), status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SecondaryMarketResultsView(View):
    """Попробуем получить информацию о процессе"""
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        request_data: str = request.body.decode('utf-8')
        try:
            data: dict = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            result.message = str(err)
            return JsonResponse(result.as_dict(), status=result.status)

        request_id: int = data.get('request_id')

        task = app.AsyncResult(request_id)
        if task.ready():
            answer = DataStructure()
            answer.status = 200
            answer.success = True
            task_data: list = task.get()
            # TODO делать возврат ошибок
            logger.info(f'Task data: {task_data}')
            answer.data = {'results': task_data} if task_data else {'results': []}
            return JsonResponse(answer.as_dict(), status=200)
        return JsonResponse({'value': 'wait'}, status=204)

#  ********************** Secondary Market END  *******************************


#  ********************** TEST CELERY *******************************


@method_decorator(csrf_exempt, name='dispatch')
class TestCeleryView(View):
    """отсылать не больше 16 -17 в инт, иначе ждать упаришся к примеру 17 примерно на минуту"""
    def post(self, request, *args, **kwargs):
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)
        value_str = data.get('value_str')
        value_int = data.get('value_int')
        answer = my_task.delay(value_str, value_int)
        # TODO  вернуть значение по ключу request_id в
        #  дате Dataclass по которому можно будет найти результат
        return JsonResponse({'time': datetime.datetime.now(), 'value_int': value_int, 'answer': answer.id}, status=200)

#  ********************** END TEST CELERY ****************************

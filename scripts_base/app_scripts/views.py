import datetime
import json

from django.forms import model_to_dict
from django.views import View
# from django.views.generic.detail import SingleObjectMixin
from django.http import JsonResponse, Http404, HttpResponse

from app_scripts.models import LicenseKey, Client, Product, Status, LicenseStatus
# from app_scripts.scripts import BASE
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from services.service_license import LicenseChecker
from services.scripts.secondary_server import SecondaryManager
from services.classes.dataclass import DataStructure

from config import logger


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
            return HttpResponse('error', status=401)
        # FIXME тут надо продолжать
        result_data: dict = LicenseChecker(**data).check_license()
        logger.info(f"{self.__class__.__qualname__}, Result_data: {result_data}")
        if result_data.get("success"):
            return JsonResponse(result_data, status=200)

        return JsonResponse(result_data, status=401)

        # response = request.body.decode('utf-8')
        # try:
        #     data = json.loads(response)
        # except (AttributeError, json.decoder.JSONDecodeError) as err:
        #     logging.info(err)
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
        ip = get_client_ip(request)
        return HttpResponse(ip)


@method_decorator(csrf_exempt, name='dispatch')
class LicenseApproveView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        # Проверять - подтвердили ли в телеграме запуск лизензии.
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=400)

        license_pk = data.get('license_pk')
        license_status: LicenseStatus = LicenseStatus.objects.filter(licensekey=license_pk).first()
        result_data: dict = {"success": False}
        status = 300
        if license_status:
            # TODO вопрос лучше присылать явно или удалять до?
            # TODO до было бы проще и реакция по сути та же самая
            # TODO статус тут вообще менять? какой когда ждем? какой когда пошел в ж?
            result_data: dict = {"success": True if license_status.status == 1 else None}
            status = 200 if license_status.status == 1 else 401

        logger.info(f"{self.__class__.__qualname__}, Result_data: {result_data}")

        return JsonResponse(result_data, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class SecondaryMarketView(View):
    def post(self, request, *args, **kwargs):
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__}, before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.info(f'{self.__class__.__qualname__}, exception: {err}')
            return JsonResponse({'error': 'error'}, status=401)
        logger.info(f'{self.__class__.__qualname__}, start script')
        result_data: dict = SecondaryManager(**data).main()
        logger.info(f'{self.__class__.__qualname__}, Result_data: {result_data}')

        if result_data.get("success"):
            return JsonResponse(result_data, status=200)
        return JsonResponse(result_data, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class AddLicenseKeyView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        logger.info(f'{self.__class__.__qualname__}, token: {token}')
        if not token == 'neyropcycoendocrinoimmunologia':
            result.status = 401
            return JsonResponse(result.as_dict(), status=401)

        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=400)

        product_pk = data.get('product_name')
        # FIXME  частично перенести в бизнес
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
        product = Product.objects.filter(id=product_pk).first()
        if client and product:
            data.update()
            license_data = {
                'client': client, 'product': product, 'license_key': data.get('license_key')}
            logger.info(f"{self.__class__.__qualname__}  product: {product}")
            license_key = LicenseKey.objects.create(**license_data)

            if license_key:
                license_key_data = model_to_dict(
                    license_key, fields=[field.name for field in license_key._meta.fields])  # data.to_dict()
                result.data = {'client_created': client_created, 'license_key': license_key_data}
                result.success = True
                return JsonResponse(result.as_dict(), status=200)
            if client_created:
                client.delete() # FIXME  возможно не удалит если не будет продукта важно или нет не ясно
        result.status = 400
        return JsonResponse(result.as_dict(), status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AddProductView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        logger.info(f'{self.__class__.__qualname__} token: {token}')
        if not token == 'neyropcycoendocrinoimmunologia':
            result.status = 401
            return JsonResponse(result.as_dict(), status=401)

        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=400)

        product = Product.objects.create(**data)
        logger.info(f"{self.__class__.__qualname__}  product: {product}")

        if product:
            product_data = model_to_dict(product, fields=[field.name for field in product._meta.fields])  # data.to_dict()
            result.data = product_data
            result.success = True
            return JsonResponse(result.as_dict(), status=200)

        result.status = 400
        return JsonResponse(result.as_dict(), status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GetAllProductsView(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        logger.info(f'{self.__class__.__qualname__} token: {token}')
        if not token == 'neyropcycoendocrinoimmunologia':
            result.status = 401
            return JsonResponse(result.as_dict(), status=401)

        products = Product.objects.all()

        logger.info(f"{self.__class__.__qualname__}  product: {products}")

        if products:
            product_data = []
            for product in products:
                product_data.append(model_to_dict(product, fields=[field.name for field in
                                                          product._meta.fields]))  # data.to_dict()
            result.data =  product_data
            result.success = True
            return JsonResponse(result.as_dict(), status=200)

        result.status = 400
        return JsonResponse(result.as_dict(), status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmLicense(View):
    def post(self, request, *args, **kwargs):
        result = DataStructure()
        token = request.headers.get('token')
        logger.info(f'{self.__class__.__qualname__} token: {token}')
        if not token == 'neyropcycoendocrinoimmunologia':
            result.status = 401
            return JsonResponse(result.as_dict(), status=401)
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=400)

        license_status_pk = data.get('license_status_pk')
        license_status: LicenseStatus = LicenseStatus.objects.filter(id=license_status_pk).first()
        if license_status:
            license_status.status = 1
            # FIXME test
            result_data = license_status.save(force_update=True)
            # license_data = model_to_dict(product, fields=[field.name for field in product._meta.fields])  # data.to_dict()
            # result.data = product_data
            result.success = True
            return JsonResponse(result.as_dict(), status=200)

        result.status = 400
        return JsonResponse(result.as_dict(), status=400)


@method_decorator(csrf_exempt, name='dispatch')
class NotConfirmLicense(View):
    def post(self, request, *args, **kwargs):
        result: DataStructure = DataStructure()
        token = request.headers.get('token')
        logger.info(f'{self.__class__.__qualname__} token: {token}')
        if not token == 'neyropcycoendocrinoimmunologia':
            result.status = 401
            return JsonResponse(result.as_dict(), status=401)
        request_data = request.body.decode('utf-8')
        logger.info(f'{self.__class__.__qualname__} before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logger.error(f'{self.__class__.__qualname__}, exception: {err}')
            result.status = 400
            return JsonResponse(result.as_dict(), status=400)

        license_status_pk = data.get('license_status_pk')
        count, result_data = LicenseStatus.objects.filter(id=license_status_pk).delete()


        result.status = 400
        result.data = {'count': count, 'result':result_data}
        return JsonResponse(result.as_dict(), status=400)

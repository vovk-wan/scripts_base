import json
import os
from typing import Union

import requests
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from app_scripts.models import LicenseStatus, LicenseKey

from services.classes.dataclass import DataStructure
from config import logger
from scripts_base.settings import DESKENT_TELEGRAM_ID, TELEBOT_TOKEN


class LicenseChecker:

    def __init__(self, license_key: str):
        self.license_key: str = license_key
        self.dataclass: 'DataStructure' = DataStructure()
        self.license_key_obj: Union[LicenseKey, None] = None

    def check_license(self) -> dict:
        """TODO нужны ли инстансы?"""
        telegram_id = self._get_telegram_id_if_license_exists()
        if not telegram_id:
            self.dataclass.status = 401
            self.dataclass.success = False
            self.dataclass.code = '401000'
            self.dataclass.message = "License code is not valid"
            self.dataclass.data = {}
            return self.dataclass.as_dict()

        # TODO сохранит сессию для запроса если лицензия есть
        # license_status = LicenseStatus.objects.filter(licensekey=self.license_key_obj).first()
        # if license_status:
        #     self.dataclass.status = 488
        #     self.dataclass.code = '488000'
        #     self.dataclass.message = "Data request for this license already exists"
        #     return self.dataclass.as_dict()
        license_status = LicenseStatus.objects.create(licensekey=self.license_key_obj)
        # TODO Для данного пользователя и лицензии поставить флаг "Ожидаю ответ"
        # TODO DBI ННАДДА!

        # TODO license_status штука 1разовый живет до ответа или по времени
        # TODO вполне подходит как идентификатор или сюда придется писать идентификатор сессии
        self._send_approve_message(telegram_id=telegram_id, license_status_id=license_status.id)
        # DB.set_check_in_progress(self.license_key)
        self.dataclass.success = True
        self.dataclass.status = 200
        self.dataclass.code = '000204'
        self.dataclass.message = "License checking in progress"
        # self.dataclass.work_key = work_key
        self.dataclass.data = {
            'check_status_id': license_status.id, 'check_status': license_status.status
        }

        return self.dataclass.as_dict()

    def _get_telegram_id_if_license_exists(self) -> int:
        """Проверяет есть ли лицензия в БД и возвращает телеграм_ид если лицензия есть"""
        # TODO Запрос в БД и получение оттуда телеграм_ид если лицензия есть
        # FIXME 1 действие упразднить функцию?
        try:
            self.license_key_obj = LicenseKey.objects.get(license_key=self.license_key)
        except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
            logger.info(f'{self.__class__.__qualname__} exception: {err}')
            return 0

        telegram_id: int = self.license_key_obj.client.telegram_id
        return telegram_id

    def _send_approve_message(self, telegram_id: int, license_status_id: int):
        """Отправляет сообщение в телеграм с кнопками Да и Нет"""

        keys = self._get_keyboard(license_status_id)
        text: str = f"Пришел запрос с вашим ключом {self.license_key}. Если его отправили вы - нажмите Да, иначе - Нет."
        url: str = f"https://api.telegram.org/bot{TELEBOT_TOKEN}/sendMessage?chat_id={telegram_id}&text={text}&reply_markup={keys}"
        response = requests.get(url)
        logger.debug(f"\nButtons sent."
                     f"\n\tAswer code: {response.status_code}"
                     f"\n\tTelegram_id: {telegram_id} "
                     f"\n\tLicense: {self.license_key}")
        return response.status_code

    def _get_keyboard(self, license_status_id) -> json:
        """Возвращает инлайн-клавиатуру телеграма в виде словаря с pk запроса на активацию скрипта"""

        data: dict = {"inline_keyboard": [[
            {"text": "Да", "callback_data": f"confirmed_{license_status_id}"},
            {"text": "Нет", "callback_data": f"not_confirmed_{license_status_id}"}
        ]]}
        return json.dumps(data)

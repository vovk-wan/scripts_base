import os

import requests
# from dotenv import load_dotenv

from services.classes.dataclass import DataStructure
from config import logger

# load_dotenv()

DESKENT_TEST_BOT = os.getenv("TELEBOT_TOKEN")
DESKENT_TELEGRAM_ID = os.getenv("DESKENT_TELEGRAM_ID")


class LicenseChecker:

    def __init__(self, license_key: str):
        self.license_key: str = license_key
        self.dataclass: 'DataStructure' = DataStructure()

    def check_license(self) -> dict:
        telegram_id: int = self._get_telegram_id_if_license_exists()
        if not telegram_id:
            self.dataclass.status = 401
            self.dataclass.success = False
            self.dataclass.code = '401000'
            self.dataclass.message = "License code is not valid"
            self.dataclass.data = {}
            return self.dataclass.as_dict()

        # TODO сгенерирует и запишет в базу к этой лицензии какой то временный ключ
        # TODO и записать его в редис
        # work_key: str = ""
        # self._send_approve_message(telegram_id)
        # TODO Для данного пользователя и лицензии поставить флаг "Ожидаю ответ"
        # DB.set_check_in_progress(self.license_key)
        self.dataclass.success = True
        self.dataclass.code = '000204'
        self.dataclass.message = "License checking in progress"
        # self.dataclass.work_key = work_key
        self.dataclass.data = {}

        return self.dataclass.as_dict()

    def _get_telegram_id_if_license_exists(self) -> int:
        """Проверяет есть ли лицензия в БД и возвращает телеграм_ид если лицензия есть"""
        # TODO Запрос в БД и получение оттуда телеграм_ид если лицензия есть

        if self.license_key != "12345":
            return 0
        # telegram_id: int = DB.get_telegram_id(license_key)
        telegram_id: int = int(DESKENT_TELEGRAM_ID)
        return telegram_id

    def _send_approve_message(self, telegram_id: int):
        """Отправляет сообщение в телеграм с кнопками Да и Нет"""

        keys = self._get_keyboard()
        text: str = f"Пришел запрос с вашим ключом {self.license_key}. Если его отправили вы - нажмите Да, иначе - Нет."
        url: str = f"https://api.telegram.org/bot{DESKENT_TEST_BOT}/sendMessage?chat_id={telegram_id}&text={text}&reply_markup={keys}"
        response = requests.get(url)
        logger.debug(f"\nButtons sent."
                     f"\n\tAswer code: {response.status_code}"
                     f"\n\tTelegram_id: {telegram_id} "
                     f"\n\tLicense: {self.license_key}")
        return response.status_code

    def _get_keyboard(self) -> dict:
        """Возвращает инлайн-клавиатуру телеграма в виде словаря с данными о лицензии"""

        # TODO сделать запрос в БД и получить оттуда pk лицензии по ее значению (license_key)
        # license_pk: int = DB.get_license_pk(self.license_key)
        license_pk: int = 1
        data: dict = {"inline_keyboard": [[
            {"text": "Да", "callback_data": f"yes_{license_pk}"},
            {"text": "Нет", "callback_data": f"no_{license_pk}"}
        ]]}
        return data
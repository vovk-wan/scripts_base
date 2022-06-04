"""Код для работы с secondary auctionator bot client"""

import os
import json
import asyncio
import datetime
from dataclasses import dataclass
from typing import List

import aiohttp

from scripts_base.celery import app

from config import logger


try:
    from aioscheduler_deskent import Scheduler
except Exception:
    logger.error("aioscheduler_deskent not found and will be installed")
    os.system('python3 -m pip install aioscheduler-deskent --upgrade')
    logger.success("aioscheduler_deskent installed")
    from aioscheduler_deskent import Scheduler

try:
    from datastructurepack import DataStructure
except Exception:
    logger.error("datastructurepack not found and will be installed")
    os.system('python3 -m pip install datastructurepack-deskent --upgrade')
    logger.success("datastructurepack installed")
    from datastructurepack import DataStructure


@dataclass
class SecondaryServer:
    product_data: dict
    headers: dict
    requests_count: int
    proxy_login: str
    proxy_password: str
    currency: str
    request_id: str = None
    cashier_id: str = None
    quotation_id: str = None

    def __post_init__(self: 'SecondaryServer') -> None:
        """Инициализация данных класса"""

        self.product_id: int = self.product_data.get("productId", 0)
        self.proxy: str = self.product_data.pop("proxy")
        self.request_params: dict = {"ssl": False}
        self.terms_accepted: bool = False
        if self.proxy:
            self.request_params.update(
                proxy=f"http://{self.proxy_login}:{self.proxy_password}@{self.proxy}/")

    @logger.catch
    async def init_and_pay(self: 'SecondaryServer', session) -> list:
        """Отправка запросов, получение данных"""

        logger.info("Getting tasks for init_and_pay...")
        url: str = 'https://www.binance.com/bapi/pay/v1/private/binance-pay/payment/order/init-and-pay'
        if self.requests_count > 500:
            self.requests_count = 500
        request_params: dict = self.request_params.copy()
        data = {
                "quotationId": self.quotation_id,
                "currency": self.currency
            }
        request_params.update({
            "url": url,
            "data": json.dumps(data)
        })
        return [asyncio.create_task(session.post(**request_params))
                for _ in range(self.requests_count)]

    @logger.catch
    async def __send_request(self: 'SecondaryServer', url: str, data: dict) -> dict:

        request_params: dict = self.request_params.copy()
        request_params.update({
            "url": url,
            "data": json.dumps(data)
        })
        async with aiohttp.ClientSession(headers=self.headers) as session:
            logger.debug(f"\n\tRequest with params: \n{request_params}\n")
            try:
                async with session.post(**request_params) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"Request error: {response.status}: {await response.text()}")
            except Exception as err:
                logger.error(err)
        return {}

    @logger.catch
    async def _get_preorder_create(self: 'SecondaryServer') -> bool:

        logger.debug("Preorder create start:")
        url: str = 'https://www.binance.com/bapi/nft/v1/private/nft/nft-trade/preorder-create'
        data: dict = {"productId": self.product_id}
        await self._common_request(url, data)
        if not self.cashier_id:
            logger.info("No cashier_id")
            return False
        return True

    @logger.catch
    async def _get_verification_two_check_list(self: 'SecondaryServer') -> bool:

        logger.debug("VerificationTwoCheckList start:")
        url = "https://www.binance.com/bapi/accounts/v1/protect/account/getVerificationTwoCheckList"
        data: dict = {"bizScene": "BINANCEPAY_CHALLENGE_PAY_RISK"}

        return await self._common_request(url, data)

    @logger.catch
    async def _get_init_account(self: 'SecondaryServer') -> bool:

        logger.debug("get_cashier_info start:")
        url = "https://www.binance.com/bapi/pay/v1/private/binance-pay/account/init-account"
        data: dict = {"touVersion": 1}

        return await self._common_request(url, data)

    @logger.catch
    async def _get_cashier_info(self: 'SecondaryServer') -> bool:

        logger.debug("get_cashier_info start:")
        url = "https://www.binance.com/bapi/pay/v1/private/binance-pay/payment/order/getCashierInfo"
        data: dict = {"cashierId": self.cashier_id, "terminalType": "web"}
        await self._common_request(url, data)
        if not self.quotation_id:
            logger.info("No quotation_id")
            return False
        return True

    @logger.catch
    async def get_preorder_confirm(self: 'SecondaryServer') -> bool:

        logger.debug("get_preorder_confirm start:")
        url = "https://www.binance.com/bapi/nft/v1/private/nft/nft-trade/preorder-confirm"
        if not self.product_id:
            logger.info("No product_id")
            return False
        if not self.request_id:
            logger.info("No request_id")
            return False
        data = {"productId": self.product_id, "requestId": self.request_id}

        return await self._common_request(url, data)

    async def is_data_prepared(self) -> bool:
        if await self._get_preorder_create():
            if await self._get_verification_two_check_list():
                if await self._get_init_account():
                    if await self._get_cashier_info():
                        logger.debug(
                            f"\n{self.request_id=}"
                            f"\n{self.cashier_id=}"
                            f"\n{self.quotation_id=}"
                        )
                        if all((self.quotation_id, self.cashier_id, self.request_id)):
                            return True
        return False

    async def _common_request(self, url: str, data: dict) -> bool:

        logger.debug("_common_request start:")
        response: dict = await self.__send_request(url=url, data=data)
        if not response:
            logger.warning(
                f"\nURL: {url}"
                f"\nData: {data}"
                f"\nResponse not found"
            )
            return False
        logger.debug(f"_common_request response: {response}")
        success: bool = response.get("success", False)
        if not success:
            logger.error(f"Request to url:\t[{url}]:\t[{success}]")
            return False
        response_data: dict = response.get("data", {})
        if response_data:
            request_id: str = response_data.get("orderNo", '')
            cashier_id: str = response_data.get("cashierId", '')
            quotation_id: str = response_data.get("payMethods", [{}])[0].get("quotationId", '')
            if request_id and cashier_id:
                self.request_id = request_id
                self.cashier_id = cashier_id
                logger.success(
                    f"Получен request_id: {self.request_id}"
                    f"\nПолучен cashier_id: {self.cashier_id}"
                )
            if quotation_id:
                self.quotation_id = quotation_id
                logger.success(f"Получен quotation_id: {self.quotation_id}")

        logger.success(f"Request to url:\t[{url}]:\t[{success}]")

        return success


@app.task
def main(**kwargs) -> dict:
    return asyncio.run(SecondaryManager(**kwargs)._main())


@dataclass
class SecondaryManager:
    headers: dict
    product_data: list[dict]
    requests_count: int
    proxy_login: str
    proxy_password: str
    sale_time: str
    currency: str
    workers: List[SecondaryServer] = None
    sale_datetime: datetime = None

    @logger.catch
    def main(self: 'SecondaryManager') -> dict:
        return asyncio.run(self._main())

    @logger.catch
    async def _main(self: 'SecondaryManager') -> dict:
        self.sale_datetime: datetime = datetime.datetime.fromisoformat(self.sale_time)
        logger.info(f"\n\t\tSale time:\t{self.sale_datetime}"
                    f"\n\t\tCurrent time:\t{datetime.datetime.utcnow()}"
                    f"\n\t\tDelta time:\t{(self.sale_datetime - datetime.datetime.utcnow()).seconds}"
        )

        result_data: 'DataStructure' = DataStructure()

        if not self.product_data:
            text: str = "Not enough data"
            logger.error(text)
            result_data.message = text
            result_data.data = {'results': []}
            return result_data.as_dict()

        workers: List[SecondaryServer] = await self._get_workers()
        self.workers: List[SecondaryServer] = await self._make_workers_data(workers)
        logger.debug(f"Total workers ready: {len(self.workers)}")
        if not self.workers:
            logger.error("No workers")
            result_data.success = True
            result_data.data = {'results': []}
            return result_data.as_dict()
        start_time: int = (self.sale_datetime - datetime.datetime.utcnow()).seconds
        logger.info(f"Scheduler starts. Tasks will be ran at: [{start_time}] seconds")
        results: list[str] = await Scheduler().add_job(self._do_purchase, self.sale_datetime).run()
        if results:
            logger.info(f"Results: {len(results)}")
        result_data.success = True
        result_data.data = {'results': results}

        return result_data.as_dict()

    @logger.catch
    async def _get_workers(self: 'SecondaryManager') -> list[SecondaryServer]:
        data: dict = {
            "headers": self.headers,
            "requests_count": self.requests_count,
            "proxy_login": self.proxy_login,
            "proxy_password": self.proxy_password,
            "currency": self.currency
        }
        return [
            SecondaryServer(product_data=product_data, **data)
            for product_data in self.product_data
        ]

    @logger.catch
    async def _make_workers_data(
            self: 'SecondaryManager', workers: list[SecondaryServer]) -> list[SecondaryServer]:
        return [worker for worker in workers if await worker.is_data_prepared()]

    @logger.catch
    async def _do_purchase(self: 'SecondaryManager') -> list[str]:
        """Отправка запросов, получение данных"""

        logger.info("Collecting requests. It will take a few seconds...")
        logger.info(f"Purchase time: {self.sale_datetime}"
                    f"\tCurrent time: {datetime.datetime.utcnow().replace(tzinfo=None)}")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = []
            for worker in self.workers:
                if await worker.get_preorder_confirm():
                    spam: list = await worker.init_and_pay(session)
                    tasks.extend(spam)
            logger.success(f"Total tasks: [{len(tasks)}]")
            t0 = datetime.datetime.utcnow().replace(tzinfo=None)
            logger.info(
                f"Requests started at: "
                f"{datetime.datetime.utcnow().replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')}")
            responses = await asyncio.gather(*tasks)
            logger.info(
                f"Total time for requests: {datetime.datetime.utcnow().replace(tzinfo=None) - t0}")
            results: list[str] = [await response.text() for response in responses]

        return results

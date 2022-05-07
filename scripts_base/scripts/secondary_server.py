import json
import time
import asyncio
import datetime
from typing import List

import aiohttp

from config import logger
from classes.dataclass import DataStructure


class SecondaryServer:

    def __init__(
            self: 'SecondaryServer',
            headers: dict,
            product_data: dict,
            requests_count: int,
            proxy_login: str,
            proxy_password: str,
    ) -> None:
        """Инициализация данных класса"""

        self.__HEADERS: dict = headers
        self.__PRODUCT_DATA: dict = product_data
        self.__PRODUCT: int = product_data.get("productId")
        self.__REQUESTS_COUNT: int = requests_count
        self.__PROXY: str = product_data.pop("proxy")
        self.__PROXY_LOGIN: str = proxy_login
        self.__PROXY_PASSWORD: str = proxy_password
        self.request_params: dict = {
            'ssl': False
        }
        if self.__PROXY:
            self.request_params.update(proxy=f"http://{self.__PROXY_LOGIN}:{self.__PROXY_PASSWORD}@{self.__PROXY}/")

    @logger.catch
    async def get_tasks(self: 'SecondaryServer', session) -> list:
        """Отправка запросов, получение данных"""

        logger.info("Getting tasks...")
        url: str = 'https://www.binance.com/bapi/nft/v1/private/nft/nft-trade/order-create'
        self.request_params.update(url=url)
        if self.__REQUESTS_COUNT > 500:
            self.__REQUESTS_COUNT = 500
        return [asyncio.create_task(session.post(**self.request_params)) for _ in range(self.__REQUESTS_COUNT)]

    @logger.catch
    async def __send_request(self: 'SecondaryServer', url: str, data: dict) -> dict:

        self.request_params.update(url=url)
        async with aiohttp.ClientSession(headers=self.__HEADERS) as session:
            if data:
                self.request_params.update(data=json.dumps(data))
            logger.debug(f"\n\tRequest with params: \n{self.request_params}\n")
            async with session.post(**self.request_params) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Request error: {response.status}: {await response.text()}")

    @logger.catch
    async def get_request_id(self: 'SecondaryServer') -> bool:

        logger.debug("get_request_id start:")
        url: str = 'https://www.binance.com/bapi/nft/v1/private/nft/nft-trade/preorder-create'
        data: dict = {"productId": self.__PRODUCT}
        response: dict = await self.__send_request(url=url, data=data)
        logger.debug(f"get_request_id response: {response}")
        if not response:
            return False
        request_id: str = response.get("data", {}).get("orderNo")
        logger.debug(f"Получен request_id: {request_id}")
        self.__PRODUCT_DATA.update(requestId=request_id)
        return True

    @logger.catch
    async def check_risk(self: 'SecondaryServer') -> bool:

        logger.debug("check_risk start:")
        url = "https://www.binance.com/bapi/nft/v1/private/nft/nft-trade/checkrisk"
        data: dict = self.__PRODUCT_DATA
        response: dict = await self.__send_request(url=url, data=data)
        logger.debug(f"check_risk response: {response}")
        success: bool = response.get("success")
        logger.debug(f"Получен success: {success}")

        return success


class SecondaryManager:

    def __init__(
            self: 'SecondaryManager',
            headers: dict,
            product_data: list[dict],
            requests_count: int,
            proxy_login: str,
            proxy_password: str,
            sale_time: float,
    ) -> None:
        """Инициализация данных класса"""
        self.__HEADERS: dict = headers
        self.__PRODUCT_DATA: list[dict] = product_data
        self.__REQUESTS_COUNT: int = requests_count
        self.__PROXY_LOGIN: str = proxy_login
        self.__PROXY_PASSWORD: str = proxy_password
        self.sale_time: float = sale_time

    @logger.catch
    def main(self: 'SecondaryManager') -> dict:
        return asyncio.run(self._main())

    @logger.catch
    async def _main(self: 'SecondaryManager') -> dict:

        result_data: 'DataStructure' = DataStructure()

        if not self.__PRODUCT_DATA:
            logger.error("Not enough data")
            result_data.code = 401001
            result_data.message = "Not enough data"
            result_data.data = {'results': []}
            return result_data.as_dict()
        workers: List[SecondaryServer] = await self._get_workers()
        workers: List[SecondaryServer] = await self._make_workers_data(workers)
        current_time = time.time()
        while self.sale_time > current_time:
            current_time = time.time()
        # results: list[str] = await self._do_purchase(workers=workers)
        lenght = len(workers)
        results = [json.dumps({key: value}) for key in range(lenght) for value in range(lenght, lenght * 2)]
        result_data.success = True
        result_data.data = {'results': results}

        return result_data.as_dict()

    @logger.catch
    async def _get_workers(self: 'SecondaryManager') -> list[SecondaryServer]:
        return [
            SecondaryServer(
                headers=self.__HEADERS, product_data=product, requests_count=self.__REQUESTS_COUNT,
                proxy_login=self.__PROXY_LOGIN, proxy_password=self.__PROXY_PASSWORD,
            )
            for product in self.__PRODUCT_DATA
        ]

    @logger.catch
    async def _make_workers_data(self: 'SecondaryManager', workers: list[SecondaryServer]) -> list[SecondaryServer]:
        for worker in workers:
            if not await worker.get_request_id():
                continue
            await worker.check_risk()
        return workers

    @logger.catch
    async def _do_purchase(self: 'SecondaryManager', workers: List['SecondaryServer']) -> list[str]:
        """Отправка запросов, получение данных"""

        logger.info("Collecting requests. It will take a few seconds...")
        async with aiohttp.ClientSession(headers=self.__HEADERS) as session:
            tasks: list = [await worker.get_tasks(session) for worker in workers]
            t0 = datetime.datetime.now()
            logger.info(f"Requests started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            responses = await asyncio.gather(*tasks)
            logger.info(f"Total time for requests: {datetime.datetime.now() - t0}")
            results: list[str] = [await response.text() for response in responses]
        return results

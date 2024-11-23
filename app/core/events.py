import asyncio
from typing import Callable

from loguru import logger
from fastapi import FastAPI

from app.db.sql import mysql_connector
from app.services.data import DataService


async def clear_table_data():
    await asyncio.sleep(10)
    while True:
        await DataService().delete_old_delivered_records()
        await asyncio.sleep(600)


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await mysql_connector.connect_to_mysql()
        # asyncio.create_task(clear_table_data())

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    @logger.catch()
    async def stop_app() -> None:
        if mysql_connector.connection:
            mysql_connector.connection.close()

    return stop_app

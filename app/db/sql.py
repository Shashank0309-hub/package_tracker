import mysql.connector

from app.core.config import MySQLEnv


class MysqlConnector:
    def __init__(self):
        self.connection = None

    async def connect_to_mysql(self) -> None:
        self.connection = mysql.connector.connect(
            host=MySQLEnv.HOST,
            user=MySQLEnv.USER,
            password=MySQLEnv.PASSWORD,
            database=MySQLEnv.DATABASE,
        )


mysql_connector = MysqlConnector()

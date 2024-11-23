import pandas as pd

from app.db.sql import mysql_connector
from app.schemas.data import DatabaseName, TableNames
from app.services.tracker import TrackerService


class DashboardService:
    def __init__(self):
        self.connector = mysql_connector.connection
        self.cursor = self.connector.cursor()

    async def _fetch_data(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    async def get_dashboard_data_service(self):
        self.cursor.execute(f"USE {DatabaseName};")

        datas = {}
        for courier_partner, table in TableNames.items():
            query = f"SELECT * FROM {table};"

            try:
                rows = await self._fetch_data(query)
            except:
                continue

            df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])
            no_of_orders = len(df)

            status_value_counts = df["status"].value_counts().to_dict()

            rto = await TrackerService().get_rto_data_service(
                courier_partner=courier_partner,
            )

            payment_received = await TrackerService().get_payment_data_service(
                courier_partner=courier_partner,
                payment_received=True,
                page_limit=False,
            )

            datas[courier_partner] = {
                "no_of_orders": no_of_orders,
                "status_value_counts": dict(status_value_counts),
                "rto": len(rto),
                "payment_received": len(payment_received),
            }

        return datas

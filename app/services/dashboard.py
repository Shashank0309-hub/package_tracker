from typing import Optional

import mysql.connector
import pandas as pd
from fastapi import HTTPException

from app.db.query_builder import SqlQueries
from app.db.sql import mysql_connector
from app.schemas.dashboard import AdditionalDataTable, AdditionalDataReq
from app.schemas.data import DatabaseName, TableNames
from app.schemas.tracker import CourierPartnerName
from app.services.tracker import TrackerService

order_col = {
    CourierPartnerName.SHIPROCKET: "order_total",
    CourierPartnerName.DTDC: "amount_to_be_paid"
}


class DashboardService:
    def __init__(self):
        self.connector = mysql_connector.connection
        self.cursor = self.connector.cursor()

    async def _fetch_data(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    async def _execute_query(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    async def additional_data_table_checker(self):
        self.cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in self.cursor.fetchall()]

        if DatabaseName not in databases:
            self.cursor.execute(f"CREATE DATABASE {DatabaseName};")

        self.cursor.execute(f"USE {DatabaseName};")
        self.cursor.execute("SHOW TABLES;")
        tables = [db[0] for db in self.cursor.fetchall()]
        if AdditionalDataTable not in tables:
            self.cursor.execute(f"CREATE TABLE {AdditionalDataTable} ({SqlQueries().ADDITIONAL_DATA_COLS});")

    async def get_dashboard_data_service(self, selected_courier_partner: Optional[CourierPartnerName] = None):
        self.cursor.execute(f"USE {DatabaseName};")

        datas = {}
        for courier_partner, table in TableNames.items():
            if (selected_courier_partner is None) or (selected_courier_partner == courier_partner):
                query = f"SELECT * FROM {table};"

                try:
                    rows = await self._fetch_data(query)
                except:
                    continue

                df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])
                no_of_orders = len(df)

                status_counts = df["status"].value_counts()
                status_percentages = (status_counts / len(df)) * 100

                status_order_totals = df.groupby("status")[order_col[courier_partner]].sum()

                status_summary = [
                    {
                        "status": status,
                        "count": count,
                        "percent": round(status_percentages[status], 2),
                        "amount": status_order_totals[status]
                    }
                    for status, count in status_counts.items()
                ]

                rto = await TrackerService().get_rto_data_service(
                    courier_partner=courier_partner,
                )

                payment_received = df[df["payment_received"] == "YES"]
                remaining_payment = df[df["payment_received"] == "NO"]

                total_payment_received = None
                pending_payment = None

                if courier_partner in order_col:
                    total_payment_received = sum(list(payment_received[order_col[courier_partner]]))
                    pending_payment = sum(list(remaining_payment[order_col[courier_partner]]))

                datas[courier_partner] = {
                    "no_of_orders": no_of_orders,
                    "status_summary": status_summary,
                    "rto": len(rto),
                    "num_of_payment_received": len(payment_received),
                    "total_payment_received": total_payment_received,
                    "num_of_remaining_payment": len(remaining_payment),
                    "pending_payment": pending_payment,
                }

                try:
                    rows = await self._fetch_data(query=F"""SELECT * FROM {AdditionalDataTable}""")
                    df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])

                    df = df[df["courier_partner"] == courier_partner]
                    data = df.to_dict(orient="records")

                    datas[courier_partner] = {**datas[courier_partner], "additional_data": data}
                except:
                    pass

        return datas

    async def put_additional_data_service(
            self,
            request: AdditionalDataReq,
            courier_partner: Optional[CourierPartnerName] = None,
    ):
        await self.additional_data_table_checker()
        request.name = request.name.strip().title()

        if request.cost_per_order and courier_partner and (not request.total_cost):
            table_name = TableNames.get(courier_partner)
            rows = await self._fetch_data(query=F"""SELECT * FROM {table_name}""")
            df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])
            request.total_cost = len(df) * request.cost_per_order

        request.cost_per_order = round(request.cost_per_order, 3) if request.cost_per_order else request.cost_per_order
        request.total_cost = round(request.total_cost, 3) if request.total_cost else request.total_cost

        rows = await self._fetch_data(query=F"""SELECT * FROM {AdditionalDataTable}""")
        df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])

        if (not len(df)) or (request.name not in list(df["name"])):
            query = await SqlQueries().get_additional_data_query(table_name=AdditionalDataTable)
            values = (request.name, request.cost_per_order, request.operator, courier_partner, request.total_cost)
        else:
            query = await SqlQueries().update_additional_data_query(table_name=AdditionalDataTable)
            values = (request.cost_per_order, request.operator, request.total_cost, request.name, courier_partner)

        await self._execute_query(query=query, values=values)

        return "Added Successfully!"

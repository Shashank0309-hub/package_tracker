import re
from datetime import date, datetime, timedelta
from typing import Optional, Dict
import pandas as pd
import mysql.connector
from fastapi import HTTPException, UploadFile, File
from loguru import logger

from app.core.config import DAYS_FOR_DELETION
from app.core.utils import save_upload_file_tmp
from app.db.query_builder import SqlQueries
from app.db.sql import mysql_connector
from app.schemas.data import TableNames, DatabaseName

from app.schemas.tracker import CourierPartnerName

order_date_col = {
    CourierPartnerName.SHIPROCKET: "shiprocket_created_at",
    CourierPartnerName.DTDC: "created_at",
    CourierPartnerName.SELLOSHIP: "order_date",
}


class DataService:
    def __init__(self):
        self.connector = mysql_connector.connection
        self.cursor = self.connector.cursor()

    def parse_date(self, date_str: str) -> date:
        normalized_date_str = re.sub(r'[-/.]', '-', date_str)
        try:
            return datetime.strptime(normalized_date_str, "%d-%m-%Y").date() if len(
                normalized_date_str.split('-')[2]) == 4 else datetime.strptime(normalized_date_str, "%d-%m-%y").date()
        except ValueError:
            raise ValueError(f"Date format not recognized: {date_str}")

    def table_checker(self, courier_partner):
        self.cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in self.cursor.fetchall()]

        if DatabaseName not in databases:
            self.cursor.execute(f"CREATE DATABASE {DatabaseName};")

        self.cursor.execute(f"USE {DatabaseName};")
        self.cursor.execute("SHOW TABLES;")
        tables = [db[0] for db in self.cursor.fetchall()]

        table_name = TableNames.get(courier_partner)
        if table_name and table_name not in tables:
            try:
                self.cursor.execute(f"CREATE TABLE {table_name} ({SqlQueries().TRACKER_DATA_COLS});")
            except:
                pass

        return table_name

    def check_missing_fields(self, **kwargs) -> Dict[str, bool]:
        return {field: value is None for field, value in kwargs.items()}

    def convert_to_type(self, value, expected_type):
        try:
            return int(value) if expected_type == 'int' else float(value) if expected_type == 'float' else str(value)
        except (ValueError, TypeError):
            return None

    def _check_order_exists(self, table_name, order_id: str) -> bool:
        query = f"SELECT COUNT(*) FROM {table_name} WHERE order_id = %s"
        self.cursor.execute(query, (order_id,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def _execute_insert(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    def _execute_update(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    def _execute_batch_insert(self, query, batch_values):
        try:
            self.cursor.executemany(query, batch_values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    async def put_data_service(
            self,
            courier_partner: CourierPartnerName,
            order_id: Optional[str] = None,
            consignment_id: Optional[str] = None,
            product_name: Optional[str] = None,
            customer_number: Optional[int] = None,
            customer_address: Optional[str] = None,
            customer_pincode: Optional[int] = None,
            product_price: Optional[float] = None,
            date: Optional[str] = None,
            status: Optional[str] = None,
            upload_file: Optional[UploadFile] = File(...),
    ):
        if upload_file:
            file_path = await save_upload_file_tmp(upload_file)
        else:
            missing_fields = self.check_missing_fields(
                order_id=order_id,
                consignment_id=consignment_id,
                product_name=product_name,
                customer_number=customer_number,
                customer_address=customer_address,
                customer_pincode=customer_pincode,
                product_price=product_price,
                date=date,
                status=status
            )
            missing_columns = [field for field, is_missing in missing_fields.items() if is_missing]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing columns: {', '.join(missing_columns)}"
                )

        table_name = self.table_checker(courier_partner)
        query_insert = SqlQueries().get_insert_tracker_data(table_name)
        query_update = SqlQueries().get_update_tracker_data(table_name)

        current_time = datetime.now()

        if not upload_file:
            values = (
                order_id,
                consignment_id,
                product_name,
                courier_partner.lower(),
                customer_number,
                customer_address,
                customer_pincode,
                product_price,
                self.parse_date(date),
                status.lower(),
                current_time,
            )

            if self._check_order_exists(table_name, order_id):
                update_values = values[1:] + (order_id,)
                self._execute_update(query_update, update_values)
            else:
                self._execute_insert(query_insert, values)
        else:
            tracker_uploaded_data = pd.read_csv(file_path)
            batch_values = []
            for _, row in tracker_uploaded_data.iterrows():
                customer_number = self.convert_to_type(row.get('customer_number'), 'int')
                product_price = self.convert_to_type(row.get('product_price'), 'float')
                if None in (customer_number, product_price, row.get('date')):
                    continue

                values = (
                    row.get('order_id'),
                    row.get('consignment_id'),
                    row.get('product_name'),
                    row.get('courier_partner', courier_partner).lower(),
                    customer_number,
                    row.get('customer_address'),
                    row.get('customer_pincode'),
                    product_price,
                    self.parse_date(row.get('date')),
                    row.get('status').lower(),
                    current_time,
                )

                if self._check_order_exists(table_name, row.get('order_id')):
                    update_values = values[1:] + (row.get('order_id'),)
                    self._execute_update(query_update, update_values)
                else:
                    batch_values.append(values)

            if batch_values:
                self._execute_batch_insert(query_insert, batch_values)

        return "Successfully dumped data !"

    async def delete_data_service(
            self,
            courier_partner,
            order_id,
            full_data,
    ):
        table_name = self.table_checker(courier_partner)

        if full_data:
            query = f"DROP TABLE {table_name}"
            values = ()
        elif order_id:
            query = f"DELETE FROM {table_name} WHERE order_id = %s"
            values = (order_id,)
        else:
            raise HTTPException(status_code=400, detail="Either order_id or consignment_id must be provided.")

        try:
            self.cursor.execute(query, values)
            self.connector.commit()
        except:
            return "Data doesn't exist!"

        return "Deleted Successfully!"

    async def get_data_service(
            self,
            courier_partner,
            order_id,
            status,
            page,
            limit,
            start_date,
            end_date,
    ):
        table_name = TableNames.get(courier_partner)

        if not table_name:
            raise HTTPException(status_code=400, detail="Invalid courier partner")

        self.cursor.execute(f"USE {DatabaseName};")

        self.cursor.execute(f"""SELECT count(*) FROM {table_name}""")
        total_count = self.cursor.fetchall()[0][0]

        data = {}
        try:
            conditions = [
                f"""
                {order_date_col[courier_partner]} >= "{start_date}" 
                AND {order_date_col[courier_partner]} <= "{end_date}"
                """
            ]
            if status:
                conditions.append(f"""status = "{status}" """)

            if order_id:
                conditions.append(f"""order_id = "{order_id}" """)

            condition = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            query = f"SELECT * FROM {table_name} {condition} ORDER BY updated_at LIMIT {limit} OFFSET {page * limit};"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            column_names = [i[0] for i in self.cursor.description]

            df = pd.DataFrame(rows, columns=column_names)

            data = df.to_dict(orient="records")
            return data, len(data) if len(data) < limit else total_count
        except Exception as err:
            logger.error(err)
            return data, len(data)

    async def delete_old_delivered_records(self):
        self.cursor.execute(f"USE {DatabaseName};")

        cutoff_date = datetime.now() - timedelta(days=DAYS_FOR_DELETION)

        tables = TableNames.values()
        deleted_count = 0

        for table_name in tables:
            query = f"""
            DELETE FROM {table_name}
            WHERE status = 'delivered' AND updated_at < %s
            """

            try:
                self.cursor.execute(query, (cutoff_date,))
                deleted_count += self.cursor.rowcount
                self.connector.commit()
            except mysql.connector.Error as err:
                raise HTTPException(status_code=500, detail=f"Database error: {err}")

    async def download_data_service(
            self,
            courier_partner,
            status,
            start_date,
            end_date,
    ):
        table_name = TableNames.get(courier_partner)

        self.cursor.execute(f"USE {DatabaseName};")
        query = f"SELECT * FROM {table_name}"

        conditions = [f"""
        {order_date_col[courier_partner]} >= "{start_date}" 
        AND {order_date_col[courier_partner]} <= "{end_date}"
        """]

        if status:
            conditions.append(f"""status = "{status}" """)

        condition = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"{query} {condition}"

        file_name = (f"{courier_partner}"
                     f"_{start_date.day}-{start_date.month}_{end_date.day}-{end_date.month}.csv")

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            column_names = [i[0] for i in self.cursor.description]

            df = pd.DataFrame(rows, columns=column_names)

            return df, file_name
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

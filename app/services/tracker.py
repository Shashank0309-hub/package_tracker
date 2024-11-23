import re
from datetime import datetime, date
from typing import List

import mysql.connector
import pandas as pd
from fastapi import HTTPException
from loguru import logger

from app.core.utils import save_upload_file_tmp
from app.db.query_builder import SqlQueries
from app.db.sql import mysql_connector
from app.schemas import Pagination
from app.schemas.data import TableNames, DatabaseName, PincodeSKUTable
from app.schemas.tracker import CourierPartnerName


class TrackerService:
    consignment_id_pattern = re.compile(r'[A-Z]\d{8,}')

    def __init__(self):
        self.connector = mysql_connector.connection
        self.cursor = self.connector.cursor()

    async def extract_consignment_id(self, file_path, partner):
        consignment_ids = []
        # with pdfplumber.open(file_path) as pdf:
        #     for page_num, page in enumerate(pdf.pages):
        #         text = page.extract_text()
        #         if text:
        #             lines = text.split('\n')
        #             for line in lines:
        #                 if partner == CourierPartnerName.DELHIVERY and line.isdigit() and len(line) == 14:
        #                     consignment_ids.append(line)
        #                     break
        #                 elif partner == CourierPartnerName.DTDC and len(line) == 9:
        #                     if self.consignment_id_pattern.search(line):
        #                         consignment_ids.append(line)
        #                         break
        return consignment_ids

    def get_data_by_consignment_ids(
            self,
            courier_partner,
            page: int,
            limit: int,
            consignment_ids: List[str],
            batch_size: int = 500
    ):
        all_results = []
        table_name = TableNames.get(courier_partner)

        self.cursor.execute(f"USE {DatabaseName};")
        self.cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = "{table_name}";
            """)
        column_names = [column[0] for column in self.cursor.fetchall()]

        offset = page * limit
        consignment_ids = consignment_ids[offset: offset + limit]

        for i in range(0, len(consignment_ids), batch_size):
            batch = consignment_ids[i:i + batch_size]
            format_strings = ', '.join(['%s'] * len(batch))
            query = f"""
            SELECT * FROM {table_name} 
            WHERE consignment_id IN ({format_strings})
            """

            try:
                self.cursor.execute(query, tuple(batch))
                rows = self.cursor.fetchall()

                for row in rows:
                    row_dict = dict(zip(column_names, row))
                    all_results.append(row_dict)
            except mysql.connector.Error as err:
                raise HTTPException(status_code=500, detail=f"Database error: {err}")

        return all_results

    # async def fetch_tracker_data_service(self, courier_partner, page, limit, upload_file):
    #     file_path = await save_upload_file_tmp(upload_file)
    #     consignment_ids = await self.extract_consignment_id(file_path, courier_partner)
    #     data = []
    #     total = len(consignment_ids)
    #
    #     if consignment_ids:
    #         logger.info(f"Fetched consignment ids for {courier_partner}")
    #         data = self.get_data_by_consignment_ids(courier_partner, page, limit, consignment_ids)
    #
    #     return data, total

    async def table_checker(self, courier_partner):
        self.cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in self.cursor.fetchall()]

        if DatabaseName not in databases:
            self.cursor.execute(f"CREATE DATABASE {DatabaseName};")

        self.cursor.execute(f"USE {DatabaseName};")
        self.cursor.execute("SHOW TABLES;")
        tables = [db[0] for db in self.cursor.fetchall()]

        table_name = TableNames.get(courier_partner)

        col_queries = None
        if courier_partner == CourierPartnerName.SHIPROCKET:
            col_queries = SqlQueries().SHIPROCKET_DATA_COLS
        elif courier_partner == CourierPartnerName.DTDC:
            col_queries = SqlQueries().DTDC_DATA_COLS

        if table_name and table_name not in tables:
            self.cursor.execute(f"CREATE TABLE {table_name} ({col_queries});")

        return table_name

    async def pincode_sku_table_checker(self):
        self.cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in self.cursor.fetchall()]

        if DatabaseName not in databases:
            self.cursor.execute(f"CREATE DATABASE {DatabaseName};")

        self.cursor.execute(f"USE {DatabaseName};")
        self.cursor.execute("SHOW TABLES;")
        tables = [db[0] for db in self.cursor.fetchall()]
        if PincodeSKUTable not in tables:
            self.cursor.execute(f"CREATE TABLE {PincodeSKUTable} ({SqlQueries().PINCODE_SKU_COLS});")

    async def _execute_batch_insert(self, query, batch_values):
        try:
            self.cursor.executemany(query, batch_values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    async def _execute_update(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.connector.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

    async def _check_order_exists(self, table_name, order_id: str) -> bool:
        query = f"SELECT COUNT(*) FROM {table_name} WHERE order_id = %s"
        self.cursor.execute(query, (order_id,))
        count = self.cursor.fetchone()[0]
        return count > 0

    async def _check_pincode_exists(self, table_name, pincode: str, courier_partner: str) -> bool:
        query = f"SELECT COUNT(*) FROM {table_name} WHERE pincode = %s and courier_partner = %s"
        self.cursor.execute(query, (pincode, courier_partner,))
        count = self.cursor.fetchone()[0]
        return count > 0

    async def parse_date(self, date_str: str) -> date:
        normalized_date_str = re.sub(r'[-/.]', '-', date_str)

        try:
            if len(normalized_date_str.split('-')[0]) == 4:
                return datetime.strptime(normalized_date_str, "%Y-%m-%d %H:%M:%S").date()

            if len(normalized_date_str.split('-')[2]) == 4:
                return datetime.strptime(normalized_date_str, "%d-%m-%Y").date()
            elif " " in normalized_date_str:
                return datetime.strptime(normalized_date_str, "%d-%m-%y %H:%M")
            else:
                return datetime.strptime(normalized_date_str, "%d-%m-%y").date()
        except ValueError:
            raise ValueError(f"Date format not recognized: {date_str}")

    async def get_tracker_data_service(self, courier_partner, page, limit, upload_file):
        # Save the uploaded file and read it into a DataFrame
        file_path = await save_upload_file_tmp(upload_file)
        df = pd.read_csv(file_path)

        if courier_partner == CourierPartnerName.DTDC:
            df = df.sort_values('Created At').drop_duplicates(subset='CN #', keep='last')
        elif courier_partner == CourierPartnerName.SHIPROCKET:
            df = df.sort_values('Shiprocket Created At').drop_duplicates(subset='Order ID', keep='last')

        # Select columns and format DataFrame based on the courier partner
        col_list, address_cols = await self._get_courier_column_list(courier_partner)
        df = df[col_list]
        df['Customer Address'] = df[address_cols].apply(lambda x: ', '.join(x.dropna()), axis=1)

        if courier_partner == CourierPartnerName.SHIPROCKET:
            pincode_dict = df['Address Pincode'].value_counts().to_dict()
        elif courier_partner == CourierPartnerName.DTDC:
            pincode_dict = df['Destination Pincode'].value_counts().to_dict()

        sorted_pincode_dict = dict(sorted(pincode_dict.items(), key=lambda item: item[1], reverse=True))

        await self.pincode_sku_table_checker()

        # Prepare batch values for insert and update operations for pincode sku
        batch_values = []
        for k, v in sorted_pincode_dict.items():
            values = (k, v, courier_partner.value)
            values = tuple(None if pd.isna(v) else v for v in values)

            if await self._check_pincode_exists(PincodeSKUTable, k, courier_partner.value):
                update_values = (k, values[1], values[-1])
                await self._execute_update(await SqlQueries().get_pincode_sku_update_data(PincodeSKUTable),
                                           update_values)
            else:
                batch_values.append(values)

        # Execute batch insert if there are any new values
        if batch_values:
            await self._execute_batch_insert(await SqlQueries().get_pincode_sku_insert_data(PincodeSKUTable),
                                             batch_values)

        # Determine table and queries for insertion and updates
        table_name = await self.table_checker(courier_partner)
        query_insert, query_update = await self._get_query_for_courier(courier_partner, table_name)
        current_time = datetime.now()

        # Prepare batch values for insert and update operations for normal data
        batch_values = []
        for _, row in df.iterrows():
            values = await self._get_values_for_courier(courier_partner, row, current_time)
            values = tuple(None if pd.isna(v) else v for v in values)

            order_id = await self._get_order_id(courier_partner, row)

            if await self._check_order_exists(table_name, order_id):
                update_values = values[1:] + (order_id,)
                await self._execute_update(query_update, update_values)
            else:
                batch_values.append(values)

        # Execute batch insert if there are any new values
        if batch_values:
            await self._execute_batch_insert(query_insert, batch_values)

        # Fetch data from the database for pagination
        table_name = TableNames.get(courier_partner)
        if not table_name:
            raise HTTPException(status_code=400, detail="Invalid courier partner")

        self.cursor.execute(f"USE {DatabaseName};")
        query = f"SELECT * FROM {table_name} ORDER BY updated_at LIMIT {limit} OFFSET {page * limit};"
        total_data_query = f"SELECT COUNT(*) as total FROM {table_name};"

        try:
            total = await self._get_total_count(total_data_query)
            rows = await self._fetch_data(query)
            df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")

        sorted_dict = df.to_dict(orient='records')
        return sorted_dict, total

    # Helper methods
    async def _get_courier_column_list(self, courier_partner):
        if courier_partner == CourierPartnerName.SHIPROCKET:
            col_list = ["Order ID", "Shiprocket Created At", "Status", "Product Name", "Product Quantity",
                        "Customer Name", "Address Line 1", "Address Line 2", "Address City", "Address State",
                        "Address Pincode", "Payment Method", "Order Total", "Courier Company", "Order Delivered Date",
                        "RTO Initiated Date", "Payment Received"]
            address_cols = ['Address Line 1', 'Address Line 2', 'Address City', 'Address State']
        elif courier_partner == CourierPartnerName.DTDC:
            col_list = ["CN #", "Status", "Created At", "Amount to be Paid", "Number Of pieces", "Receiver Name",
                        "Expected Delivery Date", "Revised Expected Delivery Date", "Destination Address Line 1",
                        "Destination Address Line 2", "Destination Address Line 3", "Destination City",
                        "Destination State", "Destination Pincode", "IS RTO", "Is COD", "Payment Received"]
            address_cols = ['Destination Address Line 1', 'Destination Address Line 2', 'Destination Address Line 3',
                            'Destination City', 'Destination State']
        return col_list, address_cols

    async def _get_query_for_courier(self, courier_partner, table_name):
        if courier_partner == CourierPartnerName.SHIPROCKET:
            return (
                await SqlQueries().get_shiprocket_insert_tracker_data(table_name),
                await SqlQueries().get_shiprocket_update_tracker_data(table_name)
            )
        elif courier_partner == CourierPartnerName.DTDC:
            return (
                await SqlQueries().get_dtdc_insert_tracker_data(table_name),
                await SqlQueries().get_dtdc_update_tracker_data(table_name)
            )

    async def _get_values_for_courier(self, courier_partner, row, current_time):
        if courier_partner == CourierPartnerName.SHIPROCKET:
            return (
                row.get('Order ID'), str(row.get('Shiprocket Created At')), row.get('Status'),
                row.get('Product Name'),
                row.get('Product Quantity'), row.get('Customer Name'), row.get('Customer Address'),
                row.get('Address Pincode'), row.get('Payment Method'), row.get('Order Total'),
                row.get('Courier Company'),
                str(row.get('Order Delivered Date')) if pd.notna(
                    row.get('Order Delivered Date')) else None,
                row.get('RTO Initiated Date'), row.get('Payment Received'),
                current_time
            )
        elif courier_partner == CourierPartnerName.DTDC:
            return (
                row.get('CN #'), row.get('Status'), str(row.get('Created At')),
                row.get('Amount to be Paid'),
                row.get('Number Of pieces'), row.get('Receiver Name'), row.get('Expected Delivery Date'),
                row.get('Revised Expected Delivery Date'), row.get('Customer Address'), row.get('Destination Pincode'),
                row.get('IS RTO'), row.get('Is COD'), row.get('Payment Received'),
                current_time
            )

    async def _get_order_id(self, courier_partner, row):
        if courier_partner == CourierPartnerName.SHIPROCKET:
            return row.get('Order ID')
        elif courier_partner == CourierPartnerName.DTDC:
            return row.get('CN #')

    async def _get_total_count(self, total_data_query):
        self.cursor.execute(total_data_query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    async def _fetch_data(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    async def get_pincode_sku_data_service(self, courier_partner, pincode):
        self.cursor.execute(f"USE {DatabaseName};")

        conditions = [f'courier_partner = "{courier_partner}"']
        if pincode:
            conditions.append(f'pincode = {pincode}')
        condition = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"SELECT * FROM {PincodeSKUTable} {condition};"

        rows = await self._fetch_data(query)
        df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])
        data = df.to_dict(orient='records')

        return data

    async def get_rto_data_service(self, courier_partner, pincode=None):
        self.cursor.execute(f"USE {DatabaseName};")

        table_name = TableNames.get(courier_partner)

        conditions = []
        if pincode:
            conditions.append(f'customer_pincode = {pincode}')

        if courier_partner == CourierPartnerName.SHIPROCKET:
            conditions.append(f'rto_initiated_date is not null')
        elif courier_partner == CourierPartnerName.DTDC:
            conditions.append(f'is_rto = "YES"')
        condition = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"SELECT * FROM {table_name} {condition};"

        try:
            rows = await self._fetch_data(query)
            df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])

            data = dict(sorted({pincode: df['customer_pincode'].tolist().count(pincode)
                                for pincode in set(df['customer_pincode'])}.items(),
                               key=lambda item: item[1],
                               reverse=True))
        except:
            data = {}

        data = [{"pincode": k, "num_of_orders": v} for k, v in data.items()]

        return data

    async def get_payment_data_service(
            self,
            courier_partner,
            payment_received=None,
            page_limit=True,
            cod=None,
            page=0,
            limit=25
    ):
        self.cursor.execute(f"USE {DatabaseName};")

        table_name = TableNames.get(courier_partner)

        conditions = []
        if payment_received:
            condition = 'payment_received = "YES"'
            conditions.append(condition)
        elif payment_received == False:
            condition = 'payment_received = "NO"'
            conditions.append(condition)

        if cod:
            if courier_partner == CourierPartnerName.DTDC:
                condition = 'is_cod = "YES"'
                conditions.append(condition)
            elif courier_partner == CourierPartnerName.SHIPROCKET:
                condition = 'payment_method = "cod"'
                conditions.append(condition)
        elif cod == False:
            if courier_partner == CourierPartnerName.DTDC:
                condition = 'is_cod = "NO"'
                conditions.append(condition)
            elif courier_partner == CourierPartnerName.SHIPROCKET:
                condition = 'payment_method <> "cod"'
                conditions.append(condition)

        condition = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        if page_limit:
            condition = f'{condition} LIMIT {limit} OFFSET {page * limit}'

        query = f"SELECT * FROM {table_name} {condition};"

        rows = await self._fetch_data(query)
        df = pd.DataFrame(rows, columns=[i[0] for i in self.cursor.description])

        return df.to_dict(orient='records')

class SqlQueries:
    PINCODE_SKU_COLS = """
        pincode INT,
        num_of_orders INT,
        courier_partner VARCHAR(255)
        """

    ADDITIONAL_DATA_COLS = """
        name VARCHAR(255),
        cost_per_order DECIMAL(10, 3) NULL,
        operator VARCHAR(255),
        courier_partner VARCHAR(255) NULL,
        total_cost DECIMAL(10, 3) NULL
        """

    # TRACKER_DATA_COLS = """
    # order_id VARCHAR(255),
    # consignment_id VARCHAR(255),
    # product_name VARCHAR(255),
    # courier_partner VARCHAR(255),
    # customer_number INT,
    # customer_address TEXT,
    # customer_pincode INT,
    # product_price DECIMAL(10, 2),
    # date DATE,
    # status VARCHAR(255),
    # updated_at DATETIME
    # """

    SHIPROCKET_DATA_COLS = """
        order_id VARCHAR(255),
        shiprocket_created_at VARCHAR(255),
        status VARCHAR(255),
        product_name VARCHAR(255),
        product_quantity INT,
        customer_name VARCHAR(255),
        customer_address TEXT,
        customer_pincode INT,
        payment_method VARCHAR(255),
        order_total DECIMAL(10, 2),
        courier_company VARCHAR(255),
        order_delivery_date VARCHAR(255),
        rto_initiated_date VARCHAR(255),
        payment_received ENUM('YES', 'NO') DEFAULT 'NO',
        updated_at DATETIME
        """

    DTDC_DATA_COLS = """
            order_id VARCHAR(255),
            status VARCHAR(255),
            created_at VARCHAR(255),
            amount_to_be_paid DECIMAL(10, 2),
            product_quantity INT,
            customer_name VARCHAR(255),
            expected_delivery_date VARCHAR(255) NULL,
            revised_expected_delivery_date VARCHAR(255) NULL,
            customer_address TEXT,
            customer_pincode INT,
            is_rto VARCHAR(255) NULL,
            is_cod VARCHAR(255) NULL,
            payment_received VARCHAR(255),
            updated_at DATETIME
            """

    # async def get_insert_tracker_data(self, table_name):
    #     return f"""
    #     INSERT INTO {table_name} (order_id, consignment_id, product_name, courier_partner,
    #                                customer_number, customer_address, customer_pincode,
    #                                product_price, date, status, updated_at)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     """

    async def get_dtdc_insert_tracker_data(self, table_name):
        return f"""
        INSERT INTO {table_name} (
        order_id,
        status,
        created_at,
        amount_to_be_paid,
        product_quantity,
        customer_name,
        expected_delivery_date,
        revised_expected_delivery_date,
        customer_address,
        customer_pincode,
        is_rto,
        is_cod,
        payment_received,
        updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    async def get_shiprocket_insert_tracker_data(self, table_name):
        return f"""
        INSERT INTO {table_name} (
        order_id, 
        shiprocket_created_at, 
        status, 
        product_name,
        product_quantity,
        customer_name,
        customer_address,
        customer_pincode,
        payment_method,
        order_total,
        courier_company,
        order_delivery_date,
        rto_initiated_date,
        updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    # async def get_update_tracker_data(self, table_name):
    #     return f"""
    #     UPDATE {table_name}
    #     SET
    #         consignment_id = %s,
    #         product_name = %s,
    #         courier_partner = %s,
    #         customer_number = %s,
    #         customer_address = %s,
    #         customer_pincode = %s,
    #         product_price = %s,
    #         date = %s,
    #         status = %s,
    #         updated_at = %s
    #     WHERE order_id = %s
    #     """

    async def get_shiprocket_update_tracker_data(self, table_name):
        return f"""
        UPDATE {table_name} 
        SET 
            shiprocket_created_at = %s, 
            status = %s, 
            product_name = %s,
            product_quantity = %s,
            customer_name = %s,
            customer_address = %s,
            customer_pincode = %s,
            payment_method = %s,
            order_total = %s,
            courier_company = %s,
            order_delivery_date = %s,
            rto_initiated_date = %s,
            updated_at = %s
        WHERE order_id = %s
        """

    async def get_shiprocket_update_payment_data(self, table_name):
        return f"""
        UPDATE {table_name} 
        SET 
            payment_received = %s,
            updated_at = %s
        WHERE order_id = %s
        """

    async def get_dtdc_update_tracker_data(self, table_name):
        return f"""
        UPDATE {table_name} 
        SET 
            status = %s,
            created_at = %s,
            amount_to_be_paid = %s,
            product_quantity = %s,
            customer_name = %s,
            expected_delivery_date = %s,
            revised_expected_delivery_date = %s,
            customer_address = %s,
            customer_pincode = %s,
            is_rto = %s,
            is_cod = %s,
            payment_received = %s,
            updated_at = %s
        WHERE order_id = %s
        """

    async def get_pincode_sku_insert_data(self, table_name):
        return f"""
        INSERT INTO {table_name} (
        pincode, 
        num_of_orders,
        courier_partner
        )
        VALUES (%s, %s, %s)
        """

    async def get_pincode_sku_update_data(self, table_name):
        return f"""
        UPDATE {table_name} 
        SET 
            num_of_orders = %s
        WHERE pincode = %s and courier_partner = %s
        """

    async def get_additional_data_query(self, table_name):
        return f"""
        INSERT INTO {table_name} (
        name,
        cost_per_order,
        operator,
        courier_partner,
        total_cost
        )
        VALUES (%s, %s, %s, %s, %s)
        """


    async def update_additional_data_query(self, table_name):
        return f"""
        UPDATE {table_name} 
        SET 
            cost_per_order = %s,
            operator = %s,
            total_cost = %s
        WHERE name = %s and courier_partner = %s
        """

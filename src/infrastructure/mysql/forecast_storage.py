import mysql.connector
from config.config import get_config
from src.utils.singleton import SingletonMeta
dbconfig = {
    "host": get_config("database", "host"),
    "port": int(get_config("database", "port")),
    "database": get_config("database", "database"),
    "user":     get_config("database", "user"),
    "password": get_config("database", "password")
}

cnx = mysql.connector.connect(pool_name = "mypool",
                              pool_size = 3,
                              **dbconfig)


class ForecastStorage(metaclass=SingletonMeta):
    def insert_result(self, product_id, store_id, forecast_quantity):
        pass

    def find_in_cache(self, product_id, store_id):
        pass

    def find_orders(self, product_id, store_id, begin_date, end_date):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(
            " SELECT product_metadata, store_type, region_id_x as region_id, brand_id, product_id, store_id, "
            " store_size, checkout_date, SUM(quantity) as sum_quantity"
            " FROM orders WHERE product_id = %(product_id)s AND store_id = %(store_id)s AND "
            " checkout_date BETWEEN %(begin_date)s AND %(end_date)s "
            " GROUP BY product_metadata, store_type, region_id_x, brand_id, product_id, store_id, store_size, "
            " checkout_date ;",
            {
                "product_id": product_id, "store_id": store_id, "begin_date": begin_date, "end_date": end_date
            })
        query_rows = cursor.fetchall()
        return query_rows

if __name__ == '__main__':
    test = ForecastStorage()
    rows = test.find_orders(4661, 629, "2022-01-01", "2022-12-01")
    for row in rows:
        print(row)
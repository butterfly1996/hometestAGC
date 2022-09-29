from src.infrastructure.mysql.forecast_storage import ForecastStorage
from src.app.domain.sale_forecast import SaleForecastModel
from src.utils.singleton import SingletonMeta
from config.config import get_config
from src.app.domain.model.forecast_result import ForecastResult
import datetime
from src.app.domain.model.request_info import RequestInfo


class Forecastor(metaclass=SingletonMeta):
    def __init__(self):
        self.model = SaleForecastModel()
        self.db = ForecastStorage()
        # self.weekly_product_ids = self.__load_weekly_products(get_config("products", "weekly"))

    def predict_quantity(self, product_id, store_id, use_cache, date):

        # if use_cache:
        #     quantity = self.db.find_in_cache(product_id, store_id)
        #     if quantity:
        #         return ForecastResult.value_of(product_id, store_id, quantity)
        #     else:
        #         forecasted_quantity = self.__forecast_quantity(product_id, store_id)
        #         self.db.insert_result(product_id, store_id, forecasted_quantity)
        # else:
        forecasted_quantity = self.__forecast_quantity(product_id, store_id, date)
        # self.db.insert_result(product_id, store_id, forecasted_quantity)
        return ForecastResult(
            product_id=product_id,
            quantity=forecasted_quantity,
            store_id=store_id,
            detail="product and store have enough data",
            is_computable=True)

    def __forecast_quantity(self, product_id, store_id, date):
        request_info = self.__preprocessing(product_id, store_id, date)
        if request_info is None:
            return None
        # if request_info in self.weekly_product_ids:
        #     return self.model.forecast(request_info)
        # else:
        return self.model.forecast(request_info)

    def __load_weekly_products(self, product_ids: str):
        return set(product_ids)

    def __preprocessing(self, product_id, store_id, date):
        if date:
            tmp_date = date
            today = datetime.datetime.strptime(tmp_date, "%Y-%m-%d")
        else:
            tmp_date = datetime.datetime.now()
            today = datetime.datetime.strptime(tmp_date, "%Y-%m-%d")
        begin_date = (today-datetime.timedelta(days=SaleForecastModel.WINDOW_SIZE)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        rows = self.db.find_orders(product_id, store_id, begin_date, end_date)
        # join will slow down the queries
        product_metadata = []
        if rows:
            product_metadata = rows[0]["product_metadata"]
            store_type = rows[0]["store_type"]
            region_id = rows[0]["region_id"]
            brand_id = rows[0]["brand_id"]
            product_id = rows[0]["product_id"]
            store_size = rows[0]["store_size"]
            quantities = [0]*SaleForecastModel.WINDOW_SIZE
            for row in rows:
                quantities[
                    (datetime.datetime.combine(row['checkout_date'], datetime.time.min)-today+datetime.timedelta(days=SaleForecastModel.WINDOW_SIZE)).days
                ] = int(row["sum_quantity"])

            return RequestInfo(
                product_metadata, store_type, region_id, brand_id, product_id, store_id, store_size, quantities
            )
        return None

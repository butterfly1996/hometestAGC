from fastapi.testclient import TestClient
import mysql.connector
import datetime


class MockCursor():
    def execute(self, anything_1=None, anything_2=None, anything_3=None, **kwargs):
        pass

    def fetchall(self):
        return [{'product_metadata': 'Frozen+Plant Based', 'store_type': 'Natural chain', 'region_id': 3, 'brand_id': 1953,
                 'product_id': 4661, 'store_id': 629, 'store_size': 2, 'checkout_date': datetime.date(2022, 1, 24),
                 'sum_quantity': 1},
                {'product_metadata': 'Frozen+Plant Based', 'store_type': 'Natural chain', 'region_id': 3, 'brand_id': 1953,
                 'product_id': 4661, 'store_id': 629, 'store_size': 2, 'checkout_date': datetime.date(2022, 1, 12),
                 'sum_quantity': 1},
                {'product_metadata': 'Frozen+Plant Based', 'store_type': 'Natural chain', 'region_id': 3, 'brand_id': 1953,
                 'product_id': 4661, 'store_id': 629, 'store_size': 2, 'checkout_date': datetime.date(2022, 1, 26),
                 'sum_quantity': 1},
                {'product_metadata': 'Frozen+Plant Based', 'store_type': 'Natural chain', 'region_id': 3, 'brand_id': 1953,
                 'product_id': 4661, 'store_id': 629, 'store_size': 2, 'checkout_date': datetime.date(2022, 1, 5),
                 'sum_quantity': 1},
                {'product_metadata': 'Frozen+Plant Based', 'store_type': 'Natural chain', 'region_id': 3, 'brand_id': 1953,
                 'product_id': 4661, 'store_id': 629, 'store_size': 2, 'checkout_date': datetime.date(2022, 1, 18),
                 'sum_quantity': 1}]
        return []


class MockDB():
    def __init__(self):
        pass

    def close(self):
        pass

    def cursor(self, dictionary=False):
        return MockCursor()

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


def mock_connector(pool_name = "mypool",
                   pool_size = 3,
                   **dbconfig):
    return MockDB()

global client
client = None


def get_client(monkeypatch):
    global client
    if client is None:
        monkeypatch.setattr(mysql.connector, "connect", mock_connector)
        from api import ForecastorGateway
        client = TestClient(ForecastorGateway.api)
    return client


def test_happy_case(monkeypatch):
    test_client = get_client(monkeypatch)
    files = {
        "product_id": 4661,
        "store_id": 629,
        "use_cache": True,
        "date": "2022-02-02"
    }
    response = test_client.post("v1/forecast", json=files)

    response_body = response.json()
    assert (response_body["product_sale"] == 1)
    assert (response_body["reason"]=="product and store have enough data")

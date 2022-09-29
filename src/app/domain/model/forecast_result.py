

class ForecastResult:
    def __init__(self, product_id, store_id, quantity, detail, is_computable):
        self.product_id = product_id
        self.store_id = store_id
        self.quantity = quantity
        self.detail = detail
        self.is_computable=is_computable

from src.presentation.model.product_forecastor_response import ProductSaleForecastorResponse


class ProductSaleForecastResponseConverter:
    @staticmethod
    def convert(model_response):
        if model_response.is_computable:
            return ProductSaleForecastorResponse(
                product_sale=model_response.quantity,
                reason=model_response.detail)
        else:
            return ProductSaleForecastorResponse(
                product_sale=0,
                reason="Not confidence because product or store has too little history record. "
                       "History sale: %s, history store: %s"
                       % (model_response.product_history, model_response.history_store))

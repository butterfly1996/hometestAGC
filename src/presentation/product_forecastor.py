from typing import Optional

from fastapi import APIRouter, Response, status
from fastapi import HTTPException
from pydantic import BaseModel
from src.app.appcore.forecastor import Forecastor
from src.presentation.converter.forecast_result_response_converter import ProductSaleForecastResponseConverter
from src.presentation.model.product_forecastor_response import ProductSaleForecastorResponse


class Item(BaseModel):
    product_id: int
    store_id: int
    use_cache: bool
    date: str


class ProductForecastor:
    router = APIRouter(prefix="", tags=["Product Forecastor"])

    @staticmethod
    @router.post("/forecast",
                 # response_model=ImageModerationConverter,
                 response_model=ProductSaleForecastorResponse,
                 summary="Predict sale.",
                 description="Predict sale.",
                 response_model_exclude_none=True)
    async def forecast_sale_in_next_60_days(
            item: Item
    ):
        predictor = Forecastor()
        model_response = predictor.predict_quantity(
            item.product_id,
            item.store_id,
            item.use_cache,
            item.date
        )
        if model_response is None:
            raise HTTPException(status_code=404, detail="Product-store id not found in recent 60 days")

        return ProductSaleForecastResponseConverter.convert(model_response)



import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
from src.presentation.product_forecastor import ProductForecastor


class ForecastorGateway:
    """
        REST API Gateway of Aphrodite
    """
    api: FastAPI = FastAPI(title="Pod-foods: Forecast sale API",
                           version="0.0.0",
                           description="Forecast product quantity. 🚀",
                           root_path="")
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api.include_router(ProductForecastor().router, prefix='/v1')


if __name__ == "__main__":
    Instrumentator().instrument(ForecastorGateway.api).expose(ForecastorGateway.api)
    uvicorn.run(app=ForecastorGateway.api, port=8000, host='0.0.0.0')

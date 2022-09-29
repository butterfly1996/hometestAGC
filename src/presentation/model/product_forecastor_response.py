from pydantic import BaseModel, Field
from typing import Optional


class ProductSaleForecastorResponse(BaseModel):
    product_sale: int = Field(0, example=0)
    reason: Optional[str]

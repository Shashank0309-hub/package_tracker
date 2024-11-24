from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AdditionalDataOperatorModel(str, Enum):
    add = "add"
    deduct = "deduct"


class AdditionalDataReq(BaseModel):
    name: str
    cost_per_order: Optional[float] = None
    operator: AdditionalDataOperatorModel
    total_cost: Optional[float] = None


AdditionalDataTable = "additional_data"

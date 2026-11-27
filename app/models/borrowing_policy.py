
from pydantic import BaseModel, Field
from typing import Literal


class BorrowingPolicyCreate(BaseModel):

    policy_name: str = Field(min_length=2, max_length=100)

    book_category: str = Field(min_length=2, max_length=100)

    borrowing_days: int = Field(ge=1, le=365)

    grace_period_days: int = Field(ge=0, le=30)

    fine_per_day_paise: int = Field(ge=0)

    book_type: Literal["physical"] = "physical"

    currency: Literal["INR"] = "INR"

    status: Literal["active", "inactive"] = "active"


class BorrowingPolicyResponse(BaseModel):

    policy_id: str

    policy_name: str

    book_category: str

    borrowing_days: int

    grace_period_days: int

    fine_per_day_paise: int

    book_type: Literal["physical"]

    currency: Literal["INR"]

    status: Literal["active", "inactive"]

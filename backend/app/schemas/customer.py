from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Jane Doe"])
    email: EmailStr = Field(..., examples=["jane@example.com"])
    phone_number: str | None = Field(None, max_length=50, examples=["+1-555-0100"])


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    success: bool = True
    data: list[CustomerResponse]
    total: int


class CustomerSingleResponse(BaseModel):
    success: bool = True
    data: CustomerResponse

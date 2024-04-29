from pydantic import BaseModel, Field


class SuccessResponseModel(BaseModel):
    status: str = "ok"
    payloads: dict = Field(title="Domains")


class FailResponseModel(BaseModel):
    status: str = "fail"
    message: str = Field(title="Fail description")

from datetime import datetime

from pydantic import BaseModel, Field


class BusinessRuleCreate(BaseModel):
    connection_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    table_names: list[str] = Field(min_length=1)
    column_names: list[str] = Field(default_factory=list)


class BusinessRuleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    table_names: list[str] = Field(min_length=1)
    column_names: list[str] = Field(default_factory=list)


class BusinessRuleResponse(BaseModel):
    rule_id: int
    connection_id: int
    title: str
    description: str
    table_names: list[str]
    column_names: list[str]
    created_at: datetime
    updated_at: datetime
from pydantic import BaseModel, Field


class DatabaseConnectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    db_type: str = Field(default="mysql", max_length=50)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=3306, ge=1, le=65535)
    database_name: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class DatabaseConnectionResponse(BaseModel):
    connection_id: int
    name: str
    db_type: str
    host: str
    port: int
    database_name: str
    username: str
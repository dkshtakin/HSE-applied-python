from typing import List, Union, Dict, Any, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, validator


class CreateRequest(BaseModel):
    url: str
    alias: Optional[str] = None
    expires_at: Optional[str] = None

    @validator('expires_at')
    def parse_datetime(cls, value: str):
        return datetime.strptime(value, '%Y-%m-%d %H:%M')


class CreateResponse(BaseModel):
    short_code: str


class UpdateRequest(BaseModel):
    url: str


class UpdateResponse(BaseModel):
    message: str


class DeleteResponse(BaseModel):
    message: str


class GetStatsResponse(BaseModel):
    url: str
    creation_time: str
    access_time: str
    access_count: int


class SearchResponse(BaseModel):
    short_codes: List[str]

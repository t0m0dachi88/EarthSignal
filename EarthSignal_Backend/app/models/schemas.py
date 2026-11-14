from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from uuid import uuid4

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return value

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: str

class BBox(BaseModel):
    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)

    @field_validator("north")
    @classmethod
    def check_latitude_order(cls, value, info):
        south = info.data.get("south")
        if south is not None and value <= south:
            raise ValueError("north must be greater than south.")
        return value

    @field_validator("east")
    @classmethod
    def check_longitude_order(cls, value, info):
        west = info.data.get("west")
        if west is not None and value <= west:
            raise ValueError("east must be greater than west; antimeridian-crossing boxes are not supported.")
        return value

class InvestigationCreate(BaseModel):
    mode: Literal["place", "question", "cell", "contrast"] = "place"
    title: str = Field(default="EarthSignal investigation", max_length=160)
    question: str | None = Field(default=None, max_length=500)
    variable: str
    cell_id: int | None = Field(default=None, ge=0)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    bbox: BBox | None = None
    comparison_cell_id: int | None = Field(default=None, ge=0)
    start_year: int = Field(default=2003, ge=2003, le=2023)
    end_year: int = Field(default=2023, ge=2003, le=2023)

    @field_validator("end_year")
    @classmethod
    def validate_year_range(cls, value, info):
        start = info.data.get("start_year")
        if start and value < start:
            raise ValueError("end_year must be >= start_year.")
        return value

    @field_validator("longitude")
    @classmethod
    def longitude_required_with_latitude(cls, value, info):
        latitude = info.data.get("latitude")
        if latitude is not None and value is None:
            raise ValueError("longitude is required when latitude is provided.")
        return value

    @model_validator(mode="after")
    def validate_mode_requirements(self):
        has_point = self.latitude is not None and self.longitude is not None
        has_location = self.bbox is not None or self.cell_id is not None or has_point
        if self.mode == "question" and not (self.question and self.question.strip()):
            raise ValueError("Question mode requires a non-empty scientific question.")
        if self.mode in ("place", "question") and not has_location:
            raise ValueError("Place/question investigations require bbox, cell_id, or latitude and longitude.")
        if self.mode == "cell" and not (self.cell_id is not None or has_point):
            raise ValueError("Cell mode requires cell_id or latitude and longitude.")
        if self.mode == "contrast" and (self.cell_id is None or self.comparison_cell_id is None):
            raise ValueError("Contrast mode requires cell_id and comparison_cell_id.")
        return self

class ContrastRequest(BaseModel):
    variable: str
    cell_a: int = Field(ge=0)
    cell_b: int = Field(ge=0)

class RecommendationRequest(BaseModel):
    variable: str
    cell_id: int | None = None
    slope_per_decade: float | None = None

class JobResponse(BaseModel):
    investigation_id: str
    job_id: str
    status: str
    created_at: datetime

class ErrorResponse(BaseModel):
    detail: str

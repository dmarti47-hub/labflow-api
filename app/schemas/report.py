from pydantic import BaseModel

from app.schemas.sample import SampleOut


class StatusSummaryItem(BaseModel):
    status: str
    total: int


class StatusSummaryReport(BaseModel):
    items: list[StatusSummaryItem]
    total: int


class TestTypeSummaryItem(BaseModel):
    test_type: str
    total: int


class TestTypeSummaryReport(BaseModel):
    items: list[TestTypeSummaryItem]
    total: int


class OverdueSamplesReport(BaseModel):
    items: list[SampleOut]
    total: int
    rules: dict[str, str]

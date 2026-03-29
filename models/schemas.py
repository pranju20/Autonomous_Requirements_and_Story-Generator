from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict


class Requirement(BaseModel):
    title: str
    description: str
    priority: str
    acceptance_criteria: List[str] = []
    approved: bool = False


class InputRequest(BaseModel):
    input_text: str = Field(..., min_length=5)


class OutputResponse(BaseModel):
    requirements: List[dict]
    conflicts: List[str]
    approved: bool
    gherkin_output: List[str]


class WorkflowState(TypedDict):
    raw_input: str
    cleaned_input: str
    requirements: list
    conflicts: list
    approved: bool
    gherkin_output: list
    run_id: str
    hitl_status: str  # "pending" | "approved" | "rejected"

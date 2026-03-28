from pydantic import BaseModel, Field
from typing import List


class Requirement(BaseModel):
    title: str
    description: str
    priority: str
    acceptance_criteria: List[str] = []
    approved: bool = False


class InputRequest(BaseModel):
    input_text: str = Field(..., min_length=5)


class OutputResponse(BaseModel):
    requirements: List[Requirement]
    conflicts: List[str]
    approved: bool
    gherkin_output: List[str]


class WorkflowState(BaseModel):
    raw_input: str
    cleaned_input: str = ""
    requirements: List[Requirement] = []
    conflicts: List[str] = []
    approved: bool = False
    gherkin_output: List[str] = []


"""
schemas.py — Pydantic models.

IMPORTANT: Pydantic models use DOT NOTATION, not dict subscript.

  req = Requirement(description="...")
  req.description        correct
  req["description"]     causes 'Requirement object is not subscriptable'

If you need dict-style access, call: req.model_dump()["description"]
"""

from typing import TypedDict, Optional


class WorkflowState(TypedDict):
    # Input
    raw_input: str
    input_type: str  # "brief" | "transcript"

    # Agent outputs
    requirements: list  # list[Requirement]
    user_stories: list  # list[UserStory]
    stories_with_criteria: list
    conflicts: list
    finalized_stories: list

    # HITL
    hitl_status: str  # "pending" | "approved" | "rejected"
    hitl_feedback: Optional[str]

    # Meta
    current_agent: str
    errors: list
    run_id: str

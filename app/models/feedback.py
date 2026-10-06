"""
Peer review and post-project feedback models.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PeerFeedbackCreate(BaseModel):
    team_id: int
    evaluator_student_id: int
    target_student_id: int
    collaboration_rating: int = Field(..., ge=1, le=5, description="1=Poor teamwork, 5=Exemplary")
    communication_rating: int = Field(..., ge=1, le=5, description="1=Unresponsive, 5=Clear & proactive")
    task_completion_rating: int = Field(..., ge=1, le=5, description="1=Missed deadlines, 5=Completed all deliverables")
    overall_satisfaction: int = Field(..., ge=1, le=5, description="1=Would not work again, 5=Eager to work again")
    comments: Optional[str] = Field(default="")


class PeerFeedback(PeerFeedbackCreate):
    id: int
    created_at: str

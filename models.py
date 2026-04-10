from typing import List, Literal
from pydantic import BaseModel
from openenv.core.env_server import Action, Observation, State


class SupportAction(Action):
    category: Literal[
        "refund",
        "billing",
        "technical_issue",
        "account_access",
        "shipping",
        "general_query",
        "complaint",
    ]
    priority: Literal["low", "medium", "high", "urgent"]
    escalate: bool
    request_more_info: bool = False
    response_draft: str
    resolution_status: Literal[
        "open",
        "waiting_for_customer",
        "resolved",
        "escalated",
    ]


class SupportObservation(Observation):
    ticket_id: str
    customer_tier: Literal["free", "premium", "enterprise"]
    subject: str
    email_body: str
    previous_interactions: List[str] = []
    sentiment_hint: Literal["calm", "frustrated", "angry", "neutral"]
    sla_hours_remaining: int
    allowed_actions: List[str] = []


class SupportState(State):
    current_task_name: str = ""
    ticket_id: str = ""
    customer_tier: str = ""
    expected_category: str = ""
    expected_priority: str = ""
    expected_escalate: bool = False
    expected_resolution_status: str = ""
    last_reward: float = 0.0
    completed: bool = False


class RewardBreakdown(BaseModel):
    category_score: float = 0.0
    priority_score: float = 0.0
    escalation_score: float = 0.0
    resolution_score: float = 0.0
    response_score: float = 0.0
    total_score: float = 0.0

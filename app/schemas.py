from enum import StrEnum
from pydantic import BaseModel, Field


class Action(StrEnum):
    AUTO_REPLY = "AUTO_REPLY"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    ESCALATE = "ESCALATE"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HistoryMessage(BaseModel):
    role: str
    text: str


class TicketInput(BaseModel):
    ticket_id: str = Field(min_length=1)
    subject: str = ""
    message: str = Field(min_length=1)
    history: list[HistoryMessage] = Field(default_factory=list)


class Prediction(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)


class RetrievedExample(BaseModel):
    id: int
    subject: str
    body: str
    answer: str
    queue: str
    priority: str
    similarity: float = Field(ge=0, le=1)


class LLMAnalysis(BaseModel):
    information_sufficient: bool
    recommended_action: Action
    user_message: str
    operator_summary: str
    missing_information: list[str]
    reason: str


class SupportTicket(BaseModel):
    subject: str
    original_message: str
    history: list[HistoryMessage]
    predicted_category: str
    risk: RiskLevel
    category_confidence: float
    risk_confidence: float
    summary: str
    missing_information: list[str]
    similar_case_ids: list[int]


class ProcessResult(BaseModel):
    ticket_id: str
    category: str
    category_confidence: float
    risk: RiskLevel
    risk_confidence: float
    action: Action
    user_message: str
    support_ticket: SupportTicket | None
    retrieved_examples: list[RetrievedExample]
    trace: list[str]
    fallback_reason: str | None = None

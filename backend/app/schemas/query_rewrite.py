from pydantic import BaseModel


class QueryRewriteOutput(
    BaseModel
):

    standalone_question: str

    depends_on_history: bool

    resolved_references: list[str]

    clarification_needed: bool

    clarification_question: str
from typing import TypedDict

class AgentState(TypedDict):
    user_query: str
    final_answer: str
    intent: str

from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # The list of messages in the conversation
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    # Current booking details
    booking_details: dict
    # Calendar ID
    calendar_id: str
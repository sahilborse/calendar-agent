from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    
    booking_details: dict
   
    calendar_id: str
🗓️ Calendar Appointment Management Agent
This project implements an intelligent agent designed to manage calendar appointments through natural language interactions. It leverages a powerful combination of FastAPI for the web API, LangChain for LLM orchestration, LangGraph for defining complex agent workflows, and the Gemini LLM for understanding and generating human-like responses. Google Calendar API is integrated for actual appointment management.

🚀 Key Technologies
FastAPI ⚡: A modern, fast (high-performance) web framework for building APIs with Python 3.7+. Used to expose the agent's capabilities via HTTP endpoints.

LangChain 🔗: A framework for developing applications powered by language models. It provides tools and abstractions for connecting LLMs with external data sources and agents.

LangGraph 📊: A library built on top of LangChain for creating stateful, multi-actor applications with LLMs. It allows defining complex conversational flows as graphs.

Google Gemini LLM ✨: Google's state-of-the-art large language model, providing the core intelligence for natural language understanding and generation.

Google Cloud Console ☁️: Used for managing Google API credentials, specifically for enabling and accessing the Google Calendar API.

Google Calendar API 📅: The backend service for creating, reading, updating, and deleting calendar events.

🧠 LangGraph Architecture
The agent's intelligence and conversational flow are orchestrated using LangGraph, which defines a stateful graph where nodes represent different steps (e.g., agent thinking, tool execution) and edges define the transitions between these steps.

AgentState 🔄
The core state object for our LangGraph workflow is AgentState, which typically includes:

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    # Add other state variables as needed, e.g., tool_output, current_event_details
    # current_event_details: dict = {}


messages: A list of BaseMessage objects, maintaining the full conversation history between the user and the agent. This is crucial for context.

Nodes 📍
The workflow consists of the following key nodes:

agent (LLM Node) 🤖:

Function: This node represents the core reasoning capability of the agent. It takes the current conversation history, processes it with the Gemini LLM, and decides on the next action.

Decision-making: The LLM determines if it needs to:

Call a tool 🛠️: If the user's request requires interacting with the calendar (e.g., "create an event", "list my appointments"). The LLM will output an AIMessage with tool_calls.

Provide a direct answer 💬: If the query is informational or does not require tool interaction (e.g., "What can you do?").

Ask for clarification 🤔: If the user's request is ambiguous or lacks necessary information.

tool_executor (Tool Execution Node) ⚙️:

Function: This node is responsible for executing the tools that the agent node decides to call. It parses the tool_calls from the AIMessage and invokes the corresponding Python functions (which wrap the Google Calendar API calls).

Output: The output of the tool execution (e.g., confirmation of event creation, list of events) is added back to the AgentState as ToolMessages, allowing the agent to see the results.

end_node (Final Response/Formatting Node - Optional but Recommended) ✅:

Function: While the agent node can also formulate final responses, a dedicated end_node can be used for more sophisticated formatting, summarization, or presenting tool outputs in a user-friendly, professional manner (e.g., using Markdown, tables, or structured text). This ensures the user receives clear and attractive information.

Edges and Conditional Logic ➡️
The flow between nodes is managed by edges and conditional logic:

agent -> tool_executor: After the agent node processes a message, it always transitions to the tool_executor. The tool_executor then checks if any tools were actually requested.

Conditional Edge from tool_executor:

should_continue function: This function inspects the AgentState (specifically the last message and tool outputs) to decide the next step.

If tool calls were made and executed: The flow returns to the agent node (tool_executor -> agent). This allows the agent to process the ToolMessage (the result of the tool execution) and formulate a natural language response to the user.

If no tool calls were made or the agent has provided a final response: The flow transitions to END (or end_node if implemented), signifying the completion of the current turn.

Conceptual Flow Diagram:

[User Input] --> [Entry Point: agent]
      |
      V
    [agent] --(decides to call tool)--> [tool_executor]
      ^                                     |
      |                                     V
      +---(tool output)--- [tool_executor] --(conditional: tool executed)
      |
      +---(conditional: no tool / final response)--> [END]


🛠️ Tools Used
The agent is equipped with several tools to interact with the Google Calendar API:

create_calendar_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None, attendees: Optional[List[str]] = None) ➕:

Purpose: Creates a new event on the user's Google Calendar.

Parameters: Event title, start and end date/time (e.g., "YYYY-MM-DDTHH:MM:SS"), optional description, and optional list of attendee emails.

list_calendar_events(start_time: Optional[str] = None, end_time: Optional[str] = None, max_results: int = 10) 📝:

Purpose: Retrieves a list of upcoming or specified events from the user's Google Calendar.

Parameters: Optional start/end date/time to filter events, and maximum number of events to retrieve.

check_availability_event(start_time: str, end_time: str, attendees: Optional[List[str>] = None) ⏰:

Purpose: Checks the availability of specified attendees for a given time range.

Parameters: Start and end date/time (e.g., "YYYY-MM-DDTHH:MM:SS"), and optional list of attendee emails to check availability for.

(Note: These tool definitions are conceptual. Actual implementation would involve wrapping Google Calendar API calls within these functions.)

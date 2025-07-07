🗓️ Calendar Appointment Management Agent
This project implements an intelligent agent designed to manage calendar appointments through natural language interactions. It uses FastAPI for the web API, LangChain and LangGraph for agent orchestration, and the Gemini LLM for understanding and generating responses. Google Calendar API is integrated for actual appointment management.
Live Demo:- https://calendar-agent-1-0q6y.onrender.com/


🚀 Key Technologies
FastAPI ⚡: A high-performance web framework for building APIs.

LangChain 🔗: Framework for LLM applications.

LangGraph 📊: For defining complex agent workflows as graphs.

Google Gemini LLM ✨: Provides core intelligence for natural language understanding.

Google Cloud Console ☁️: Manages Google API credentials.

Google Calendar API 📅: Manages calendar events.

🧠 Agent Architecture
The agent's conversational flow is orchestrated using a graph-based approach, where nodes represent steps (like agent thinking or tool execution) and edges define transitions.

Key Components:
Agent (LLM Node) 🤖: Uses the Gemini LLM to understand requests and decide whether to use a tool or provide a direct answer.

Tool Executor (Tool Execution Node) ⚙️: Executes the tools chosen by the agent, such as interacting with Google Calendar.

Conditional Logic ➡️: Directs the flow based on whether a tool was used, returning to the agent for a response or ending the conversation.

🛠️ Tools Used
The agent is equipped with several tools to interact with the Google Calendar API:

create_calendar_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None, attendees: Optional[List[str]] = None) ➕:

Purpose: Creates a new event on Google Calendar.

Parameters: Event title, start/end time, optional description, and attendees.

list_calendar_events(start_time: Optional[str] = None, end_time: Optional[str] = None, max_results: int = 10) 📝:

Purpose: Retrieves a list of events from Google Calendar.

Parameters: Optional start/end time to filter, and max results.

check_availability_event(start_time: str, end_time: str, attendees: Optional[List[str>] = None) ⏰:

Purpose: Checks attendee availability for a given time range.

Parameters: Start/end time, and optional attendee emails.

import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, FunctionMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_community.tools.render import format_tool_to_json_schema
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.tools import tools, tool_schemas, create_calendar_event, check_calendar_availability, list_calendar_events
from agent.state import AgentState
from config.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.7,
    google_api_key=settings.GEMINI_API_KEY
)

llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Define the Tool Node
def call_tool(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        # print("tool-call", last_message.tool_calls)  # Debugging output
        tool_outputs = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
           # Debugging output
            # print("tool-call", tool_name, tool_args)
            try:
                # Dynamically call the tool function
                if tool_name == "create_calendar_event":
                    output = create_calendar_event(**tool_args)
                elif tool_name == "check_calendar_availability":
                    output = check_calendar_availability(**tool_args)
                elif tool_name == "list_calendar_events":
                    output = list_calendar_events(**tool_args)
                else:
                    output = {"status": "error", "message": f"Unknown tool: {tool_name}"}
                
                 # Debugging output
                tool_outputs.append(FunctionMessage(name=tool_name, content=str(output)))
            except Exception as e:
                tool_outputs.append(FunctionMessage(name=tool_name, content=f"Error executing tool {tool_name}: {e}"))
            # print("tool_output",tool_outputs,"\n\n")
        return {"messages": tool_outputs}
    return state # If no tool call, return state as is (shouldn't happen if condition is met)


# Define graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tool", call_tool)

# Define edges
workflow.add_edge("agent", "tool") # Agent always tries to call a tool if available
# workflow.add_edge("end", END)
# Define conditional edges
def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    print("last_message", last_message)
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        print("continue_tool_execution")
        return "continue_tool_execution"
    else:
       
        return "summarize_and_end"

workflow.add_conditional_edges(
    "tool",
    should_continue,
    {
        "continue_tool_execution": "agent",
        "summarize_and_end": END
    }
)
# workflow.add_edge("summarize", "end")
workflow.set_entry_point("agent")

# workflow.set_finish_point("end")
graph = workflow.compile()


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import settings
from agent.agent import graph, AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings


app = FastAPI(title="Calendar Booking AI Agent")

# Mount static files for Streamlit to access (if needed, otherwise remove)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize graph once
# Ensure GEMINI_API_KEY and GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON are set in env or .env
# graph = create_agent_graph() # If you make graph a function call

class ChatRequest(BaseModel):
    message: str
    chat_history: List[List[str]] = [] # [[user_msg, ai_msg], ...]

class ChatResponse(BaseModel):
    response: str
    chat_history: List[List[str]]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", # or "gemini-1.5-pro", "gemini-1.5-flash"
    temperature=0.7,
    google_api_key=settings.GEMINI_API_KEY
)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Calendar Booking AI Agent</title>
        </head>
        <body>
            <h1>Welcome to the Calendar Booking AI Agent Backend!</h1>
            <p>This is the backend for your Streamlit chat interface.</p>
            <p>Access the Streamlit frontend to interact with the bot.</p>
        </body>
    </html>
    """
def call_model_final(prompt):
    # messages = state["messages"]
    # print("\n\n messages:", messages[-1])
    # response = llm_with_tools.invoke("Create a summary to this data and show it for easy understanding"+str(messages))
    response = llm.invoke(f"Show the provided data in more general and understandable form with covering each content from the data if htmlLink are present show them also don't provide observations and understanding headings or quotes:\n{prompt}")
    # return {"messages": messages + [response]}
    print("\n\n response:")
    return response.content  # Add a key for the end node to use
    
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Convert chat_history to LangChain messages
    messages = []
    for human_msg, ai_msg in request.chat_history:
        messages.append(HumanMessage(content=human_msg))
        messages.append(AIMessage(content=ai_msg))
    
    messages.append(HumanMessage(content=request.message))

    # Initialize agent state
    current_state = AgentState(
        messages=messages,
        booking_details={}, # Reset or manage state across turns carefully
        calendar_id=settings.CALENDAR_ID
    )

    try:
        final_response_message = None
        for s in graph.stream(current_state):
            # print(f"Agent step: {s}\n") # Debugging
            # The last message in the stream should be the AI's final response or tool output
            # We want the actual AI message for the final response
            for key, value in s.items():
                print("\nkey: ",key, "\nvalue:",value)
                if key == "agent" and value and value['messages']:
                    last_msg = value['messages'][-1]
                    if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                        final_response_message = last_msg.content
                elif key == "tool" and value and value['messages']:
                    # Capture tool output for agent to process next, but not as final display
                     # Debugging output
                    # print("output", value['messages'])  # Debugging output
                    final_response_message = value['messages'][-1].content 
                    pass
        
        # If no explicit AI message was found at the end, default to the last message content
        if not final_response_message:
            # This handles cases where the agent might just output tool results or finish without a direct AI message
            final_response_message = messages[-1].content if messages else "No response generated."
        
        # Append current interaction to chat_history for next turn
        updated_chat_history = request.chat_history + [[request.message, str(final_response_message)]]
        # print("final_response_message", final_response_message)
        # final_response = call_model_final(str(final_response_message))
          # Debugging output ## contains only user chat
        # print("messages", messages)  # Debugging output ## contains all chat history
        response_message = call_model_final(str(final_response_message))
        return ChatResponse(response=response_message, chat_history=updated_chat_history)
    except Exception as e:
        print(f"Error during chat processing: {e}")
        return ChatResponse(response="An error occurred while processing your request. Please try again.", chat_history=request.chat_history)
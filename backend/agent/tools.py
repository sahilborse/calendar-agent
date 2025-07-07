import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
from config.settings import settings 

# --- Google Calendar Setup ---
SCOPES = ['https://www.googleapis.com/auth/calendar']
# This will be loaded from environment variable in production
# For local dev, ensure GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON is set in .env
SERVICE_ACCOUNT_INFO = settings.GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON

def get_calendar_service():
    if not SERVICE_ACCOUNT_INFO:
        raise ValueError("GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON environment variable not set.")
    
    try:
       
        info_dict = json.loads(SERVICE_ACCOUNT_INFO)
        print("info_dict", info_dict)
        credentials = service_account.Credentials.from_service_account_info(
            info_dict, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)
        print("Initializing Google Calendar service...\n")
        return service
    except Exception as e:
        print(f"Error initializing Google Calendar service: {e}")
        raise

# --- Pydantic Schemas for Tools (for LLM function calling) ---

class CreateEventSchema(BaseModel):
    summary: str = Field(description="Title or summary of the calendar event.")
    start_time: str = Field(description="Start datetime of the event in ISO 8601 format (e.g., '2025-07-05T10:00:00').")
    end_time: str = Field(description="End datetime of the event in ISO 8601 format (e.g., '2025-07-05T11:00:00').")
    description: Optional[str] = Field(None, description="Optional description for the event.")
    # attendees: Optional[List[str]] = Field(None, description="Optional list of attendee emails.")

class CheckAvailabilitySchema(BaseModel):
    start_time: str = Field(description="Start datetime for availability check in ISO 8601 format.")
    end_time: str = Field(description="End datetime for availability check in ISO 8601 format.")

# --- Google Calendar Tool Functions ---

def create_calendar_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None, attendees: Optional[List[str]] = None) -> Dict:
    """
    Creates a new event on the Google Calendar.
    Requires summary, start_time, and end_time.
    start_time and end_time must be in ISO 8601 format (e.g., '2025-07-05T10:00:00').
    """
    service = get_calendar_service()
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'}, # Adjust timezone as needed
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'}, # Adjust timezone as needed
        # 'attendees': [{'email': email} for email in attendees] if attendees else [],
        'reminders': {'useDefault': True},
    }
    try:
        print("tool:- create_calender_event\n")
        event = service.events().insert(calendarId=settings.CALENDAR_ID, body=event).execute()
        return {"status": "success", "event_id": event['id'], "html_link": event['htmlLink']}
    except HttpError as error:
        return {"status": "error", "message": f"Failed to create event: {error.content.decode('utf-8')}"}

def check_calendar_availability(start_time: str, end_time: str) -> Dict:
    """
    Checks the availability of the calendar for a given time range.
    Returns True if available, False otherwise.
    start_time and end_time must be in ISO 8601 format.
    """
    service = get_calendar_service()
   
    
    # Adjust timezone if necessary for precise availability checks
    # current_timezone = 'Asia/Kolkata' # This should match your calendar's timezone settings
    
    body = {
        "timeMin": start_time +"Z",
        "timeMax": end_time+"Z",
        "items": [{"id": settings.CALENDAR_ID}] 
    }
    print(body)
    try:
        response = service.freebusy().query(body=body).execute()
        busy_intervals = response['calendars'][settings.CALENDAR_ID]['busy']
        
        if busy_intervals:
            return {"status": "busy", "intervals": busy_intervals}
        else:
            return {"status": "available"}
    except HttpError as error:
        print("check availability error",error)
        return {"status": "error", "message": f"Failed to check availability: {error.content.decode('utf-8')}"}

# Add more tools as needed (e.g., list_events, update_event, delete_event)
# Example: List events for a period
class ListEventsSchema(BaseModel):
    time_min: Optional[str] = Field(None, description="Start datetime for listing events in ISO 8601 format. Defaults to now.")
    time_max: Optional[str] = Field(None, description="End datetime for listing events in ISO 8601 format. Defaults to 7 days from now.")
    max_results: int = Field(10, description="Maximum number of events to return.")

def list_calendar_events(time_min: Optional[str] = None, time_max: Optional[str] = None, max_results: int = 10) -> Dict:
    """
    Lists events from the Google Calendar within a specified time range.
    Defaults to 10 events from now to 7 days from now if dates are not provided.
    """
    service = get_calendar_service()
    now = datetime.utcnow()
    
    if not time_min:
        time_min = now.isoformat() + 'Z'
    if not time_max:
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
    print("list_calendar_events\n", time_min, time_max, max_results)
    try:
        events_result = service.events().list(
            calendarId=settings.CALENDAR_ID,
            timeMin=time_min+"Z",
            timeMax=time_max+"Z",
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        if not events:
            return {"status": "success", "message": "No upcoming events found."}
        
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_list.append({
                "summary": event.get('summary'),
                "start": start,
                "end": end,
                "htmlLink": event.get('htmlLink')
            })
        return {"status": "success", "events": event_list}
    except HttpError as error:
        return {"status": "error", "message": f"Failed to list events: {error.content.decode('utf-8')}"}

# Register tools for LangChain/LangGraph
tools = [
    create_calendar_event,
    check_calendar_availability,
    list_calendar_events
]

# Map Pydantic schemas to tools for LLM
tool_schemas = {
    "create_calendar_event": CreateEventSchema,
    "check_calendar_availability": CheckAvailabilitySchema,
    "list_calendar_events": ListEventsSchema
}
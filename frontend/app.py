import streamlit as st
import requests
import os

# Backend URL (use environment variable for deployment)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") # Default for local testing

st.set_page_config(page_title="Calendar Booking AI", layout="centered")

st.title("🗓️ Calendar Booking AI Agent")
st.markdown("I can help you book appointments on your Google Calendar. Just tell me what you need!")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # For sending to backend

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you book an appointment?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            # Send message to FastAPI backend
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "message": prompt,
                    "chat_history": st.session_state.chat_history
                }
            )
            response.raise_for_status() 
            
            data = response.json()
            ai_response = data.get("response")
            updated_chat_history = data.get("chat_history", [])

            with st.chat_message("assistant"):
                st.markdown(ai_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.session_state.chat_history = updated_chat_history

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with backend: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "I'm having trouble connecting right now. Please try again later."})
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "An unexpected error occurred. Please try again."})
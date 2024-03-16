import streamlit as st
import openai
import os
import requests
import json


#####################################################################
# functions
#####################################################################

def get_response(endpoint, conversation_history):
    
    payload = {
      "inputs": [conversation_history],
      "parameters": {
        "max_new_tokens": 500,
        "top_p": 0.9,
        "temperature": 0.6,
        "return_full_text": False
      }
    }

    url_post = f"{endpoint}/ask"

    response = requests.post(url_post, json=payload)

    try:
      response = json.loads(response.text)[0]['generation']['content']
      #print(response)
    except Exception as e:
      response = e
        
    
    
    return response

#####################################################################
# constants
#####################################################################
endpoint_engine = 'http://localhost:8080'

#####################################################################
# app configs
#####################################################################

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Converse com o Assistente Virtual do Hype 💬")

#####################################################################
# app configs
#####################################################################
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Me faça perguntas sobre o Hype, a entidade de Ciência de Dados da EACH-USP."}
    ]

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            conversation_history = st.session_state.messages
            
            response = get_response(endpoint=endpoint_engine, conversation_history = conversation_history)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message) # Add response to message history
            
            print(st.session_state.messages)

import streamlit as st
from utils import *



def main():
    st.set_page_config(
    page_title="Echo Bot",
    page_icon="👋",
    )
    st.write("# ChatBot! 👋")
    options=["English","Spanish","Hindi","Russian","Telugu","Gujarati"]
    language = st.selectbox("Language: ",options=options)
    st.session_state['language'] = language
    
    
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    chat_messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # response = f"Echo: {prompt}"
        response = chat_response(prompt,st.session_state['language'])
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(AIMessage(content=response).content)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": AIMessage(content=response).content})
    
    # st.write("# ChatBot! 👋")
    # options=["English","Spanish"]
    # language = st.selectbox("Language: ",options=options)
    # st.session_state['language'] = language
    
    # prompt = st.chat_input("Say something")
    # if prompt:
    #     chat_messages.append(HumanMessage(prompt))
    #     st.session_state.message.append({"role":"user","content":prompt})
    #     st.write(f"{prompt}")
    #     response = chat_response(prompt,st.session_state['language'])
    #     chat_messages.append(AIMessage(content=response))
    #     # st.session_state['chat_messages'].append(AIMessage(content=response))
    #     st.session_state.message.append({"role":"assistant","content":AIMessage(content=response)})
    #     st.write(response)
    #     with st.sidebar:
    #         for c in st.session_state.messages:
    #             print(type(c))
    #             if type(c)==type(HumanMessage):
    #             #st.write(f"{c.content}\n" for c in chat_messages)
    #                 st.chat_message(user,(f"User: {c.content}")
    #             if type(c)==type(AIMessage):    
    #                 st.sidebar.write(f"Alex: {c.content}")
                    
if __name__=="__main__":
    main()

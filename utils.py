import os
import uuid
from langchain_core.runnables import RunnableConfig
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage,BaseMessage,trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START,MessagesState,StateGraph

from typing import Sequence
from langgraph.graph.message import add_messages
from typing_extensions import Annotated,TypedDict

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="Your API Key"
os.environ["MISTRAL_API_KEY"]="Your API Key"

chats_by_session_id = {}
models = ["mistral-large-latest","ministral-3b-latest"]
model = ChatMistralAI(model=models[0])
trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

#region Project 1
# messages = [
#     HumanMessage(content="hi! I'm Bob"),
#     AIMessage(content="Hello Bob! How can I assist you today?"),
#     HumanMessage(content="What's my name?"),
#     ]
# # print(model.invoke(messages).content)
# print(model.invoke(messages).content)

#endregion

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]
    language: str


def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history

# Define the function that calls the model
def call_model(state: MessagesState, config: RunnableConfig) -> list[BaseMessage]:
    # Make sure that config is populated with the session id
    if "configurable" not in config or "session_id" not in config["configurable"]:
        raise ValueError(
            "Make sure that the config includes the following information: {'configurable': {'session_id': 'some_value'}}"
        )
    # Fetch the history of messages and append to it any new messages.
    chat_history = get_chat_history(config["configurable"]["session_id"])
    messages = list(chat_history.messages) + state["messages"]
    ai_message = model.invoke(messages)
    # Finally, update the chat message history to include
    # the new input message from the user together with the
    # repsonse from the model.
    chat_history.add_messages(state["messages"] + [ai_message])
    return {"messages": ai_message}


def call_model(state: State):
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system","You talk like a pirate. Answer all questions to the best of your ability",),
    #                                            MessagesPlaceholder(variable_name="messages"),])
    prompt = ChatPromptTemplate.from_messages(
    [(
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    if prompt is None:
        response = model.invoke(state["messages"])
        return {"messages": response}
    else:
        chain = prompt|model
        trimmed_messages = trimmer.invoke(state["messages"])
        response = chain.invoke({"messages": trimmed_messages,"language":state['language']})
        return {"messages": [response]}

def create_graph():
    # Define a new Graph
    workflow = StateGraph(state_schema=State)
    
    # Define the (single) node in the graph
    workflow.add_edge(START,"model")
    workflow.add_node("model",call_model)
    
    # Add Memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

def chat_response(query,language="English"):
    app = create_graph()
    config = {"configurable": {"thread_id": "abc457"}}
    messages = [
        SystemMessage(content="you're a good assistant"),
        HumanMessage(content="hi! I'm bob"),
        AIMessage(content="hi!"),
        HumanMessage(content="I like vanilla ice cream"),
        AIMessage(content="nice"),
        HumanMessage(content="whats 2 + 2"),
        AIMessage(content="4"),
        HumanMessage(content="thanks"),
        AIMessage(content="no problem!"),
        HumanMessage(content="having fun?"),
        AIMessage(content="yes!"),
    ]
    input_messages = messages + [HumanMessage(query)]
    if language is None:
        output = app.invoke({"messages": input_messages}, config)
        output["messages"][-1].pretty_print()
        response:AIMessage = output["messages"][-1]
        return response.content
    else:
        output = app.invoke({"messages":input_messages,"language":language}, config)
        output["messages"][-1].pretty_print()
        response:AIMessage = output["messages"][-1]
        get_status(app=app,config=config)
        return response.content

def get_status(app,config):
    state = app.get_state(config).values
    print(f'Language: {state["language"]}')
    for message in state["messages"]:
        message.pretty_print()    

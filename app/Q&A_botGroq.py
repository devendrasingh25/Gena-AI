from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st

llm = ChatGroq(model="openai/gpt-oss-20b")

search = GoogleSerperAPIWrapper()
tools = [search.run]

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()

if "history" not in st.session_state:
    st.session_state.history = []

agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=st.session_state.memory,
    system_prompt="You are an amazing AI agent and can search on Google as well."
)

st.subheader("Quick Answer - As the speed of thoughts")

for m in st.session_state.history:
    st.chat_message(m["role"]).markdown(m["content"])

query = st.chat_input("Ask anything")

if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role": "user", "content": query})

    res = agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": "1"}},
        stream_mode="messages"
    )



    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()
        message = ""

        for chunk in res :
            message = message + chunk[0].content
            space.write(message)

        st.session_state.history.append({"role":"ai" , "content":message})     
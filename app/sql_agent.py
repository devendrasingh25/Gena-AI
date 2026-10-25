from dotenv import load_dotenv
load_dotenv()

import uuid
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

db = SQLDatabase.from_uri("sqlite:///C:/Users/ACER/Desktop/gen-ai/app/my_tasks.db")

db.run("""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT CHECK(status IN ('pending','in_progress','completed')) DEFAULT 'pending'
    );
""")

llm = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

search = GoogleSerperAPIWrapper()
search_tool = Tool(
    name="google_search",
    func=search.run,
    description="Search Google for current information such as match times, news, prices and facts."
)

tools = [search_tool, *toolkit.get_tools()]

system_prompt = """You are a task manager for a SQLite database.
Table: tasks(id, title, description, status)
- id: integer, auto-generated. Never insert it.
- title: short name of the task.
- description: details of the task.
- status: only 'pending', 'in_progress' or 'completed'. Default is 'pending'.

TOOLS
- Use the SQL tools for anything about the user's tasks.
- You have a google_search tool and CAN search the web. Use it whenever the user asks for current information such as a match time, news or prices. Never say you cannot browse the web.

SEARCH + TASK
If the user asks to add a task that needs a fact from the web (for example a match time), first call google_search, then include the result in the task description, then INSERT it and confirm with a SELECT.

TASK RULES
1. Check the table schema before writing any query.
2. For UPDATE or DELETE, always use WHERE with the task id. If the request is unclear, ask the user which task they mean.
3. After performing any task (create, update or delete), run a SELECT to confirm it, then show the result as a markdown table in this format:

| ID | Title | Description | Status |
|----|-------|-------------|--------|
| 1  | Example title | Example details | pending |

Start with one line saying what was done, for example "Task 2 marked as completed." For a delete, the table should no longer contain that task.

CRUD OPERATIONS
Create: INSERT INTO tasks (title, description) VALUES ('title', 'details');
Read:   SELECT * FROM tasks;  or  SELECT * FROM tasks WHERE status = 'pending';
Update: UPDATE tasks SET status = 'completed' WHERE id = 1;
Delete: DELETE FROM tasks WHERE id = 1;
"""

@st.cache_resource
def get_agent():
    return create_agent(
        model=llm,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )

agent = get_agent()

st.subheader("TaskBot - Manage ur todos")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

prompt = st.chat_input("Ask me to manage ur task ?")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("ai"):
        with st.spinner("Processing"):
            res = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                {"configurable": {"thread_id": st.session_state.thread_id}}
            )
            result = res["messages"][-1].content
            st.markdown(result)
            st.session_state.messages.append({"role": "ai", "content": result})
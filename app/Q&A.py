from dotenv import load_dotenv
load_dotenv()

import streamlit as st


from langchain_groq import ChatGroq
llm = ChatGroq(model="openai/gpt-oss-20b")  


st.title("Ask me Question")
st.markdown("My QnA Bot with Langchain and Groq !")



if"messages" not in st.session_state:
     st.session_state.messages = [] 

for message in st.session_state.messages:
     role = message["role"] 
     content = message["content"]
     st.chat_message(role).markdown(content)

query = st.chat_input("Ask anything...")

if query :
    st.session_state.messages.append({"role" : "user" , "content" : query})
   
    st.chat_message("user").markdown(query)
    res = llm.invoke(st.session_state.messages)

    st.chat_message("ai").markdown(res.content)
    st.session_state.messages.append({"role" : "ai" , "content" : res.content})


 
 



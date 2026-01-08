import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import os
import dotenv

dotenv.load_dotenv()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] 
if "poster_encoded" not in st.session_state:
    st.session_state.poster_encoded = None 
if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

        
llm = ChatOpenAI(
    model="qwen/qwen2.5-vl-72b-instruct", 
    api_key=st.secrets("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

st.title("Event Assistant")


uploaded_file = st.file_uploader("Upload Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
   
    import base64
    st.session_state.poster_encoded = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    st.image(uploaded_file, caption="Uploaded Event Poster", width=300)


st.divider()
st.subheader("Ask questions about the event")


for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)


if prompt := st.chat_input("Ex: 'What is the dress code?' or 'Is there a contact number?'"):
    if not st.session_state.poster_encoded:
        st.warning("Please upload a poster first!")
    else:
        
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

       
        payload = [
            {"type": "text", "text": f"Context: You are an event assistant. User asks: {prompt}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.poster_encoded}"}}
        ]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing poster details..."):
                response = llm.invoke([HumanMessage(content=payload)])
                st.markdown(response.content)

                st.session_state.chat_history.append(AIMessage(content=response.content))

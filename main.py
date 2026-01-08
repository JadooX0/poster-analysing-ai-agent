import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import base64


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] 
if "poster_encoded" not in st.session_state:
    st.session_state.poster_encoded = None 


llm = ChatOpenAI(
    model="qwen/qwen2.5-vl-72b-instruct", 
    api_key=st.secrets["OPENROUTER_API_KEY"], 
    openai_api_base="https://openrouter.ai/api/v1"
)

st.title("Event Assistant ")


with st.sidebar:
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

#
uploaded_file = st.file_uploader("Upload Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Encode image only if it hasn't been encoded yet to save processing
    st.session_state.poster_encoded = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    st.image(uploaded_file, caption="Uploaded Event Poster", width=300)

st.divider()
st.subheader("Ask questions about the event")

# --- 5. CHAT HISTORY DISPLAY ---
for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- 6. CHAT LOGIC WITH MEMORY ---
if prompt := st.chat_input("Ex: 'What is the dress code?'"):
    if not st.session_state.poster_encoded:
        st.warning("Please upload a poster first!")
    else:
       
        with st.chat_message("user"):
            st.markdown(prompt)

       
        payload = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.poster_encoded}"}}
        ]

        #
        memory_window = st.session_state.chat_history[-5:]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing poster..."):
                
                response = llm.invoke(memory_window + [HumanMessage(content=payload)])
                st.markdown(response.content)
        
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        st.session_state.chat_history.append(AIMessage(content=response.content))

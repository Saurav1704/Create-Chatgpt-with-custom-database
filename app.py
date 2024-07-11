import streamlit as st
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
from langchain import prompts
import pandas as pd  # Import pandas for DataFrame
import methods  # Import methods from methods.py

# Load environment variables
load_dotenv()

# Call Gemini API
genai.configure(api_key="AIzaSyC8W43iv9O1AAKpz2oUFUgS6VpjrCzIAUQ")

# Function to load Google Gemini model and take prompt as input
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    return response.text

# Function to retrieve the query from SQL database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [description[0] for description in cur.description]  # Get column names
        conn.commit()
        conn.close()
        return rows, column_names, None
    except Exception as e:
        return None, None, str(e)

# Load the prompt
with open('prompts.txt','r') as file:
    prompts = file.read().strip()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to generate AI response
def generate_response(question):
    response_gemini = get_gemini_response(question, prompts)
    if not response_gemini.strip().lower().startswith("select"):
        return pd.DataFrame(), "Generated response is not a valid SQL query."
    
    query_result, column_names, error = read_sql_query(response_gemini, "MAKT.db")
    if error:
        return pd.DataFrame(), f"An error occurred: {error}"
    
    if query_result:
        df = pd.DataFrame(query_result, columns=column_names)
        response_df = df
        response_md = df.to_markdown(index=False)
    else:
        response_df = pd.DataFrame()
        response_md = "No results found."
    return response_df, response_md

st.markdown('Local ChatGPT')

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if question := st.chat_input("Your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(question)

    # Generate AI response
    response_df, response_md = generate_response(question)

    # Add AI message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_md})

    # Display AI message in chat
    with st.chat_message("assistant"):
        tab1, tab2 = st.tabs(["Tabular Data", "Graphical Representation"])
        with tab1:
            st.markdown(response_md)
        
        with tab2:
            if not response_df.empty:
                if len(response_df.columns) == 2:
                    if response_df.dtypes[1] in ['int64', 'float64']:
                        st.write("Graphical Representation")
                        st.bar_chart(data=response_df.set_index(response_df.columns[0]))
                else:
                    st.write("The data is not suitable for a Bar chart.")
            else:
                st.write("No data available to display.")

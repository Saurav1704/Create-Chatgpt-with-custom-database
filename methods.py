import google.generativeai as genai
import sqlite3

# Function to load Google Gemini model and takes prompt as input
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, question])
    return response.text

# Function to retrieve the query from SQL database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    column_names = [description[0] for description in cur.description]  # Get column names
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows, column_names
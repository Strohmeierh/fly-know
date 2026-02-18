import streamlit as st
import google.generativeai as genai
import os

# API Key sicher aus den Streamlit Secrets laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Dein "NotebookLM" Wissen
mein_wissen = """
Hier kannst du deinen Text hineinkopieren, der das Wissen deines Notebooks darstellt.
Du kannst hier alles reinschreiben, was die KI wissen soll.
"""

st.title("Mein eigenes NotebookLM")
user_input = st.text_area("Stelle eine Frage an das Dokument:")

if st.button("Frage stellen"):
    if user_input:
        with st.spinner("KI denkt nach..."):
            # Prompt zusammenbauen
            full_prompt = f"Nutze folgendes Wissen:\n{mein_wissen}\n\nBeantworte die Frage: {user_input}"
            response = model.generate_content(full_prompt)
            st.success("Antwort:")
            st.write(response.text)
    else:
        st.warning("Bitte gib eine Frage ein.")

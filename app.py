import streamlit as st
import google.generativeai as genai
import os

# API Key sicher aus den Streamlit Secrets laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# NEU: Das Skript liest jetzt automatisch die Datei wissen.txt ein!
try:
    with open("wissen.txt", "r", encoding="utf-8") as datei:
        mein_wissen = datei.read()
except FileNotFoundError:
    mein_wissen = "Fehler: Die Datei wissen.txt wurde nicht gefunden. Bitte lade sie auf GitHub hoch."

st.title("Mein eigenes NotebookLM")
user_input = st.text_area("Stelle eine Frage an dein Dokument:")

if st.button("Frage stellen"):
    if user_input:
        with st.spinner("KI denkt nach..."):
            # Prompt zusammenbauen: Wissen + Frage
            full_prompt = f"Nutze folgendes Wissen, um die Frage zu beantworten:\n\n{mein_wissen}\n\nFrage: {user_input}"
            
            # Anfrage an Gemini senden
            response = model.generate_content(full_prompt)
            
            st.success("Antwort:")
            st.write(response.text)
    else:
        st.warning("Bitte gib eine Frage ein.")

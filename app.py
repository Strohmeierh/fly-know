import streamlit as st
import google.generativeai as genai

st.title("Fehlersuche: Meine verfügbaren Modelle")

try:
    # API Key laden
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    st.write("Google sagt, du darfst diese Modelle nutzen:")
    
    # Google nach den Modellen fragen
    modelle_gefunden = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name)
            modelle_gefunden = True
            
    if not modelle_gefunden:
        st.warning("Dein API-Key ist gültig, aber es sind keine Text-Modelle freigeschaltet.")

except Exception as e:
    st.error(f"Es gab ein Problem mit der Verbindung: {e}")

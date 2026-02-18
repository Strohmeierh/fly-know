import streamlit as st
import google.generativeai as genai

# 1. API Key sicher laden und Google konfigurieren
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 2. Das korrekte, neueste Modell nutzen!
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="Du bist ein direkter und sachlicher Assistent der Luftsportgemeinschaft Hotzenwald und gibst Auskunft über flugrelevante Themen auf Anfrage als FAQ. Antworte immer extrem kurz, prägnant und auf den Punkt. Lass unnötige Höflichkeitsfloskeln weg."
)

# 3. Dein NotebookLM Wissen aus der Textdatei laden
try:
    with open("wissen.txt", "r", encoding="utf-8") as datei:
        mein_wissen = datei.read()
except FileNotFoundError:
    mein_wissen = "Fehler: Die Datei wissen.txt wurde nicht auf GitHub gefunden. Bitte lade sie hoch."

# 4. Die Webseite (Benutzeroberfläche) aufbauen
st.title("Mein eigenes NotebookLM")
st.write("Stelle Fragen an dein hochgeladenes Dokument.")

user_input = st.text_area("Deine Frage:")

if st.button("Frage stellen"):
    if user_input:
        with st.spinner("KI liest das Dokument und denkt nach..."):
            # Prompt zusammenbauen: Wissen + Frage
            full_prompt = f"Nutze ausschließlich folgendes Wissen, um die Frage zu beantworten:\n\n{mein_wissen}\n\nFrage des Nutzers: {user_input}"
            
            try:
                # Anfrage an Gemini 2.5 senden
                response = model.generate_content(full_prompt)
                st.success("Antwort:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")
    else:
        st.warning("Bitte gib zuerst eine Frage ein.")

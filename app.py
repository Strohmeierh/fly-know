import streamlit as st
from google import genai
from google.genai import types

# 1. API Key sicher laden und neuen Client initialisieren
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. Dein Wissen aus der Textdatei laden
try:
    with open("wissen.txt", "r", encoding="utf-8") as datei:
        mein_wissen = datei.read()
except FileNotFoundError:
    mein_wissen = "Fehler: Die Datei wissen.txt wurde nicht gefunden."

# 3. Die System-Anweisung
system_regeln = f"""
Du bist ein direkter und hilfreicher Assistent der Luftsportgemeinschaft Hotzenwald e.V. 
Antworte immer kurz und prägnant.
Nutze AUSSCHLIESSLICH das folgende Wissen für deine Antworten. Wenn die Antwort nicht im Text steht, sage das ehrlich.

WISSENSBASIS:
{mein_wissen}
"""

# 4. Webseite aufbauen
st.title("Luftsportgemeinschaft Hotzenwald FAQ")
st.write("Stelle Fragen an unsere KI. Der Verlauf wird nicht gespeichert und beim Neuladen der Seite geleert.")

# 5. Verlauf als einfache Liste speichern (Bulletproof Methode für Streamlit)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Bisherigen Verlauf anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Das neue Chat-Eingabefeld
if user_input := st.chat_input("Deine Frage..."):
    
    # Nutzerfrage speichern und anzeigen
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Daten werden ermittelt..."):
            try:
                # Den Verlauf für das neue Google-Paket passend formatieren
                gemini_verlauf = []
                for m in st.session_state.messages:
                    g_role = "user" if m["role"] == "user" else "model"
                    gemini_verlauf.append({"role": g_role, "parts": [{"text": m["content"]}]})
                    
                # Die Regeln übergeben
                config = types.GenerateContentConfig(system_instruction=system_regeln)
                
                # HIER IST DIE ÄNDERUNG: Wir nutzen jetzt das stabile und verfügbare 2.0-Flash Modell!
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=gemini_verlauf,
                    config=config
                )
                
                # Antwort anzeigen und speichern
                st.markdown(response.text)
                st.session_state.messages

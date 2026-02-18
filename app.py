import streamlit as st
import google.generativeai as genai

# 1. API Key sicher laden und Google konfigurieren
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 2. Dein Wissen aus der Textdatei laden
try:
    with open("wissen.txt", "r", encoding="utf-8") as datei:
        mein_wissen = datei.read()
except FileNotFoundError:
    mein_wissen = "Fehler: Die Datei wissen.txt wurde nicht gefunden."

# 3. Die System-Anweisung: Hier definieren wir die Regeln UND übergeben das Wissen
system_regeln = f"""
Du bist ein direkter und hilfreicher Assistent der Luftsportgemeinschaft Hotzenwald e.V.. 
Antworte immer extrem kurz, prägnant und auf den Punkt.
Nutze AUSSCHLIESSLICH das folgende Wissen für deine Antworten. Wenn die Antwort nicht im Text steht, sage das ehrlich.

WISSENSBASIS:
{mein_wissen}
"""

# 4. Das Modell mit den festen Regeln initiieren
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    system_instruction=system_regeln
)

# 5. Webseite aufbauen (DEINE ÄNDERUNG: Neuer Titel)
st.title("Luftsportgemeinschaft Hotzenwald FAQ")

# (Optional: Hier kannst du auch den kleinen Untertitel anpassen, falls du magst)
st.write("Stelle Fragen an unsere KI. Der Verlauf wird nicht gespeichert und beim Neuladen der Seite geleert.")

# 6. Den Chat-Verlauf für diese Sitzung starten/speichern
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# 7. Den bisherigen Verlauf auf der Seite anzeigen
for message in st.session_state.chat.history:
    rolle = "assistant" if message.role == "model" else "user"
    with st.chat_message(rolle):
        st.markdown(message.parts[0].text)

# 8. Das neue Chat-Eingabefeld
if user_input := st.chat_input("Deine Frage..."):
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # DEINE ÄNDERUNG: Neuer Lade-Text
        with st.spinner("Daten werden ermittelt..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Fehler bei der Anfrage: {e}")

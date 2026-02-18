import streamlit as st
from google import genai
from google.genai import types

# 1. API Key sicher laden und neuen Google Client initialisieren (NEU)
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

# 5. Konfiguration und Chat-Sitzung starten (NEUES SYSTEM)
if "chat" not in st.session_state:
    # Die Regeln werden jetzt in einem Config-Objekt übergeben
    config = types.GenerateContentConfig(system_instruction=system_regeln)
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash", config=config)
    
    # Wir speichern den Verlauf jetzt super-sauber direkt in Streamlit
    st.session_state.messages = []

# 6. Den bisherigen Verlauf auf der Seite anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Das neue Chat-Eingabefeld
if user_input := st.chat_input("Deine Frage..."):
    
    # Frage des Nutzers anzeigen und speichern
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Antwort der KI holen und anzeigen
    with st.chat_message("assistant"):
        with st.spinner("Daten werden ermittelt..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                st.markdown(response.text)
                # Antwort der KI im Verlauf speichern
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                if "429" in str(e):
                    st.warning("Unsere KI macht gerade eine kleine Verschnaufpause, da zu viele Fragen gleichzeitig gestellt wurden. Bitte warte etwa eine Minute und versuche es noch einmal! ⏱️")
                else:
                    st.error(f"Fehler bei der Anfrage: {e}")

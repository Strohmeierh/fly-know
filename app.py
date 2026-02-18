import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# 1. API Key sicher laden und Google konfigurieren
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 2. NEU: Funktion zum Auslesen aller PDFs in einem Ordner (mit Zwischenspeicher für mehr Geschwindigkeit)
@st.cache_data
def lade_wissen_aus_pdfs(ordner_pfad="dokumente"):
    gesammeltes_wissen = ""
    
    # Prüfen, ob der Ordner überhaupt existiert
    if not os.path.exists(ordner_pfad):
        return f"Fehler: Der Ordner '{ordner_pfad}' wurde auf GitHub nicht gefunden."
    
    # Alle Dateien im Ordner durchgehen
    for dateiname in os.listdir(ordner_pfad):
        if dateiname.endswith(".pdf"):
            dateipfad = os.path.join(ordner_pfad, dateiname)
            try:
                # PDF öffnen und Text aus allen Seiten auslesen
                with open(dateipfad, "rb") as pdf_datei:
                    pdf_leser = PyPDF2.PdfReader(pdf_datei)
                    for seite in pdf_leser.pages:
                        text = seite.extract_text()
                        if text:
                            gesammeltes_wissen += text + "\n"
            except Exception as e:
                st.error(f"Konnte {dateiname} nicht lesen: {e}")
                
    if not gesammeltes_wissen:
         return "Fehler: Es konnte kein Text aus den PDFs extrahiert werden."
         
    return gesammeltes_wissen

# Wissen einmalig laden
mein_wissen = lade_wissen_aus_pdfs("dokumente")

# 3. Die System-Anweisung
system_regeln = f"""
Du bist ein direkter und hilfreicher Assistent der Luftsportgemeinschaft Hotzenwald e.V. 
Antworte immer kurz und prägnant.
Nutze AUSSCHLIESSLICH das folgende Wissen für deine Antworten. Wenn die Antwort nicht im Text steht, sage das ehrlich.

WISSENSBASIS:
{mein_wissen}
"""

# 4. Das Modell initiieren
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_regeln
)

# 5. Webseite aufbauen
st.title("Luftsportgemeinschaft Hotzenwald FAQ")

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
        with st.spinner("Daten werden ermittelt..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                st.markdown(response.text)
            except Exception as e:
                if "429" in str(e):
                    st.warning("Unsere KI macht gerade eine kleine Verschnaufpause, da zu viele Fragen gleichzeitig gestellt wurden. Bitte warte etwa eine Minute und versuche es noch einmal! ⏱️")
                else:
                    st.error(f"Fehler bei der Anfrage: {e}")

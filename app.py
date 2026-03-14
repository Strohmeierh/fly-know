import streamlit as st
from google import genai
from google.genai import types

# 1. API Key sicher laden und neuen Client initialisieren
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. Die System-Anweisung aus der Datei Prompt.txt laden
try:
    with open("Prompt.txt", "r", encoding="utf-8") as datei:
        system_regeln = datei.read()
except FileNotFoundError:
    system_regeln = "Du bist ein hilfreicher Flugwetter-Berater."
    st.error("Fehler: Die Datei Prompt.txt wurde nicht gefunden. Bitte erstelle sie im selben Verzeichnis.")

# 3. Webseite aufbauen
st.set_page_config(page_title="Huberts KI-Flugwetter", page_icon="🛩️", layout="wide")

# --- NEU: Seitenleiste (Sidebar) für Einstellungen und Schnellzugriffe ---
with st.sidebar:
    st.header("⚙️ Steuerung")
    
    # Button zum Leeren des Chat-Verlaufs
    if st.button("🗑️ Neues Briefing (Chat leeren)", use_container_width=True):
        st.session_state.messages = []
        st.rerun() # Lädt die Seite neu
        
    st.divider()
    
    st.header("📍 Schnell-Briefings")
    st.markdown("Klicke auf einen Button, um direkt eine Abfrage zu starten:")
    
    # Variablen für die Schnell-Buttons
    quick_prompt = None
    if st.button("Wetter Ossingen (Heute)", use_container_width=True):
        quick_prompt = "Gib mir ein detailliertes VFR- und Segelflug-Briefing für Ossingen und Umgebung für den heutigen Tag."
    if st.button("Wochenende: Thermik-Ausblick", use_container_width=True):
        quick_prompt = "Wie sieht der Ausblick für das kommende Wochenende in der Nordschweiz aus? Fokus auf Hochdruckeinfluss und Segelflug-Thermik."
    if st.button("METAR/TAF Zürich (LSZH)", use_container_width=True):
        quick_prompt = "Bitte rufe das aktuellste METAR und TAF für LSZH (Zürich) ab und übersetze es in ein klares VFR-Briefing."

# --- Hauptbereich ---
st.title("🛩️ Huberts KI-Flugwetter")
st.markdown("Gib einen Ort, einen ICAO-Code oder eine Flugstrecke ein. Die KI sucht über das Internet nach aktuellen Daten und erstellt ein fundiertes Briefing.")

# 4. Verlauf als einfache Liste speichern 
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Bisherigen Verlauf anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Das Eingabefeld für Ort/Flugstrecke
chat_input_text = st.chat_input("Beispiel: Wie wird das Wetter für einen VFR Flug rund um Ossingen morgen Vormittag?")

# Kombinieren von manueller Eingabe ODER Klick auf einen Sidebar-Button
active_prompt = chat_input_text or quick_prompt

if active_prompt:
    
    # Nutzer-Nachricht anzeigen und speichern
    st.chat_message("user").markdown(active_prompt)
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    
    # KI-Antwort generieren
    with st.chat_message("assistant"):
        try:
            with st.spinner("Wetterdaten werden live gesucht und analysiert... 📡"):
                
                # Vorherige Nachrichten für den Kontext sammeln
                gemini_verlauf = []
                for m in st.session_state.messages:
                    g_role = "user" if m["role"] == "user" else "model"
                    nachrichten_teil = types.Part.from_text(text=m["content"])
                    nachrichten_paket = types.Content(role=g_role, parts=[nachrichten_teil])
                    gemini_verlauf.append(nachrichten_paket)
                    
                # Websuche für Echtzeitdaten aktivieren
                config = types.GenerateContentConfig(
                    system_instruction=system_regeln,
                    tools=[{"google_search": {}}],  
                    temperature=0.3 
                )
                
                # Anfrage an das Modell senden
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_verlauf,
                    config=config
                )
                
            # Antwort anzeigen und speichern
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("Unsere KI macht gerade eine kleine Verschnaufpause (Rate Limit). Bitte warte kurz! ⏱️")
            else:
                st.error(f"Fehler bei der Anfrage: {e}")

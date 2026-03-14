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

# 3. Webseite aufbauen (Mobile-optimiert)
# "centered" sorgt dafür, dass es auf dem Desktop gut lesbar bleibt und sich auf dem Handy perfekt einpasst.
st.set_page_config(page_title="KI Flugwetter Hubert", page_icon="🛩️", layout="centered")

# Kopfbereich mit Titel und Löschen-Button nebeneinander
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛩️ KI Flugwetter Hubert")
with col2:
    st.write("") # Etwas Abstand
    if st.button("🗑️ Reset", use_container_width=True, help="Chat leeren"):
        st.session_state.messages = []
        st.rerun()

st.markdown("Gib einen Ort, einen ICAO-Code oder eine Flugstrecke ein. Die KI sucht über das Internet nach aktuellen Daten und erstellt ein fundiertes Briefing.")

# --- Mobile-freundliche Schnellzugriffe (Expander statt Sidebar) ---
quick_prompt = None
with st.expander("📍 Schnell-Briefings (Hier tippen zum Ausklappen)", expanded=False):
    st.markdown("Tippe auf einen Button, um direkt eine Abfrage zu starten:")
    
    # Buttons untereinander (ideal für die Touch-Bedienung auf Handys)
    if st.button("EDSF (Hütten-Hotzenwald)", use_container_width=True):
        quick_prompt = "Bitte gib mir ein aktuelles VFR- und Segelflug-Briefing für den Flugplatz Hütten-Hotzenwald (EDSF). Achte besonders auf lokale Gegebenheiten im Hotzenwald."
    if st.button("LSZK (Speck Fehraltorf)", use_container_width=True):
        quick_prompt = "Bitte rufe die aktuellen Wetterdaten für den Flugplatz Speck in Fehraltorf (LSZK) ab und erstelle ein präzises VFR-Briefing."
    if st.button("Wangen bei Dübendorf", use_container_width=True):
        quick_prompt = "Bitte gib mir eine allgemeine, detaillierte Wettervorhersage für Wangen bei Dübendorf. Da dies kein Flugplatz ist, brauche ich hier nur das allgemeine Lokalwetter (Temperatur, Wind, Niederschlag, allgemeine Bewölkung) ohne spezielles VFR-Briefing."
    if st.button("Thermik: Schwarzwald & Alb", use_container_width=True):
        quick_prompt = "Erstelle eine detaillierte Thermikprognose für den Schwarzwald und die Schwäbische Alb für heute und morgen. Bewerte die thermische Güte, die erwartete Basis der Cumuluswolken, mögliche Inversionen und warne vor potenziellen Überentwicklungen oder großflächiger Abschirmung."

st.divider()

# 4. Verlauf als einfache Liste speichern 
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Bisherigen Verlauf anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Das Eingabefeld für Ort/Flugstrecke (bleibt auf Handys automatisch unten haften)
chat_input_text = st.chat_input("Ort, ICAO-Code oder Flugstrecke eingeben...")

# Kombinieren von manueller Eingabe ODER Klick auf einen Schnell-Button
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

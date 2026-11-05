import os

import httpx
import streamlit as st

# Lokalt kører API'en på 127.0.0.1. I Docker sættes API_URL til http://api:5000,
# fordi containerne finder hinanden via service-navnet i docker-compose.yml.
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")
TIMEOUT = 2  # sekunder


def call_api(method, path, json=None):
    """Kald API'en. Returnér response ved succes - ellers vis en st.error og returnér None."""
    try:
        response = httpx.request(method, f"{API_URL}{path}", json=json, timeout=TIMEOUT)
        response.raise_for_status()  # 4xx/5xx -> httpx.HTTPStatusError
        return response
    # ConnectTimeout er med, fordi Windows kan bruge et par sekunder på at afvise en lukket port
    except (httpx.ConnectError, httpx.ConnectTimeout):
        st.error(f"Kan ikke få forbindelse til API'en på {API_URL}. Kører den?")
    except httpx.TimeoutException:  # forbindelsen var der, men svaret kom ikke i tide
        st.error(f"API'en svarede ikke inden for {TIMEOUT} sekunder. Prøv igen om lidt.")
    except httpx.HTTPStatusError as e:
        # Vis API'ens egen fejlbesked fra {"error": "..."}, ikke kun statuskoden
        message = e.response.json()["error"]
        st.error(f"Fejl {e.response.status_code}: {message}")
    except httpx.RequestError as e:  # alle andre netværksfejl
        st.error(f"Noget gik galt i kaldet til API'en: {e}")
    return None


st.set_page_config(page_title="Fredagsbaren")
st.title("Fredagsbarens events")

# --- Mit navn (sidebar) ---
# key="name" gør, at værdien gemmes i st.session_state.name og huskes mellem kørsler
if "name" not in st.session_state:
    st.session_state.name = ""
st.sidebar.text_input("Dit navn", key="name")
name = st.session_state.name.strip()

# Besked fra en handling i forrige kørsel (se st.rerun() længere nede)
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

# --- Oversigt ---
# Streamlit kører hele scriptet forfra ved hvert klik, så vi henter frisk data hver gang.
response = call_api("GET", "/events")
if response is None:
    st.stop()  # uden data giver resten af siden ikke mening
events = response.json()

st.header("Oversigt")
rows = [
    {
        "Titel": event["title"],
        "Dato": event["date"],
        "Tilmeldte": len(event["participants"]),
        "Ledige pladser": event["capacity"] - len(event["participants"]),
    }
    for event in events
]
st.dataframe(rows, hide_index=True)

# --- Tilmeld og afmeld ---
st.header("Tilmeld og afmeld")
if not events:
    st.info("Der er ingen events endnu. Opret et herunder.")
else:
    # En tekst pr. event til selectbox'en. labels[i] hører til events[i],
    # så vi kan finde det valgte event via dets plads i listen.
    labels = [f"{event['title']} ({event['date']})" for event in events]
    selected = st.selectbox("Vælg et event", labels)
    event = events[labels.index(selected)]
    event_id = event["id"]
    free = event["capacity"] - len(event["participants"])

    if event["participants"]:
        participants_text = ", ".join(event["participants"])
    else:
        participants_text = "ingen endnu"
    st.write(f"**Deltagere ({len(event['participants'])}/{event['capacity']}):** {participants_text}")

    if free <= 0:
        st.warning("Eventet er fuldt.")
    if not name:
        st.info("Skriv dit navn i sidebaren for at tilmelde eller afmelde dig.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tilmeld", disabled=free <= 0 or not name):
            if call_api("POST", f"/events/{event_id}/signups", json={"name": name}) is not None:
                st.session_state.message = f"{name} er tilmeldt {event['title']}"
                st.rerun()  # kør forfra, så oversigten viser det nye antal
    with col2:
        if st.button("Afmeld", disabled=not name):
            if call_api("DELETE", f"/events/{event_id}/signups/{name}") is not None:
                st.session_state.message = f"{name} er afmeldt {event['title']}"
                st.rerun()

# --- Opret event ---
st.header("Opret event")
with st.form("create_event", clear_on_submit=True):
    title = st.text_input("Titel")
    date = st.date_input("Dato")
    capacity = st.number_input("Antal pladser", min_value=1, step=1, value=10)
    submitted = st.form_submit_button("Opret")

if submitted:
    new_event = {"title": title, "date": date.isoformat(), "capacity": int(capacity)}
    if call_api("POST", "/events", json=new_event) is not None:
        st.session_state.message = f"{title} er oprettet"
        st.rerun()

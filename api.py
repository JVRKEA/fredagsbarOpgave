import os

from flask import Flask, request

app = Flask(__name__)

# "Database": en liste af events, hvor hvert event har navngivne felter (title, date osv.).
# Den ligger kun i hukommelsen, så alt nyt forsvinder, når API'en genstartes.
events = [
    {"id": 1, "title": "Quizaften", "date": "2026-11-13", "capacity": 3, "participants": ["Anna", "Bo"]},
    {"id": 2, "title": "Brætspilsaften", "date": "2026-11-20", "capacity": 8, "participants": []},
    {"id": 3, "title": "Beerpong-turnering", "date": "2026-11-27", "capacity": 2, "participants": ["Carl", "Dorte"]},
]


def find_event(event_id):
    """Returnér eventet med det id, eller None hvis det ikke findes."""
    for event in events:
        if event["id"] == event_id:
            return event
    return None


def not_found(event_id):
    return {"error": f"Intet event med id {event_id}"}, 404


@app.get("/events")                                  # hent alle events
def get_events():
    return events


@app.get("/events/<int:event_id>")                   # hent et event
def get_event(event_id):
    event = find_event(event_id)
    if event is None:
        return not_found(event_id)
    return event


@app.post("/events")                                 # opret et event
def create_event():
    data = request.get_json(silent=True)             # silent=True: None i stedet for fejl ved ugyldig JSON
    if not data or not data.get("title") or not data.get("date") or "capacity" not in data:
        return {"error": "title, date og capacity er påkrævet"}, 400

    capacity = data["capacity"]
    if not isinstance(capacity, int) or capacity <= 0:
        return {"error": "capacity skal være et positivt heltal"}, 400

    new_event = {
        "id": max((e["id"] for e in events), default=0) + 1,
        "title": data["title"],
        "date": data["date"],
        "capacity": capacity,
        "participants": [],
    }
    events.append(new_event)
    return new_event, 201                            # 201 Created


@app.post("/events/<int:event_id>/signups")          # tilmeld en person
def signup(event_id):
    event = find_event(event_id)
    if event is None:
        return not_found(event_id)

    data = request.get_json(silent=True)
    if not data or not data.get("name"):
        return {"error": "name er påkrævet"}, 400

    name = data["name"]
    if name in event["participants"]:
        return {"error": f"{name} er allerede tilmeldt"}, 409      # 409 Conflict
    if len(event["participants"]) >= event["capacity"]:
        return {"error": f"{event['title']} er fuldt"}, 409

    event["participants"].append(name)
    return event, 201


@app.delete("/events/<int:event_id>/signups/<name>")  # afmeld en person
def cancel_signup(event_id, name):
    event = find_event(event_id)
    if event is None:
        return not_found(event_id)
    if name not in event["participants"]:
        return {"error": f"{name} er ikke tilmeldt {event['title']}"}, 404

    event["participants"].remove(name)
    return "", 204                                   # 204 No Content: succes, men ingen body


@app.delete("/events/<int:event_id>")                # slet et event
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return not_found(event_id)
    events.remove(event)
    return "", 204


if __name__ == "__main__":
    # Lokalt lytter vi kun på 127.0.0.1. I Docker sættes FLASK_HOST=0.0.0.0,
    # så den anden container (og værtsmaskinen) kan nå API'en.
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=True)

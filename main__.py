from fastapi import FastAPI
from datetime import datetime

fake_daten = [
    {"Zeit": "2024-04-01T10:00", "Ort": "Bahnhof", "Kinder": 20, "Erwachsene": 100},
    {"Zeit": "2024-04-01T11:00", "Ort": "Postplatz", "Kinder": 40, "Erwachsene": 130},
    {"Zeit": "2024-04-01T12:00", "Ort": "Einkaufszentrum", "Kinder": 15, "Erwachsene": 80}
]



app = FastAPI()

@app.get("/analyse/kinder_anteil")
def kinder_anteil(
    analyseort: str
):
    # Filter nach Ort
    filter = []
    for zeile in fake_daten:
        if zeile["Ort"] == analyseort:
            filter.append(zeile)

    # Für jedes Element den Kinderanteil berechnen
    resultat = []
    for zeile in filter:
        total = zeile["Kinder"] + zeile["Erwachsene"]
        anteil = zeile["Kinder"] / total 
        resultat.append({
            "Zeit": zeile["Zeit"],
            "kinder_anteil": anteil
        })
    return resultat
# -------------------------
# Endpunkt: Locations
# -------------------------
@app.get("/orte")
def get_orte():
    orte = []
    for zeile in fake_daten:
        ort = zeile["Ort"]
        if ort not in orte:
            orte.append(ort)
    return orte



# debugger (FastAPI) starten -> auf link klicken
# im Browser Endpunkte ausprobieren: /orte oder /analyse/kinder_anteil?analyseort=Bahnhof


#@app.get("/greet")
#def greet_user(name: str | None = None):
#    test = 42 
#    return f"Hello {name}!"
#im Server /docs aufrufen, um die API-Dokumentation zu sehen die Automatisch erstellt wirdfast
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import csv

# CSV-Daten laden
daten = []
with open("Gesamtdatensatz.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for z in reader:
        z["child_pedestrians_count"] = int(z["child_pedestrians_count"])
        z["adult_pedestrians_count"] = int(z["adult_pedestrians_count"])
        z["temperature"] = float(z["temperature"])
        daten.append(z)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://projektarbeit-git-main-melanies-projects-3f1f17b6.vercel.app"
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Monatsnamen
month_names = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# Endpoints
@app.get("/orte")
def get_orte():
    orte = []
    for z in daten:
        if z["location_name"] not in orte:
            orte.append(z["location_name"])
    return orte

@app.get("/analyse/kinderanteil_monat")
def kinderanteil_monat(analyseort: str, jahr: int, tempCheck: bool = False):
    gefiltert = []
    for z in daten:
        if z["location_name"] == analyseort and z["timestamp"].startswith(str(jahr)):
            gefiltert.append(z)

    # Leeres Dict für alle 12 Monate
    agg = {}
    for m in range(1, 13):
        agg[m] = {"child": 0, "adult": 0, "temp_sum": 0, "temp_count": 0}

    # Dict mit Werten füllen
    for z in gefiltert:
        m = datetime.fromisoformat(z["timestamp"]).month
        agg[m]["child"] += z["child_pedestrians_count"]
        agg[m]["adult"] += z["adult_pedestrians_count"]
        if tempCheck:
            agg[m]["temp_sum"] += z["temperature"]
            agg[m]["temp_count"] += 1

    # Ergebnisliste erstellen
    result = []
    for m in range(1, 13):
        total = agg[m]["child"] + agg[m]["adult"]
        if total > 0:
            anteil = agg[m]["child"] / total
        else:
            anteil = 0

        if tempCheck:
            temp = round(agg[m]["temp_sum"] / agg[m]["temp_count"], 1)
        else:
            temp = None

        result.append({
            "month_name": month_names[m-1],
            "child": agg[m]["child"],
            "adult": agg[m]["adult"],
            "anteil": anteil,
            "temperature": f"{temp} °C"
        })

    return result

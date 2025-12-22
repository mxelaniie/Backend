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

# Monatsnamen für Anzeige
month_names = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# Endpunkte
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

    # Aggregation pro Monat
    agg = {}
    for m in range(1, 13):
        agg[m] = {"child": 0, "adult": 0, "temp_sum": 0, "temp_count": 0}

    for z in gefiltert:
        m = datetime.fromisoformat(z["timestamp"]).month
        agg[m]["child"] += z["child_pedestrians_count"]
        agg[m]["adult"] += z["adult_pedestrians_count"]
        if tempCheck:
            agg[m]["temp_sum"] += z["temperature"]
            agg[m]["temp_count"] += 1

    result = []
    for m in range(1, 13):
        total = agg[m]["child"] + agg[m]["adult"]
        anteil = agg[m]["child"] / total if total > 0 else 0
        temp = (agg[m]["temp_sum"] / agg[m]["temp_count"]) if tempCheck and agg[m]["temp_count"] else None
        result.append({
            "month_name": month_names[m-1],
            "child": agg[m]["child"],
            "adult": agg[m]["adult"],
            "anteil": anteil,
            "temperature": f"{temp}°C" if temp is not None else None
        })
    return result

@app.get("/analyse/temperaturen")
def temperaturen(analyseort: str):
    gefiltert = [z for z in daten if z["location_name"] == analyseort]
    temp_map = {}

    for z in gefiltert:
        dt = datetime.fromisoformat(z["timestamp"])
        key = (dt.year, dt.month)
        if key not in temp_map:
            temp_map[key] = {"sum": 0, "count": 0}
        temp_map[key]["sum"] += z["temperature"]
        temp_map[key]["count"] += 1

    result = []
    for (year, month), vals in sorted(temp_map.items()):
        result.append({
            "year": year,
            "month": month,
            "value": vals["sum"] / vals["count"]
        })
    return result

@app.get("/analyse/kinder_anteil_max")
def kinder_anteil_max(analyseort: str):
    gefiltert = [z for z in daten if z["location_name"] == analyseort]
    max_anteil, max_ts = 0, None

    for z in gefiltert:
        total = z["child_pedestrians_count"] + z["adult_pedestrians_count"]
        if total == 0:
            continue
        anteil = z["child_pedestrians_count"] / total
        if anteil > max_anteil:
            max_anteil, max_ts = anteil, z["timestamp"]

    return {
        "location_name": analyseort,
        "max_child_anteil": max_anteil,
        "timestamp": max_ts
    }

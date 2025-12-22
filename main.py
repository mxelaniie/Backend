from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import csv

# -------------------------
# CSV-Daten laden
# -------------------------
daten = []
with open("Gesamtdatensatz.csv", "r", encoding="utf-8") as datei:
    reader = csv.DictReader(datei)
    for zeile in reader:
        # Zähler in int umwandeln
        zeile["child_pedestrians_count"] = int(zeile["child_pedestrians_count"])
        zeile["adult_pedestrians_count"] = int(zeile["adult_pedestrians_count"])
        # Temperatur optional in float
        if zeile.get("temperature"):
            try:
                zeile["temperature"] = float(zeile["temperature"])
            except ValueError:
                zeile["temperature"] = None
        daten.append(zeile)

# -------------------------
# FastAPI initialisieren
# -------------------------
app = FastAPI()

# CORS konfigurieren
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://projektarbeit-git-main-melanies-projects-3f1f17b6.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Monatsnamen für Anzeige
month_names = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# -------------------------
# Endpunkte
# -------------------------

@app.get("/orte")
def get_orte():
    """Gibt alle Orte zurück"""
    orte = list({z["location_name"] for z in daten})
    return sorted(orte)


@app.get("/analyse/kinderanteil_monat")
def kinderanteil_monat(analyseort: str, jahr: int, tempCheck: bool = False):
    """Aggregiert Kinderanteil pro Monat für ein Jahr und optional Temperatur"""
    gefiltert = [
        z for z in daten
        if z["location_name"] == analyseort and z["timestamp"].startswith(str(jahr))
    ]

    agg_map = {}
    for z in gefiltert:
        try:
            dt = datetime.fromisoformat(z["timestamp"])
        except ValueError:
            continue
        month = dt.month
        if month not in agg_map:
            agg_map[month] = {"child": 0, "adult": 0, "temperature_sum": 0, "temperature_count": 0}
        agg_map[month]["child"] += z["child_pedestrians_count"]
        agg_map[month]["adult"] += z["adult_pedestrians_count"]
        if tempCheck and z.get("temperature") is not None:
            agg_map[month]["temperature_sum"] += z["temperature"]
            agg_map[month]["temperature_count"] += 1

    result = []
    for month in range(1, 13):
        data = agg_map.get(month, {"child": 0, "adult": 0, "temperature_sum": 0, "temperature_count": 0})
        total = data["child"] + data["adult"]
        anteil = data["child"] / total if total > 0 else 0
        temperature = (
            round(data["temperature_sum"] / data["temperature_count"], 1)
            if tempCheck and data["temperature_count"] > 0 else None
        )
        result.append({
            "month_name": month_names[month - 1],
            "child": data["child"],
            "adult": data["adult"],
            "anteil": anteil,
            "temperature": f"{temperature}°C" if temperature is not None else None
        })

    return result


@app.get("/analyse/temperaturen")
def temperaturen(analyseort: str):
    """Durchschnittliche Temperatur pro Monat für einen Ort"""
    gefiltert = [z for z in daten if z["location_name"] == analyseort]

    temp_map = {}
    for z in gefiltert:
        ts = z["timestamp"]
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            continue

        year = dt.year
        month = dt.month
        value = z.get("temperature")
        if value is None:
            continue

        key = (year, month)
        if key not in temp_map:
            temp_map[key] = {"sum": 0.0, "count": 0}
        temp_map[key]["sum"] += value
        temp_map[key]["count"] += 1

    result = [
        {"year": year, "month": month, "value": temp_map[(year, month)]["sum"] / temp_map[(year, month)]["count"]}
        for (year, month) in sorted(temp_map.keys())
    ]

    return result


@app.get("/analyse/kinder_anteil_max")
def kinder_anteil_max(analyseort: str):
    """Gibt den Zeitpunkt mit maximalem Kinderanteil zurück"""
    gefiltert = [z for z in daten if z["location_name"] == analyseort]

    max_anteil = 0
    max_zeitpunkt = None

    for z in gefiltert:
        child = z["child_pedestrians_count"]
        adult = z["adult_pedestrians_count"]
        total = child + adult
        if total == 0:
            continue
        anteil = child / total
        if anteil > max_anteil:
            max_anteil = anteil
            max_zeitpunkt = z["timestamp"]

    return {
        "location_name": analyseort,
        "max_child_anteil": max_anteil,
        "timestamp": max_zeitpunkt
    }

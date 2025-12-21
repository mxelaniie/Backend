# Frage:
# Wann (Zeitraum) ist der Anteil der Kinder im Vergleich zu den erwachsenen Fussgängern
# (Anteil/Zählung) am grössten an der Bahnhofstrasse Mitte (Ort)?

from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import json
from urllib.parse import unquote
import csv


# Datenimport
daten = []
with open("Gesamtdatensatz.csv", "r", encoding="utf-8") as datei:
    reader = csv.DictReader(datei)  # liest CSV als Dict
    for zeile in reader:
        # Optional: falls die Zahlen als Strings kommen, in int umwandeln
        zeile["child_pedestrians_count"] = int(zeile["child_pedestrians_count"])
        zeile["adult_pedestrians_count"] = int(zeile["adult_pedestrians_count"])
        daten.append(zeile)

app = FastAPI()

# header festlegen, damit Frontend zugreifen kann
origins = [
    "http://localhost:5173",
    "http://localhost:5174", # falls zwei laufen
    "https://projektarbeit-git-main-melanies-projects-3f1f17b6.vercel.app" # für vercel Deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Endpunkte definieren
@app.get("/analyse/kinder_anteil")
def kinder_anteil(analyseort: str):
    gefiltert = []
    for zeile in daten:
        if zeile["location_name"] == analyseort:
            gefiltert.append(zeile)

    resultat = []
    for z in gefiltert:
        child = z["child_pedestrians_count"]
        adult = z["adult_pedestrians_count"]
        

        # Sinnvolle Infos zurückgeben
        resultat.append({
            "timestamp": z.get("timestamp"),
            "location_name": z.get("location_name"),
            "child": child,
            "adult": adult,
        })

    return resultat


@app.get("/orte")
def get_orte():
    orte = []
    for zeile in daten:
        ort = zeile["location_name"]
        if ort not in orte:
            orte.append(ort)
    return orte

@app.get("/analyse/temperaturen")
def temperaturen(analyseort: str):
    """
    Gibt die durchschnittliche Temperatur pro Monat für einen Ort zurück.
    Rückgabe: [{"year": 2025, "month": 1, "value": 5.2}, ...]
    """
    gefiltert = [z for z in daten if z["location_name"] == analyseort]

    # Map für Jahr+Monat: summe + count
    temp_map = {}  # key: (year, month) -> {"sum": ..., "count": ...}

    for z in gefiltert:
        ts = z["timestamp"]
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            continue

        year = dt.year
        month = dt.month

        value = z.get("temperature")
        if value is None or value == "":
            continue

        try:
            value = float(value)
        except ValueError:
            continue

        key = (year, month)
        if key not in temp_map:
            temp_map[key] = {"sum": 0.0, "count": 0}
        temp_map[key]["sum"] += value
        temp_map[key]["count"] += 1

    # Durchschnitt berechnen
    result = [
        {"year": year, "month": month, "value": temp_map[(year, month)]["sum"] / temp_map[(year, month)]["count"]}
        for (year, month) in sorted(temp_map.keys())
    ]

    return result


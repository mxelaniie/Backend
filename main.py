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


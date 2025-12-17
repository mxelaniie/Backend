import fastapi

app = fastapi()

CORSmiddleware = middleware(origins, allowed_methods)

app.useMiddleware(CORSmiddleware)

pesestrian_count = pandas.read_csv("Datensatz.csv")
# correct timestamp data types
"http://localhost:1234/api/va/data"
#fetch(`http://localhost:1234/api/v1/dataendpoint/pfadparameter1?quryparam=${foobar}`)

@app.get("/api/v1/date")
def get_data(param):
    #data json
    filtered_data = pedestrian_count.query("meine Query anhand der Parameter")
    filtered_data[["spalte1", "spalte2"]].to_json()
    returrn data

# bei header der response muss umbedingt corse gesettet werden sonst funktioniert das mit dem usemiddleware nicht
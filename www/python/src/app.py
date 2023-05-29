from flask import Flask, render_template, request, jsonify
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def run_sparql_query(locIDs):
    all_results = []
    for chunk in chunks(locIDs, 400):
        print(len(chunk))
        locIDs_values = " ".join(f'"{id}"' for id in chunk)
        sparql.setQuery(
            f"""
            SELECT ?item ?locId ?image
            WHERE 
            {{
                VALUES ?locId {{ {locIDs_values} }}
                ?item wdt:P5200 ?locId.
                OPTIONAL {{ ?item wdt:P18 ?image. }}
            }}
        """
        )
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        all_results.extend(results["results"]["bindings"])
    return all_results


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/map", methods=["GET"])
def map():
    lat = request.args.get("lat", "")
    lng = request.args.get("lng", "")
    dist = request.args.get("dist", "25")
    ebird_api_url = f"https://api.ebird.org/v2/ref/hotspot/geo?lat={lat}&lng={lng}&dist={dist}&fmt=json"
    response = requests.get(ebird_api_url)
    data = response.json()
    locIDs = [item["locId"] for item in data]
    wikidata_results = run_sparql_query(locIDs)

    # create a dictionary for easier access
    wikidata_dict = {
        result["locId"]["value"]: {
            "wikidata": result["item"]["value"],
            "image": result.get("image", {}).get("value"),
        }
        for result in wikidata_results
    }

    # iterate through the data to add Wikidata information
    for item in data:
        if item["locId"] in wikidata_dict:
            wikidata_info = wikidata_dict[item["locId"]]
            item["wikidata"] = wikidata_info["wikidata"]
            item["image"] = wikidata_info["image"] if wikidata_info["image"] else None
        else:
            item["wikidata"] = None
            item["image"] = None

    return render_template("map.html", data=data, lat=lat, lng=lng)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)

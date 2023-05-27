from flask import Flask, render_template, request, jsonify
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

def run_sparql_query(locIDs):
    locIDs_values = ' '.join(f'"{id}"' for id in locIDs)
    sparql.setQuery(f"""
        SELECT ?item ?locId
        WHERE 
        {{
            VALUES ?locId {{ {locIDs_values} }}
            ?item wdt:P5200 ?locId.
        }}
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/map', methods=['GET'])
def map():
    lat = request.args.get('lat', '')
    lng = request.args.get('lng', '')
    ebird_api_url = f"https://api.ebird.org/v2/ref/hotspot/geo?lat={lat}&lng={lng}&fmt=json"
    response = requests.get(ebird_api_url)
    data = response.json()

    locIDs = [item['locId'] for item in data]
    wikidata_results = run_sparql_query(locIDs)

    # create a dictionary for easier access
    wikidata_dict = {result['locId']['value']: result['item']['value'] for result in wikidata_results}

    # iterate through the data to add wikidata information
    for item in data:
        if item['locId'] in wikidata_dict:
            item['wikidata'] = wikidata_dict[item['locId']]
        else:
            item['wikidata'] = None

    return render_template('map.html', data=data, lat=lat, lng=lng)

if __name__ == '__main__':
    app.run(debug=True)

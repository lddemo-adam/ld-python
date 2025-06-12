# Flask container for Python LaunchDarkly Demo
# Adam Smith <lddemo@adamooo.com>
# original structure derived from https://code.visualstudio.com/docs/python/tutorial-flask
# POTA JSON data access and handling derived from: https://www.kc8jc.com/2023/02/02/simple-pota-hunter-script/

import re
from datetime import datetime

from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/spots/")
@app.route("/spots/mode/<mode>")
@app.route("/spots/locs/<locations>")
@app.route("/spots/mode/<mode>/locs/<locations>")
@app.route("/spots/locs/<locations>/mode/<mode>")
def spots(mode=None, locations="US-"): # default to no mode filter and all US locations :)
    import json
    import requests

    response = requests.get("https://api.pota.app/spot/activator")
    spots = json.loads(response.text)

    my_targets = locations

    filtered_spots = []
    for spot in spots:
        if mode is None or spot["mode"] == mode:
            #if spot["locationDesc"] in my_targets:
            #if any (re.match(rf"\b{target}\b", spot["locationDesc"]) for target in my_targets.split(",")):                
            for target in my_targets.split(","):
                # Check if the spot's location matches any of the specified (or default) locations
                if re.match(rf"\b{target}\b", spot["locationDesc"]):
                    # If it does, add it to the filtered list
                    filtered_spots.append(spot)
                    break

    return render_template(
        "spots.html",
        count=len(spots),
        selected=len(filtered_spots),
        spots=filtered_spots,
        mode=mode,
        locs=locations,
        date=datetime.now()
    )

@app.route("/about/")
def about():
    return "This demonstration app queries the public Parks On The Air API for activator spots and displays them based on the selected mode. You can filter by mode or see all spots."

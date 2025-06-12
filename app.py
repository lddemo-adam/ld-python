# Flask container for Python LaunchDarkly Demo
# Adam Smith <lddemo@adamooo.com>
# Flask app structure derived from https://code.visualstudio.com/docs/python/tutorial-flask
# POTA JSON data access and handling derived from: https://www.kc8jc.com/2023/02/02/simple-pota-hunter-script/
# LaunchDarkly Python SDK tutorial: https://launchdarkly.com/docs/sdk/server-side/python

import re
from datetime import datetime

from flask import Flask
from flask import render_template

import ldclient
from ldclient.config import Config
from ldclient import Context

# LaunchDarkly SDK setup - substitute with your own SDK key and feature flag key
# SDK keys for demo: Test environment: sdk-fad800e4-2188-45ce-aac0-27a022667260
#                   Production environment: sdk-bd1e3e0d-121d-4166-aacb-5757ec9efbfb
sdk_key = "sdk-fad800e4-2188-45ce-aac0-27a022667260"
# Feature flag key for demo: demo-feature
feature_flag_key = "demo-feature"

if __name__ == "__main__":
    if not sdk_key:
        print("*** Please set the SDK key in code before running the demo")
        exit()
    if not feature_flag_key:
        print("*** Please set the flag key in code before running the demo")
        exit()

    ldclient.set_config(Config(sdk_key))

    # check that the SDK  initialized successfully
    if not ldclient.get().is_initialized():
        print("*** SDK failed to initialize. Please check your internet connection and SDK credential for any typo.")
        exit()
    print("*** SDK successfully initialized")

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

@app.route("/test/flag")
def test_flag():
    ldclient.set_config(Config(sdk_key))
    # check that the SDK  initialized successfully
    if not ldclient.get().is_initialized():
        print("*** SDK failed to initialize. Please check your internet connection and SDK credential for any typo.")
        exit()
    print("*** SDK successfully initialized")

    # Set up the evaluation context. This context should appear on your
    # LaunchDarkly contexts dashboard soon after you run the demo.
    context = \
        Context.builder('example-user-key').kind('user').name('Demo User').build()

    flag_value = ldclient.get().variation(feature_flag_key, context, False)
    
    return f"Flag name: \"{feature_flag_key}\" has value: \"{flag_value}\""

@app.route("/about/")
def about():
    return "This demonstration app queries the public Parks On The Air API for activator spots and displays them based on the selected mode. You can filter by mode or see all spots."

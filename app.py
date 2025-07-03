# Flask container for Python LaunchDarkly Demo
# Adam Smith <lddemo@adamooo.com>
# Flask app structure derived from https://code.visualstudio.com/docs/python/tutorial-flask
# POTA JSON data access and handling derived from: https://www.kc8jc.com/2023/02/02/simple-pota-hunter-script/
# LaunchDarkly Python SDK tutorial: https://launchdarkly.com/docs/sdk/server-side/python

import re
import shelve
import atexit

from datetime import datetime

from flask import Flask, request   # NOTE: request is distinct from the requests package used to retrieve POTA.app data in spots()
from flask import render_template

import ldclient
from ldclient.config import Config
from ldclient import Context

### LaunchDarkly SDK setup
# Substitute with your own values if using an alternate LD account or setup from the demo one.
# SDK keys for demo: Test environment: sdk-fad800e4-2188-45ce-aac0-27a022667260
#                   Production environment: sdk-bd1e3e0d-121d-4166-aacb-5757ec9efbfb
# In a real application, you would not hard-code these values but rather use environment variables or a secure vault, etc
sdk_key = "sdk-fad800e4-2188-45ce-aac0-27a022667260"
# Feature flag key (default for demo: "demo-feature" and for beta: "beta-feature"
feature_flag_key = "demo-feature"
beta_flag_key =  "beta-feature"
# Client side ID for JS in active page.  Test env "6849a0b7a955ff0926acc10e", Production env "6849a0b7a955ff0926acc10f"
client_side_id = "6849a0b7a955ff0926acc10e"
# API access token - in a real application this would probably be created as a Service token in LD,
# and would definitely be stored and injected more securely into a trusted integration/admin app.
api_token = "api-c6bf94c3-6c7d-4089-bdb0-ab784558ed71"
# Additional keys for API requests - specify the Project and Environment
project_key =  "default"    # e.g.  "default"
env_key = "test"            # e.g. "test" or "production"

###
### Functions for LaunchDarkly SDK access and handling setup/termination of the app
###

# Initialize the LD client with the configured SDK key and check that it is ready to use (exit on failure)
def setup_ld_client():
    ldclient.set_config(Config(sdk_key))
    my_client = ldclient.get()
    # check that the SDK  initialized successfully
    if not my_client.is_initialized():
        print("*** SDK failed to initialize. Please check your internet connection and SDK credential for any typo.")
        exit()
    else:
        print("*** SDK successfully initialized")
    return my_client

# Get the value of the demo feature flag for the user name specified in URL parameter "user".  
# For demo purposes, if no user is specified, it defaults to 'Demo User'.
def get_demo_flag():
    return get_flag_val(feature_flag_key)

def get_beta_flag():
    return get_flag_val(beta_flag_key)

def get_flag_val(flag_key = feature_flag_key):
    username = request.args.get('user', 'Demo User')   
    # Set up the evaluation context. If a user name is passed in a query parameter, 
    # use that; otherwise, use a default.
    if (not username): # if no username is provided, default to 'Demo User'
        username = 'Demo User'
        usertype = 'demouser'
    elif username.startswith("Demo"): # usernames starting with "Demo" are given a different usertype
        usertype = 'demouser'
    else:                             #  usernames not starting with "Demo" may get beta functionality
        usertype = 'nameduser'

    # build user and usertype contexts for flag evaluation
    userctx = \
        Context.builder(f"UserKey-Demo-{username}").kind('user').name(username).build()
    typectx = \
        Context.builder(f"TypeKey-Demo-{usertype}").kind('type').name(usertype).build()
    # get the flag value for the given context(s)
    return client.variation(flag_key, Context.create_multi(userctx, typectx), False)

def cleanup_on_exit():
    print("Flask application is shutting down. Performing cleanup...")
    # Add your cleanup logic here, e.g., closing database connections
    app_data.close()  # Close the shelve database


###
### "Main" application code to init LD and start Flask
###

# Check that LaunchDarkly key values are set, and test client initialization; exit on failure
if not sdk_key:
    print("*** Please set the SDK key in code before running the demo")
    exit()
if not feature_flag_key:
    print("*** Please set the flag key in code before running the demo")
    exit()
print(f"*** Using LaunchDarkly SDK key: {sdk_key}")

ldclient.set_config(Config(sdk_key))

# Initialize the LaunchDarkly client to check that connectivity and keys are good
client = setup_ld_client()

# Open a shelf for a small amount of persistent app data
app_data = shelve.open("app_data.db", flag='c', writeback=True)
app_data['runtime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if not 'thumbs_up' in app_data: # if this is the first run, set thumbs-up count to 0
    app_data['thumbs_up'] = 0
if not 'thumbs_down' in app_data: # if this is the first run, set thumbs-down count to 0
    app_data['thumbs_down'] = 0

app = Flask(__name__)
atexit.register(cleanup_on_exit)


###
### Route-specific functions for handling requests
###


@app.route("/spots/")
@app.route("/spots/mode/<mode>")
@app.route("/spots/locs/<locations>")
@app.route("/spots/mode/<mode>/locs/<locations>")
@app.route("/spots/locs/<locations>/mode/<mode>")
def spots(mode=None, locations=""): # default to no mode filter and all locations
    import random
    import json
    import requests   # again note, this is the requests package, not Flask's inbound "request"

    # get an LD client - will exit if network or keys are not set up correctly
    client = ldclient.get()
    # get the value of the demonstration feature flag 
    feature_enabled = get_demo_flag()
    beta_value = get_beta_flag()

    response = requests.get("https://api.pota.app/spot/activator")
    spots = json.loads(response.text)

    my_targets = locations

    filtered_spots = []
    qrt_count = 0;
    for spot in spots:
        if mode is None or spot["mode"] == mode:
            for target in my_targets.split(","):
                # Check if the spot's location matches any of the specified (or default) locations
                if re.search(f",{target}", f",{spot["locationDesc"]}"):
                    # If everything matches, add it to the filtered list
                    # But first, if feature flag turned on then filter out any spots with "QRT" in the comments
                    if(feature_enabled and re.search("qrt",  spot["comments"], re.IGNORECASE)):
                        qrt_count += 1
                    else:
                        filtered_spots.append(spot)
                        # the following is a silly bug introduced under the flagged feature, for demo narrative purposes
                        # it causes random spots to be duplicated in the table when the feature is active
                        if (feature_enabled and (random.randint(1,10) == 10)):
                            filtered_spots.append(spot)
                            print("inserting duplicate spot (intentional bug with feature enabled)")
                    break
    if not feature_enabled: qrt_count = -1;

    return render_template(
        "spots.html",
        count=len(spots),
        selected=len(filtered_spots),
        spots=filtered_spots,
        qrt=qrt_count,
        mode=mode,
        locs=locations,
        date=datetime.now(),
        user=request.args.get('user', 'Demo User'),  # pass user name from URL args, or default value
        client_id=client_side_id,
        beta_val = beta_value
    )

@app.route("/test/flag")
def test_flag():
    # get an LD client - will exit if network or keys are not set up correctly
    client = setup_ld_client()
    # use the client to check the value of the feature flag
    flag_value = get_demo_flag()

    return f"Flag name: \"{feature_flag_key}\" has value: \"{flag_value}\" for user: " + request.args.get('user', 'Demo User')

@app.route("/")
@app.route("/index.html")
@app.route("/about/")
def about():
    return app.send_static_file("about.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/admin/flag/update/")
@app.route("/admin/flag/update/<action>")
def admin_flag_update(p_key = project_key,  f_key = feature_flag_key, token = api_token, action = "none"):
    import json
    import requests   # again note, this is the requests package, not Flask's inbound "request"

    if(action == "turnFlagOn" or action == "turnFlagOff"):
        req_url = f"https://app.launchdarkly.com/api/v2/flags/{p_key}/{f_key}"
        req_headers = {
            "LD-API-Version": "20240415",
            "Authorization": token,
            "Content-Type": "application/json; domain-model=launchdarkly.semanticpatch"
        }
        req_payload = f"{{ \"environmentKey\": \"{env_key}\", \
            \"comment\": \"action via app admin endpoint: {action}\",\
            \"instructions\": \
                [{{ \"kind\": \"{action}\" }}] }}"

        response = requests.patch(req_url, headers=req_headers, data=req_payload)
        result = json.loads(response.text)

        return f"Admin update attempted {action} for flag {f_key}: <br>\
                Response was: <em>{result}</em><br>\
            Debug:<br>\
            {req_url}<br>\
            {req_headers}<br>\
            {req_payload}"
    else:
        return f"To update flag {f_key} add .../turnFlagOn or .../turnFlagOff to URL"
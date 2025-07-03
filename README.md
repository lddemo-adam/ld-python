# LaunchDarkly Demonstration - POTA Spots web app
Public demonstration app for LaunchDarkly Release, Targeting, and Experimentation controls.
By Adam Smith, lddemo@adamooo.com, June 2025
Hosted at: https://github.com/lddemo-adam/ld-python.git
This probably won't get maintained for long.

## BACKGROUND
This app was implemented as a "homework exercise" and is meant as a simple demonstration of various capabilities of LaunchDarkly including Feature Flag based rollout, rollback, remediation, targeting, and Experimentation.  


## TECHNICAL NOTES / PREREQUISITES
I assume system/local installation of recent Python 3, pip, and virtualenv tooling and that the user is generally familiar with these as well as interactions with GitHub to download the demo  files.   Python 3.13.5 used at time of development.  Required (publically available) third party modules include Flask, Requests, and the LaunchDarkly Server SDK (see brief installation notes below).

The app behavior requires internet connectivity to a public website (pota.app).  The LD SDK requires internet connectivity to LaunchDarkly service, and the demo app will exit if not conneted or if incorrect keys are configured.
Data persistence uses Python Shelve (pickle, DBM) functionality and will create an "app_data.db" and related files in the working directory.

Launch Darkly is set up by default to access the account of lddemo@adamooo.com: "LD Demonstration" org, "Default Project" project, "Test" environment.  SDK and API keys for the Project, Environment, flag(s), etc are set in the code (see .../app.py) - and could be substituted if using an alternate account, etc (but should work out of the box as long as the referenced account is active).

## SETUP
1. Clone the project from GitHub ("main" branch): 
    https://github.com/lddemo-adam/ld-python.git
2. In the project directory, create a virtual environment using IDE or e.g. "python -m venv ./.venv" (adjust to your python path as needed).  
3. Activate the venv with e.g. "source .venv/bin/activate". 
4. Install Flask with e.g. "python -m pip install flask" which should result in something like: "Successfully installed blinker-1.9.0 click-8.2.1 flask-3.1.1 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.2 werkzeug-3.1.3".
5. Install the Requests module with e.g. "python -m pip install requests" which should results in something like: 
    ```
    "Successfully installed certifi-2025.4.26 charset_normalizer-3.4.2 idna-3.10 requests-2.32.4 urllib3-2.4.0"
    ```
    Note: Varying packages for dependencies may be installed depending on your local environment.
6. Install the LaunchDarkly Python server-side SDK, with e.g. "python -m pip install launchdarkly-server-sdk" which should result in something like: 
    ```
    "Successfully installed expiringdict-1.2.2 launchdarkly-eventsource-1.2.4 launchdarkly-server-sdk-9.11.1 pyRFC3339-2.0.1 semver-3.0.4"
    ```

## EXECUTING THE APPLICATION
Run the application with:
    % python -m flask run 
    // optionally with IP/port specified: --host=127.0.0.1 --port=5000

## DEMONSTRATED FEATURES

### Run and access the demo app
1. Set  up and run the application as described above, on a system with internet access.  
2. Connect to http://127.0.0.1:5000/ and confirm that the index / intro page loads.
* This simple application queries a public API and displays the returned data after filtering.
* The data represents "spots" for the amateur radio "Parks on the Air" program, each of which lists the callsign, frequency, and park reference (with other data) for a current operation.
3. Connect to LaunchDarkly with a user authorized in lddemo@adamooo.com's account.
* In the sidebar, select Flags under Release, and then click on the Demo Feature flag.
* With the Test environment selected, note whether the flag is On or Off.

### "Release and Remediate"
Access http://127.0.0.1:5000/spots/ to get the current POTA spots.
* You can optionally filter the mode or location (see the app index page for examples).
* With no filter, or with e.g. ".../locs/US", there will usually be spots available, especially in US daytime/evening hours.
Scenario: A new feature is available which filters out spots that have the code "QRT" in the comment field, which indicates the station has ceased operation recently. 
* With the feature flag *Off*, you may see spots in the returned table with "QRT" in the comment field.  You'll see a note like "The QRT spot suppression feature is disabled" at the top of the page.
* With the feature flag *On*, spots with "QRT" (case-insensitive) in the comment will be removed from the table.  You'll see a note like "The QRT spot suppression feature is enabled (11 spots removed)." at the top of the page.
Release: in the LaunchDarkly UI, change the Demo Feature flag between Off and On by clicking on the switch "Flag is (Off/On) ..." under "Targeting Configuration for Test".  Click "Review and Save" at the bottom of the screen, enter a Comment if desired, and click Save Changes.
* Enabling the feature flag effectively "rolls out" the feature behavior, while disabling it constitutes a "roll back".
* Note that when the Flag is changed at LaunchDarkly, a listener in the web app receives the update and causes a reload which immediately updates the app behavior.
* Unfortunately, the feature flag also causes some non-QRT spots (~10%) to be duplicated in the table when the feature is active.  (This is an intentional, if silly, bug for demonstration's sake.)
Remediation: Let's say that you've rolled out the QRT-filtering feature, but users are now reporting duplicated lines in the active spot table.  You want to roll back the feature until it can be fixed.  This can be done from a separate management system or other automation.
As an example, access http://127.0.0.1:5000/admin/flag/update/turnFlagOff in a new tab/browser to disable the flag.  The spots page should quickly update to show "The QRT spot suppression feature is disabled" and duplicated spot rows will stop occurring.

###  "Target"


## CLEANUP / RESET
Remove the app data files app_data.db* if desired to reset persisted data.
Exit the venv with "deactivate" command.    
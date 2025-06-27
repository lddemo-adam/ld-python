# LaunchDarkly Demonstration - POTA Spots web app
Public demonstration app for LaunchDarkly Release, Targeting, and Experimentation controls.
By Adam Smith, lddemo@adamooo.com, June 2025
Hosted at: https://github.com/lddemo-adam/ld-python.git
This probably won't get maintained for long.

## BACKGROUND
This app was implemented as a "homework exercise" and is meant as a simple demonstration of various capabilities of LaunchDarkly including Feature Flag based rollout, rollback, remediation, targeting, and Experimentation.  


## TECHNICAL NOTES / PREREQUISITES
I assume system/local installation of recent Python 3, pip, and virtualenv tooling and that the user is generally familiar with these as well as interactions with GitHub to download the demo app files.
Python 3.13.4 was used at time of development.  Required (publically available) modules include Flask, Requests, and the LaunchDarkly Server SDK (see brief installation notes below).
The app behavior requires internet connectivity to a public website (pota.app).  The LD SDK requires internet connectivity to LaunchDarkly service, and the demo app will exit if not conneted or if incorrect keys are configured.
Data persistence uses Python Shelve (pickle, DBM) functionality and will create an "app_data.db" or related files in the working directory.

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

## EXECUTION
Run the application with:
    % python -m flask run 
    // optionally with IP/port specified: --host=127.0.0.1 --port=5000

## CLEANUP / RESET
Remove the app data files app_data.db* if desired to reset persisted data.
Exit the venv with "deactivate" command.    
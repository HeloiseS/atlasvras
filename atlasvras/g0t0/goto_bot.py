"""
GOTO Bot
========
Slack bot to allow OxQUB slack users to make GOTO forced photometry
data requests through slack.
"""
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import yaml
import pkg_resources
import re
from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import time
from atlasvras.utils.exceptions import LightcurveTimeoutError
from atlasvras.g0t0.parser import  parse_target_command

# LOAD CONFIG
BOT_CONFIG_FILE = pkg_resources.resource_filename('atlasvras', 'data/bot_config_MINE.yaml')

with open(BOT_CONFIG_FILE, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        LOG_PATH = config['log_path']
        BOT_TOKEN = config['slack_token_g0t0']
        APP_TOKEN = config['app_token_g0t0']
        URL_BASE = config['base_url']+'candidate/'
        EYEBALL_THRESHOLD = config['eyeball_threshold']
        URL_SLACK = config['url_slack']
        goto_username= config['goto_username']
        goto_password= config['goto_password']
    except yaml.YAMLError as exc:
        print(exc)

#### SET UP THE HELP MESSAGE
HELP_MESSAGE = """
*GOTO Bot Help :robot_face:*
Use the bot to fetch lightcurves from the GOTO Force Photometry server (currently in beta).

*Example:*
`@G0T0 target SN2024cld RA=237.590033 Dec=18.93919 date_from=2024-02-01 plot`

*Basic usage:*
`@G0T0 target <name> RA=<ra> Dec=<dec> [date_from=YYYY-MM-DD] [date_to=YYYY-MM-DD] [plot (optional)]`

*Example:*
`@G0T0 target SN2025abc RA=123.45 Dec=-45.6 date_from=2025-01-01`

*Notes:*
- RA and Dec must be in *decimal degrees* (e.g. 123.456, not HMS)
- `date_to` defaults to *today*
- Add `plot` to generate a lightcurve plot (optional)

Need someone to blame? Contact Heloise.
"""

# Initialize app
app = App(token=BOT_TOKEN)


######################
### GOTO API
######################

def fetch_lightcurve_data(params, auth, base_url="https://goto-observatory.warwick.ac.uk", poll_interval=2, timeout=15):
    submit_url = f"{base_url}/lightcurve/api-v1/submit/"
    data_base_url = f"{base_url}/lightcurve/api-v1/data/"

    json_conf = {
        "conf": {
            "target_name": params["target_name"],
            "ra": params["ra"],
            "dec": params["dec"],
            "epoch": "J2000.0",
            "pm_ra_mas": None,
            "pm_dec_mas": None,
            "colour_ref": "g-r",
            "colour_mag": 0,
            "date_from": params["date_from"],
            "date_to": params["date_to"],
            "centroid": True,
            "image_type": "set",
            "radius": None,
            "snr_limit": 5,
            "use_difference_images": True,
            "include_thumbnail": False,
            "include_cutout": False,
            "include_error_frames": True,
            "reprocess_error_frames": False,
            "reprocess_all": False,
            "recalibrate_photometry": False,
            "fallback_radius": None
        }
    }

    r = requests.post(submit_url, auth=auth, json=json_conf)
    r.raise_for_status()
    dag_id = r.json()["dag_run_id"]
    data_url = f"{data_base_url}{dag_id}.json"

    # Poll for availability
    start = time.time()
    while time.time() - start < timeout:
        dat = requests.get(data_url, auth=auth)
        if dat.status_code == 200:
            return pd.DataFrame(dat.json()["results"]), data_url
        time.sleep(poll_interval)

    raise LightcurveTimeoutError(data_url)

######################
# PLOT PLOT PLOT
#######################


def make_lightcurve_plot(df):
    plt.figure()
    colours = ['grey' if f == 'L' else 'k' for f in df['filter']]
    plt.scatter(df['mjd'], df['forced_mag'], c=colours)
    plt.gca().invert_yaxis()
    plt.xlabel("MJD")
    plt.ylabel("Forced Mag")
    plt.title("GOTO Lightcurve")

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmpfile.name)
    plt.close()
    return tmpfile.name  # return path to file

##############################
# SLACK SLACK SLACK SLACK SLACK
##############################

@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")
    user = event["user"]
    channel = event["channel"]

    if "help" in text.lower():
        app.client.chat_postEphemeral(
            channel=event["channel"],
            user=event["user"],
            text=HELP_MESSAGE
        )
        return

    try:
        params = parse_target_command(text)
    except ValueError as ve:
        say(f"<@{user}> {ve}")
        return

    if not params:
        say(f"<@{user}> I couldn't understand your request. Try: `target SN2024cld RA=123.45 Dec=-12.3`. If you need help ask me for help! (@G0T0 help)")
        return

    say(f"<@{user}> Fetching data for `{params['target_name']}`...")

    try:
        auth = (config['goto_username'], config['goto_password'])
        df, data_url = fetch_lightcurve_data(params, auth)

        # Save CSV
        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(tmp_csv.name, index=False)

        # Upload CSV
        app.client.files_upload_v2(
            channel=channel,
            initial_comment="...",
            file=tmp_csv.name,
            title=f"{params['target_name']}_lightcurve.csv",
        )
        os.remove(tmp_csv.name)

        # Optional plot?
        if params.get("plot"):
            plot_path = make_lightcurve_plot(df)
            app.client.files_upload_v2(
                channel=channel,
                #initial_comment=f"Lightcurve plot for `{params['target_name']}`",
                file=plot_path,
                title=f"{params['target_name']}_plot.png",
            )
            os.remove(plot_path)

    except LightcurveTimeoutError as te:
        say(f"<@{user}> The data is still processing. Try again soon or check manually: {te.data_url}")
    except Exception as e:
        say(f"<@{user}> Something went wrong: `{e}`")



@app.command("/goto")
def handle_slash_command(ack, respond, command):
    ack()  # acknowledge to Slack immediately

    text = command.get("text", "")
    user = command["user_id"]

    if "help" in text.lower():
        respond(HELP_MESSAGE)
        return

    try:
        params = parse_target_command(text)  # prepend "target" so parser works
    except ValueError as ve:
        respond(f"<@{user}> {ve}")
        return

    if not params:
        respond(f"<@{user}> I couldn't understand your command. Try `/goto target=SN123 RA=... Dec=...`")
        return

    respond(f"<@{user}> Processing your request for `{params['target_name']}`...")

    try:
        auth = (config['goto_username'], config['goto_password'])
        df, data_url = fetch_lightcurve_data(params, auth)

        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(tmp_csv.name, index=False)

        app.client.files_upload_v2(
            channel=command["channel_id"],
            initial_comment=f"Here's the lightcurve for `{params['target_name']}`",
            file=tmp_csv.name,
            title=f"{params['target_name']}_lightcurve.csv"
        )
        os.remove(tmp_csv.name)

        if params.get("plot"):
            plot_path = make_lightcurve_plot(df)
            app.client.files_upload_v2(
                channel=command["channel_id"],
                initial_comment="Plot attached:",
                file=plot_path,
                title=f"{params['target_name']}_plot.png"
            )
            os.remove(plot_path)

    except LightcurveTimeoutError as te:
        respond(f"<@{user}> The data is still processing. Check manually: {te.data_url}")
    except Exception as e:
        respond(f"<@{user}> Something went wrong: `{e}`")


# Entry point
if __name__ == "__main__":
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()

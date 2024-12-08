# Slack API
import os
from slack_sdk import WebClient
from atlasvras.utils.prettify import vra_colors, label_to_color
from atlasapiclient import client as atlasapiclient
from atlasvras.utils.misc import fetch_vra_dataframe
# generic things
import logging
import sys
from datetime import datetime
# Analysis things
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import yaml
import pkg_resources

BOT_CONFIG_FILE = pkg_resources.resource_filename('atlasvras', 'data/bot_config_MINE.yaml')

with open(BOT_CONFIG_FILE, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        LOG_PATH = config['log_path']
        SLACK_TOKEN = config['slack_token_el01z']
        URL_BASE = config['base_url']
        EYEBALL_THRESHOLD = config['eyeball_threshold']
        URL_SLACK = config['url_slack']
    except yaml.YAMLError as exc:
        print(exc)

####################################################################################
######################### STARTING THE SCRIPT ######################################

# Get the last run date from the command line arguments. This will be handled by the
# bash script that will call this python script.
try:
    last_run_date = sys.argv[1]
except IndexError:
    raise IndexError("CL argument not found. Call script with [INCLUDE THE GREP COMMAND I'LL USE IN THE BASH SCRIPT]")
# last_run_date = '2024-09-13'

TODAY = datetime.today().strftime('%Y-%m-%d')
# Configure logging
logging.basicConfig(level=logging.INFO,
                    # Set the logging level to DEBUG (you can change it as needed)
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    # Define the format of log messages
                    filename=f'{LOG_PATH}/weeklyreport.log',
                    # Specify the log file
                    filemode='a')  # Set the file mode to 'w' for writing (change as needed)

# Write in the log that we are starting the script
logging.info("Starting the script - last run date: " + last_run_date)

#### CONSTANTS TO PRETIFY THE PLOTS ####
plt.style.use('vra')



def determine_alert_type(vra_table_row):
    if vra_table_row['rank'] == -1:
        return "auto-garbage"
    if vra_table_row.preal == 0.0 and vra_table_row.pgal != 1.0:
        return 'garbage'
    elif vra_table_row.preal == 0.0 and vra_table_row.pgal == 1.0:
        return 'pm'
    elif vra_table_row.preal == 1.0 and vra_table_row.pgal == 1.0:
        return 'galactic'
    elif vra_table_row.preal == 1.0 and vra_table_row.pgal != 1.0:
        return "good"
    elif vra_table_row.preal == 0.5:
        return "possible"


###########################################################
####### MAIN #######
############################################################
vra_past_week = fetch_vra_dataframe(datethreshold=last_run_date).set_index('transient_object_id')
logging.info("Fetched the VRA datarame")

TEXT_REPORT = f"*VRA Weekly Report*\n"

#### N_RBScore > 0.2
N_2EYEBALL= vra_past_week[(vra_past_week['rank']>4)
                            ].index.unique().shape[0]
N_RBSCORE_GT0p2 = vra_past_week[~pd.isna(vra_past_week.apiusername)].index.unique().shape[0]


#### PIE CHART
labels_ALL = vra_past_week.apply(determine_alert_type, axis=1).rename('type')
df = labels_ALL[~pd.isna(labels_ALL)].value_counts()
df.plot(kind='pie', autopct="%.2f%%", textprops={'color': 'k'},
        colors=[label_to_color[label] for label in df.index.values], legend=True)

plt.title(f'From {last_run_date} to {TODAY}')
plt.savefig(f'{LOG_PATH}/figures/{TODAY}.png', bbox_inches='tight')

##### NEW EVENTS AND POTENTIAL MISSES
in_tns = vra_past_week[vra_past_week['rank'] == 10.0].index
vra_past_week['type'] = labels_ALL
potential_misses = vra_past_week.loc[in_tns][vra_past_week.loc[in_tns].type == 'good'].index.unique()
trace = vra_past_week[pd.isna(vra_past_week.username)].loc[potential_misses]


N_FOUND_FIRST = len(set(vra_past_week[vra_past_week.type == 'good'].index.unique()) - set(potential_misses))
N_FOUND_BY_OTHERS = len(potential_misses)

TEXT_REPORT +=f"*TL;DR*\n"
TEXT_REPORT +=f":eye: *{N_2EYEBALL}* | :first_place_medal: *{N_FOUND_FIRST}* | :second_place_medal: *{N_FOUND_BY_OTHERS}*\n\n"

TEXT_REPORT +=f"*The Deets*\n"
TEXT_REPORT +=f"- Week Starting: {last_run_date}\n"
TEXT_REPORT += (f"- You eyeballed *{N_2EYEBALL}* ({np.round(N_2EYEBALL/N_RBSCORE_GT0p2*100,1)}%) "
                f"alerts out of the *{N_RBSCORE_GT0p2}* with RB > 0.2\n")
TEXT_REPORT += (f"- **TNS**: *{N_FOUND_FIRST}* Reported by us first "
                f"and another *{N_FOUND_BY_OTHERS}* (Cross-matched to TNS) \n\n")

### THINGS THAT GOT LOW VRA SCORE BUT WERE IN TNS
misses_index = set(trace[(trace['rank'] < 4)].index) - set(trace[(trace['rank'] > 4) & (trace['rank'] < 10)].index)
N_POTENTIAL_MISSES = len(misses_index)

RANKS = trace[trace['rank'] < 4].loc[list(misses_index)]['rank']

#pstar_web_url_base = 'https://star.pst.qub.ac.uk/sne/atlas4/candidate/'

TEXT_REPORT += f":warning: {N_POTENTIAL_MISSES} *Potential Misses* (low VRA scores but X-match raised their ranks.\n"
#for index in misses_index:
#   TEXT_REPORT += f"   - <{pstar_web_url_base}{index}| {index}> got a rank of {RANKS.loc[index]}\n"
potential_misses_df = pd.DataFrame(misses_index)
potential_misses_df['timestamp']=TODAY
potential_misses_df.to_csv(f'{LOG_PATH}/potential_misses.csv',
                                header=False, mode='a', index=False)

logging.info("Analysis and Figure complete")

with open(f"{LOG_PATH}/report.csv", "a") as f:
    f.write(f"{TODAY},{N_RBSCORE_GT0p2},{N_2EYEBALL},{N_FOUND_FIRST},{N_FOUND_BY_OTHERS},{N_POTENTIAL_MISSES}\n")

logging.info("numbers saved to report.csv")
###################################################

client = WebClient(token=SLACK_TOKEN)

file_path = f'{LOG_PATH}/figures/{TODAY}.png'

file_response = client.files_upload_v2(
    channels=["C07HZGBKHQX"],
    #channels=["C0842K2QZS8"], # #vra-dev to test
    initial_comment=f"Here are the label distributions for the week starting on {TODAY}",
    file=file_path,
)
file_url = file_response["file"]["permalink"]

client.chat_postMessage(
    channels="C07HZGBKHQX", # #vra-forum for real thing
    #channel="C0842K2QZS8", # #vra-dev to test
    text=TEXT_REPORT,
)

##### NEED TO DO THE DEV REPORTING #####
TEXT_REPORT_DEV = f"*Rank Comparison for the week starting: {last_run_date}*\n"
N_2EYEBALL_ALT = vra_past_week[(vra_past_week['rank_alt1']>4)
                                ].index.unique().shape[0]

TEXT_REPORT_DEV+= (f":eye: Number comparisons:  "
                   f" :baby:{N_2EYEBALL}  |  :older_adult:{N_2EYEBALL_ALT}")
### Making the comparison df
# Vra for all the objects that were dealth with by NEW model
# excludes the rows corresponding to crossmatching, garbaging and human decisions
vra_decisions_df = vra_past_week[(vra_past_week.apiusername == 'vra')]
vra_df_new_ranks = vra_decisions_df[(vra_decisions_df['rank']!=-1)
                                    & (vra_decisions_df.rank_alt1.isna())
                                    & (vra_decisions_df['rank'] != 10)]

# Vra for all the objects that were dealth with by OLD model
vra_df_old_ranks = vra_decisions_df[(vra_decisions_df['rank']!=-1)
                                    & (~vra_decisions_df.rank_alt1.isna())
                                    & (vra_decisions_df['rank'] != 10)]

# Making the comparison dataframe
comparison_df = vra_df_new_ranks[['rank']].join(vra_df_old_ranks.rank_alt1
                                                )

comparison_df.columns = ['rank_NEW', 'rank_OLD']

# isolating human decisions
human_decisions_df = vra_past_week[~(vra_past_week.apiusername == 'vra')]
comparison_df = comparison_df.join(human_decisions_df.type)

label_to_color = {'garbage':vra_colors['red'],
                 'good':vra_colors['blue'],
                 'pm':vra_colors['orange'],
                 'galactic':vra_colors['yellow'],
                 'auto-garbage':'grey',
                 'possible': vra_colors['white'],
                 np.nan: 'white'
                }


f, ax = plt.subplots(1, figsize=(5,5))
ax.scatter(comparison_df.rank_NEW, comparison_df.rank_OLD,
           color = [label_to_color[label] for label in comparison_df.type.values],
           s=5, zorder=1000, marker='*', alpha=0.9)
ax.axline((1, 1), slope=1, color='grey', ls='--')
# Create a rectangle patch
rect1 = patches.Rectangle((0, 4), 4, 6, linewidth=1, edgecolor=vra_colors['red'], facecolor='none')
ax.axvspan(0, 4, ymin=4/10, ymax=10/10, alpha=0.3, color=vra_colors['red'])

rect2 = patches.Rectangle((4, 0), 6, 4, linewidth=1, edgecolor=vra_colors['yellow'], facecolor='none')
ax.axvspan(4, 10, ymin=0, ymax=4/10, alpha=0.3, color=vra_colors['yellow'])


ax.axvspan(4, 10, ymin=4/10, ymax=10, alpha=0.3, color=vra_colors['blue'])
# Add the rectangle to the plot
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.set_ylabel('BMO Rank')
ax.set_xlabel('Crabby Rank')
ax.set_ylim(0,10)
ax.set_xlim(0,10)

ax.text(0.1, 9.5, 'Danger', color=vra_colors['red'], fontsize=15)
ax.text(10.1, 4.3, 'Agree', color=vra_colors['blue'], fontsize=15, rotation=90 )
ax.text(10.1, 0.3, 'New', color=vra_colors['yellow'], fontsize=15, rotation=90)
ax.set_title(f'From {last_run_date} to {TODAY}')
plt.savefig(f'{LOG_PATH}/figures/{TODAY}_RankComparison.png', bbox_inches='tight')

### Isolating just the scores from the models
vra_scores_df = vra_decisions_df[(vra_decisions_df['rank']!=10.0)&
                                 (vra_decisions_df['rank']!=-1.0)
                                ]

N_w_rank = sum(~vra_scores_df['rank'].isna())
N_w_rank_alt1 = sum(~vra_scores_df['rank_alt1'].isna())

N_MISSED_RANKS = N_w_rank - N_w_rank_alt1

TEXT_REPORT_DEV+= (f"\n:warning: Old model would have *{N_MISSED_RANKS}* missing rank values "
                   f"(:baby: {N_w_rank} | :older_adult:{N_w_rank_alt1} )\n")

### Looking at how many garbage avoided and how many goods "saved"
real_ids = set(human_decisions_df[human_decisions_df.preal==1.0].index)
bogus_ids = set(human_decisions_df[human_decisions_df.preal==0.0].index)
_index_set = set(vra_scores_df.index)

vra_scores_real = vra_scores_df.loc[list(real_ids.intersection(_index_set))]
vra_scores_bogus = vra_scores_df.loc[list(bogus_ids.intersection(_index_set))]

N_AVOIDED_GARBAGE =  vra_scores_bogus[vra_scores_bogus['rank_alt1']<4].shape[0]

missed_OLDmodel_typecount = human_decisions_df.loc[vra_scores_real[vra_scores_real['rank_alt1']<4].index].type.value_counts()
N_SAVED_GOOD = missed_OLDmodel_typecount['good']
N_SAVED_GAL = missed_OLDmodel_typecount['galactic']

TEXT_REPORT_DEV+= f"\n:recycle: *{N_AVOIDED_GARBAGE}* garbage avoided\n"
TEXT_REPORT_DEV+= f":boom: *{N_SAVED_GOOD}* goods saved\n"
TEXT_REPORT_DEV+= f":milky_way: *{N_SAVED_GAL}* galactic saved\n"

with open(f"{LOG_PATH}/dev_report.csv", "a") as f:
    f.write(f"{TODAY},{N_2EYEBALL},{N_2EYEBALL_ALT},{N_MISSED_RANKS},{N_AVOIDED_GARBAGE},{N_SAVED_GOOD},{N_SAVED_GAL}\n")


file_path = f'{LOG_PATH}/figures/{TODAY}_RankComparison.png'
file_response = client.files_upload_v2(
    channels=["C0842K2QZS8"],
    initial_comment=f"Rank Comparisons for the past week",
    file=file_path,
)

file_url = file_response["file"]["permalink"]

client.chat_postMessage(
    channel="C0842K2QZS8", # #vra-dev
    text=TEXT_REPORT_DEV,
)

#########################################
logging.info("Finished")
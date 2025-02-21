#!/usr/bin/bash

export STYLEFILE="/usr/local/ps1code/gitrelease/atlasvras/atlasvras/data/vra.mplstyle"

export PYTHONPATH=/usr/local/ps1code/gitrelease/atlasapiclient:/usr/local/ps1code/gitrelease/atlasvras
#export PYTHONPATH=/usr/local/ps1code/gitrelease/stephen/st3ph3n:/usr/local/ps1code/gitrelease/atlasapiclient
export CONFIG_ATLASAPI=/usr/local/ps1code/gitrelease/atlasapiclient/atlasapiclient/config_files/api_config_MINE.yaml

export PYTHON="/usr/local/swtools/python/atls/anaconda3/envs/vra/bin/python"
export CODEBASE="/usr/local/ps1code/gitrelease/atlasvras/atlasvras/el01z"
export LOGBASE="/db5/tc_logs/atlas4/vralogs"

export GREP=`/usr/bin/grep "Finished" $LOGBASE/weeklyreport.log | /usr/bin/tail -n 1 | /usr/bin/cut -d',' -f1 | /usr/bin/sed 's/ /T/'`
$PYTHON $CODEBASE/weeklyreport.py $GREP $STYLEFILE #> /tmp/whathappened_weeklyreport.log 2>&1

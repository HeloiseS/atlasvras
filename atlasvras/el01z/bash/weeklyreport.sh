#!/usr/bin/bash

export PYTHON="/home/stevance/anaconda3/bin/python"
export PYTHONPATH="${PYTHONPATH}:/home/stevance/software/atlasapiclient"
export PYTHONPATH="${PYTHONPATH}:/home/stevance/software/atlasvras"
export CODEBASE="/home/stevance/software/atlasvras/atlasvras/el01z"
export LOGBASE="/home/stevance/software/logs/"
export STYLEFILE="/home/stevance/anaconda3/lib/python3.10/site-packages/matplotlib/mpl-data/stylelib/vra.mplstyle"


export GREP=`/usr/bin/grep "Finished" $LOGBASE/weeklyreport.log | /usr/bin/tail -n 1 | /usr/bin/cut -d',' -f1 | /usr/bin/sed 's/ /T/'`
$PYTHON $CODEBASE/weeklyreport.py $GREP $STYLEFILE #> /tmp/whathappened_weeklyreport.log 2>&1
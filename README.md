<p align="center">
<img src="./docs/source/_static/logo.png?raw=true" width="120px" />
</p>

# ATLAS Virtual Research Assistant (VRAs)
[![DOI](https://zenodo.org/badge/888466484.svg)](https://doi.org/10.5281/zenodo.14363396)

This repository contains data processing and models that are used by 
the ATLAS Virtual Research Assistant (VRA) in the production pipeline. 

The VRA is a bot designed to perform preliminary eyeballing on the ATLAS Transient data stream. 
It uses Histogram Based Gradient Boosted Decision Tree Classifiers to score incoming alerts on two axes: “Real” and  “Galactic”. 
The alerts are then ranked between 0 and 10 such that the most “Real” and “Extra-galactic” receive high scores. 
The alerts most likely to be "Galactic" are flagged with a boolean
Policies are defined to select the most promising alerts for humans to eyeball and to automatically
remove the alerts most likely to be bogus. 
**This strategy has resulted in a reduction in eyeballing workload by 80%** with no loss of follow-up opportunity.  


For some quick information you can check the [VRA website](https://heloises.github.io/atlasvras/about.html).
A paper is coming soon and will be linked here. 

## G0T0 Slack Bot

A Slack-integrated interface to query the GOTO telescope lightcurve archive. Built for transient astrophysics workflows.

---

### 🚀 Features

- Query GOTO forced photometry lightcurve data using Slack messages or slash commands
- Retrieve results as a CSV file, optionally with a lightcurve plot
- Works in public channels, private groups, and direct messages with the bot
- Validates input and handles asynchronous data availability via polling

---

### 💬 Usage
(if in doubt, summon the bot and type help in the message)
#### Directly in the @G0T0 app in slack
`target SN2025abc RA=123.45 Dec=-45.6 date_from=2025-01-01 plot=true`

#### `@G0T0` Mention (in a channel)
`@G0T0 target SN2025abc RA=123.45 Dec=-45.6 date_from=2025-01-01 plot=true`

#### `/goto` From anywhere including DMs
`/goto target=SN2025abc RA=123.45 Dec=-45.6 date_from=2025-01-01 plot=true`

## If you want the gnarly details

**Technical Manual** 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14983098.svg)](https://doi.org/10.5281/zenodo.14983098)

**Code and Data Release for VRA v1**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14906192.svg)](https://doi.org/10.5281/zenodo.14906192)


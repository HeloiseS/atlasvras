<p align="center">
<img src="./docs/source/_static/logo.png?raw=true" width="120px" />
</p>

# ATLAS Virtual Research Assistant (VRAs)
[![DOI](https://zenodo.org/badge/888466484.svg)](https://doi.org/10.5281/zenodo.14363396)

---
[**Eyeballer Cheat Sheet**](https://heloises.github.io/atlasvras/eyeball.html)

---

This repository contains data processing and models that are used by 
the ATLAS Virtual Research Assistant (VRA) in the production pipeline. 
It also contains the various slack bots installed on the OxQUB slack channel.

**This code is not written with the intention to be used as-is by other teams - but it is open source so if you find something useful to you, you can use it**
At this time I will not be taking requests for features from people outside our core team. 

## The VRA 

### Summary 
The VRA is a bot designed to perform preliminary eyeballing on the ATLAS Transient data stream. 
It uses **Histogram Based Gradient Boosted Decision Tree Classifiers** to score incoming alerts on two axes: “Real” and  “Galactic”. 
The alerts are then ranked between 0 and 10 such that the most “Real” and “Extra-galactic” receive high scores. 
The alerts most likely to be "Galactic" are flagged with a boolean.
Policies are defined to select the most promising alerts for humans to eyeball and to automatically
remove the alerts most likely to be bogus. 
**This strategy has resulted in a reduction in eyeballing workload by 80%** with no loss of follow-up opportunity.  

### The Docs
More extensive documentation can be found on the [VRA website](https://heloises.github.io/atlasvras/about.html).
The paper can be found on the arxiv here **[COMING SOON]**.


#### For devs and brave people

Technical Manual

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14983098.svg)](https://doi.org/10.5281/zenodo.14983098)

Code and Data Release for VRA v1

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14906192.svg)](https://doi.org/10.5281/zenodo.14906192)


## G0T0 Slack Bot
The GOTO Slack bot allows OxQUB team members to request GOTO Force Photometry directly form slack.

  1. **Go to the #goto Channel**
  2. Try this example

```
@G0T0 target SN2024cld RA=237.590033 Dec=18.93919 date_from=2024-02-01 plot
```

If it works you will receive a reply from the bot with a .csv of the data and, if you added ``plot`` at the end of your query, a png of the magnitude lightcurve. 

Here is a more formal usage definition highlighting all parameters and whihc ones are optional:

```
@G0T0 target <name> RA=<ra> Dec=<dec> [date_from=YYYY-MM-DD] [date_to=YYYY-MM-DD] [plot (optional)]
```






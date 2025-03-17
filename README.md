
<img src="./docs/source/_static/logo.png?raw=true" width="100px" />

# ATLAS Virtual Research Assistants (VRAs)
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

### If you want the gnarly details

**Technical Manual** 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14983098.svg)](https://doi.org/10.5281/zenodo.14983098)

**Code and Data Release for VRA v1**
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14906192.svg)](https://doi.org/10.5281/zenodo.14906192)


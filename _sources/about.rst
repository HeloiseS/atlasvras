Background
=============
.. _Tonry et al. 2018: https://ui.adsabs.harvard.edu/abs/2018PASP..130f4505T/abstract
.. _Smith et al. 2020: https://ui.adsabs.harvard.edu/abs/2020PASP..132h5002S/abstract
.. _Sherlock: https://lasair.readthedocs.io/en/develop/core_functions/sherlock.html
.. _Weston et al. 2024: https://academic.oup.com/rasti/article/3/1/385/7713043
.. _scikit-learn docs: https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting

Data Journey: From Telescope to Transient Name Server
------------------------------------------------------------

.. seealso::
   Survey Design: `Tonry et al. 2018`_ | Transient Server `Smith et al. 2020`_

The ATLAS data are first reduced (debiased and flat fielded) on site before
being sent to Hawaii for difference imaging. Alerts are produced if a detection
above 5 sigma is recorded, and these form the data stream that is handled by
the servers at Queen's University Belfast.

The alert stream size is of order 10s millions per night. Most of these are artefacts from the
difference imaging process, or known variable stars. The data stream is handled
as follows:

1. **Alerts to Sources**: We aggregate individual alerts into sources (one source will likely have mutiple alerts). If the source is new, its unique 19 digit ATLAS ID is created.
2. **Basic Cuts**: Some simple quality cuts can help reduce the volume of the data stream. The main is that **at least 3 detections per source (per night)** are required to move onto the next stage.
3. `Sherlock`_ catalogue cross matching and **remove variable stars**.
4. **Real/Bogus Score**: We use a Convolutional Neural Network to classify the alerts as real or bogus (see `Weston et. al 2024`_ ). **If the RB score >0.2** they are passed on to eyeball list
5. **Eyeball list**: The alerts are eyeballed and classified as ``garbage``, ``good`` or ``attic`` (for real alerts from transients within the galaxy). Good alerts are automatically pushed to TNS.

The eyeball list in ATLAS still receives between **1000 and 3000 alerts**
every week depending on weather and phase of the moon.
Despite the fact that the CNN removes 98.5% of alerts, most of the eyeball list is still garbage.

.. image:: _static/pie_chart.png
   :width: 400
   :align: center
   :alt: Pie chart showing the distribution of alerts in the eyeball list from data gathered between 27th March and 13th August 2024

The Challenge of Automation
----------------------------------------
The difficulty in automating the eyeballing process further is two fold:
1. We need **very high completeness** (we don't want to miss cool transients)
2. Humans are FAST at the eyeballing task. Meaning they need _little_ data

.. important::
   Given the cadence of ATLAS, people making over 90% of decisions within 24/48 hours means they most often only have **one to two lightcurve points** to look at.


.. image:: _static/when_decision_made.png
    :width: 650
    :align: center
    :alt: Histograms split by types showing the delay in human decisions

Because lightcurve information is not rich, classic transient classifiers made to reproduce
spectroscopic classifications using only the lightcurve information are
**never going to have sufficient information** to be useful in this regime.
We therefore need to bridge the gap between the Real/Bogus classifiers (day 1 regime)
and the Transient classifiers (day 7+ regime).

--------


The Virtual Research Assistant
=================================

The VRA is designed to emulate the decision making of the eyeballers,
and to leverage as much of the data available on the web server as possible.
In addition to using the RB score, the virtual eyeballer ``st3ph3n`` also uses
**context** and **lightcurve features**  and it follows  a similar strategy
to the human team by asking **two questions**:

- *Does this alert look REAL?*
- *Does this alert look GALACTIC ?*

Real and Galactic Scores
-----------------------------------
To calculate the Real and Galactic scores, we train models called
Histogram base Gradient Boosted Decision Trees (see `scikit-learn docs`_ ).
Both models use **the same features** but they **calculate scores independently**,
and they are trained separately.

They each score the alerts **from 0 to 1**, such that we can place our alerts in a plot
we call the score space:

.. image:: _static/score_space.png
    :width: 650
    :align: center
    :alt: Score space showing the balanced training data for the Crabby models

.. seealso::
   For more information about the data and the training of the models see the **Data** and **Training** subsections

Because we care about **extragalactic transients** we are interested in alerts
nearest the **bottom right** (real=1, galactic=0).
We're going to use this to calculate the ranks.

Ranking
-----------------------------------
To rank our alerts we now use the *pythagoras theorem* :sparkles:.
We calculate the distance from the bottom right corner of the score space, scaling the
galactic axis by **0.4** to separate the bad alerts from the good ones more effectively.
It also ensures that our eyeballing policy (see below) encompasses the real=1, galactic=1 corner
whilst leaving out as much or the garbage as possible.

We then normalise all the distances (by the maximum distance that can be reached in the scaled score space),
so that they range between 0 and 1. Then we multiply by 10 to get the values you see
on the web server

.. warning::
   In the previous version of the VRA the scaling factor was 0.5. This means the new models will give you a few more alerts to eyeball with more contamination down in the rank 4-6. But we're also less likely to miss real galactic alerts.


Eyeballing Policy
-----------------------------------

.. image:: _static/ss_byalert_wranks.png
    :width: 650
    :align: center
    :alt: Here we show the score space distributions for each alert type. We also plot the VRA rank contours.

[Plots of the eyeballing policy fractions]


Garbaging Policies
-----------------------------------
There are currently three "garbage collection" policies in place:
* On **entering the eyeball list** with ``rank<1.5``
* On a **second visit**, ``max(rank)<3``.
* On the **third and subsequent visits**, ``mean(rank)<3``.

Because the cadence is often 2 to 3 days, after the 3rd or 4th visit we will get close to +15 days after initial alert, which falls out of the training window.

Now because we eyeball everything with rank >4, these garbaging policies will leave some alerts in "purgratory".
These are now being handled by ``el01z`` which has a sentinel looking out for
alerts that are left in purgatory after they have fallen out of ``st3ph3n``'s training window.

.. caution::
   We will need to add a garbage collection policy to automate purgatory collection.






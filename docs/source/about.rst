Curating the eyeball list
---------------------------------

The eyeball list in ATLAS is defined as everything that gets a Real/Bogus score >0.2 in our CNN.
Every week that is between 1000 and 3000 alerts depending on weather and phase of the moon.

The virtual eyeballer ``st3ph3n`` uses **context** and **lightcurve features** (in addition to
the RB score) to help distinguish further the alerts we care about from those we don't.
We have ``st3ph3n`` follow  a similar strategy to a human eyeballer, we ask **two questions**:

- *Does this look REAL?*
- *Does this look GALACTIC ?*

Real and Galactic Scores
~~~~~~~~~~~~~~~~~~~~~~~~~
To calculate the Real and Galactic scores, we train models called
Histogram base Gradient Boosted Decision Trees [REF models].
Both models use **the same features** but they **calculate scores independently**,
and they are trained separately.

They each score the alerts **from 0 to 1**, such that we can place our alerts in a plot
we call the score space:
[ADD picture]

Because we care about **extragalactic transients** we are interested in alerts
nearest the **bottom right** (real=1, galactic=0).
We're going to use this to calculate the ranks.

Ranking
~~~~~~~~~~~~~~~~~~~~~~~~~
To rank our alerts we now use the *pythagoras theorem* :sparkles:.
We calculate the distance from the bottom right corner of the score space, using a **scalar**
(a.k.a fudge factor) to separate the bad alerts from the good ones more effectively.
We scale the galactic axis by **0.4** to capture the real=1, galactic=1 corner and leave out
as much or the garbage as possible.

We then normalise all the distances (by the maximum distance that can be reached in the scaled score space),
so that they range between 0 and 1. Then we multiply by 10 to get the values you see
on the web server

[ADD picture to show score space with the rank arcs]

.. warning::
   In the previous version of the VRA the fudge factor was 0.5. This means the new models will give you a few more alerts to eyeball with more contamination down in the rank 4-6. But we're also less likely to miss real galactic alerts.



Eyeballing Policy
~~~~~~~~~~~~~~~~~~~~~~~~~


Garbaging Policies
~~~~~~~~~~~~~~~~~~~~~~~~~


Purgatory
~~~~~~~~~~~~~~~~~~~






How does it work?
====================

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

Day 1 Vs Day N Models
~~~~~~~~~~~~~~~~~~~~~~~


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

.. warning::
   In the previous version of the VRA the fudge factor was 0.5. This means the new models will give you a few more alerts to eyeball with more contamination down in the rank 4-6. But we're also less likely to miss real galactic alerts.


Eyeballing Policy
~~~~~~~~~~~~~~~~~~~~~~~~~

[ADD picture to show score space with the rank arcs]
[Plots of the eyeballing policy fractions]


Garbaging Policies
~~~~~~~~~~~~~~~~~~~~~~~~~
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






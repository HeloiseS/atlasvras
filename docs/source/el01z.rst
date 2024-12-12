Monitoring with El01z
===================

``el01z`` is the bot that monitors the behaviour of the VRA.
It's actually currently made of **3 different bots** (as in: three separate scripts)
that have slightly different purposes

1. **Weekly reports**
2. **Monitoring purgatory**
3. **Comparing old and new models**

The first bot is a permanent fixture although the body of the reports
may evolve (and have already).
The other two are 100% dev helpers that will be turned off eventually.

Weekly Reports
--------------------
Every Friday before the data wrangling meeting, ``el01z`` will generate a report
to the ``#vra-forum`` channel which is meant for the whole QUB team.
It will tell you:

- The number of eyeballed objects
- The number of objects with RB > 0.2
- The number of objects that were found first by us
- The number of objects that were found by others
- The number of potential misses
- Upload a pie chart of the distribution of alert types labeled this week

.. note::
   Potential misses are defined as alerts that the VRA scored too low to be eyeballed
   but were already in TNS. These are **not necessarily** misses since some
   TNS crossmatches are bad, old, or simply because in ATLAS the object
   is simply so faint we can't expect the VRA to catch it (that's why we update
   the VRA ranks with cross-matching).

``el01z`` will also send a message to ``#vra-dev`` and save some data to
a csv. For details, check the top of the docstring in
``atlasvras/el01z/weeklyreport.py``


Monitoring Purgatory
-------------------------

Purgatory
   Objects that are stuck in the eyeball list because their rank is too high to be
   garbaged but too low to be eyeballed are in *purgatory*.

.. important::
   Remember that the ``dayN`` models are only trained with data up to
   15 days after the initial alert. So there is little point giving the VRA data
   for objects that fall outside of its training window (in fact it'd be reckless).

If alerts are still in purgatory after that 15 day window they must be looked at.
Once a week, just before the weekly report, ``el01z`` will generate a list of
objects in purgatory that are past that 15 day "best-by" date
and send it to the ``#vra-dev`` channel so I can eyeball them.

.. note::
   Eventually I *will* add a new garbage collecting policy to get rid of the
   purgatory concept. The reason it exists is that I was panicked at the idea
   of garbaging an alert that was actually real and I made garbaging policies
   that were conservative.


Comparing Old and New Models
------------------------------------

We added the new ``Crabby`` models in production on ``2024-12-06``.
We want to compare to previous models to:

1. See how much more awesome they are
2. Avoid binning something interesting if I messed up.

The compare-bot runs once a day currently and sends to the
``#vra-dev`` channel two lists:

1. The *would-not-have-been-garbaged* alerts. That is those which
   would not have met the auto-garbaging policies in the old model.
   I eyeball each of these to see if there is any reason to doubt.

2. The *danger-zone* alerts: Those that would have been eyeballed
   under the old scheme but are not being eyeballed now. I eyeball them
   to see if we might have missed something.

.. note::
   *"What about the alerts that would NOT have been eyeballed in the old model?"*
   Well those are being eyeballed by the other eyeballers. After a few weeks I
   will take a look and see if we are sending too many extra alerts for eyeballing and
   can cut back further.

The compare-bot also saves a few things to a  file to allow me to do some
comparison plots in a few weeks:

- ``rank_NEW``: the rank given by the new model
- ``rank_OLD``: the rank given by the old model
- ``garbage_flag``: whether the object was garbaged (rank = -1)
- ``timestamp_bot``: the timestamp of the bot run
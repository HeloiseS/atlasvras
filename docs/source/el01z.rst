Monitoring with El01z
===================

``el01z`` is the bot that monitors the behaviour of the VRA.
It's actually currently made of **3 different bots** (as in: three separate scripts)
that have slightly different purposes

1. **Weekly reports**
2. **Monitoring purgatory**
3. **TNS crossmatch to garbage**


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
and send it to the ``#vra-forum`` channel so this week's eyeballer cna eyeball them.


TNS Cross-match to Garbage
------------------------------------
New with ``Duck`` we have a cron-job checking the ``garbage`` with ``rb_pix>0.2``
and [CURRENT YEAR] cross-matches. If runs every friday and checks the last 7 days.
The links to the cross-matches are sent to the ``#vra-dev`` channel.
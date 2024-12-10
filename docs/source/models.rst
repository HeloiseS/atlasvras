The Data
-------------

.. note::
   The naming convention is as follows: new names are chosen for new
   data sets(not new features), with their names starting with incremented
   letters of the alphabet. The Crabby models are the third iteration of VRA
   models (the first two being unpublished prototypes)

The current family of models is called ``Crabby`` and encompasses
data gathered between ``2024-03-27`` and ``2024-08-13``.
These dates were determined by technical reasons; the former
corresponds to our implementation of the systems that record human
decisions as they are being made whilst the latter corresponds to
when we changed the eyeballing strategy to include the VRA ranks.
We chose to only train on alerts whose data could be recorded
as the human decisions were being made so that we have a truthful
record of what they looked like at the time.

Because of updates in e.g. the ``Sherlock`` cross-matching in some
older data in the database, recreating the conditions under which each alert
was eyeballed is non trivial and since we get a constant influx of new data,
we opted for the thrifty option of using data we could control fully.
The August cut off is chosen such that these data are not affected
by any human-machine interaction considerations. **Future data cleaning
and gathering will have to take that into account.**


Some Numbers
~~~~~~~~~~~~~~~~~~~~~~
As you can see in the `pie chart <about.html>`_ in the general description,
the data eyeballed over the period covered by ``crabby`` includes over
40,000 alerts, 88% of which were either Garbage or Proper Motion stars.


Some Caveats
~~~~~~~~~~~~~~~~~~~~
1. **Only one eyeballer** handled each alert (apart from a few exceptions
posted on slack). Ideally for a well curated data set we would want
two to three opinions especially for borderline cases. Here are a few
ways this will affect the current data:
    a. Not all eyeballers use the Proper Motion star list. They will just
    put proper motion alerts in the garbage. This will lead to some confusion
    between the ``garbage`` and ``pm`` alerts.

    b. Most eyeballers will put galactic events in the ``good`` list if another team
    has mistakenly added those to the TNS. This will lead to some confusion
    between the ``galactic`` and ``good`` alerts.

2. The  ``galactic`` tag is actually an ``attic`` list tag. But the attic list also contains:
    a. Duplicate supernovae
    b. Suspected AGN activity

This will lead to further confusion between the ``galactic`` and ``good`` alerts.

.. seealso::
   In the future we **will** re-eyeball the training data, which will solve all these issues.
   It will  be necessary anyway in future iterations because the auto-garbaged
   alerts will contain some galactic events.

Training
---------------
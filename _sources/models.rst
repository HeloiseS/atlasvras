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

The data downloaded is what is returned by the `ATLAS API`_, for the schema
you can check the `json schema`_.

.. _ATLAS API: https://heloises.github.io/atlasapiclient/users.html
.. _json schema: https://psweb.mp.qub.ac.uk/misc/api/atlas/

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

.. attention::
   In the future we **will** re-eyeball the training data, which will solve all these issues.
   It will  be necessary anyway in future iterations because the auto-garbaged
   alerts will contain some galactic events.

Training and Validation sets
~~~~~~~~~~~~~~~~~~~~~~~~
As you can see in the `pie chart <about.html>`_ in the general description,
the data eyeballed over the period covered by ``crabby`` includes over
40,000 alerts, 88% of which were either Garbage or Proper Motion stars.
Roughly 5.5% were classified as ``good`` and 6.5% as ``galactic`` (i.e. put
in the attic).

With these data we create a **balanced** training set and an **unbalanced**
validation set that we will use to check that our models generalise decently and
to tune some hyperparameters.
We do this by randomly sampling the alerts *before* balancing, selecting
15% to be our validation set. Then we balance what's left to create the training set.

.. note::
   We do not call it a **test set** because it isn't : we use it to check our models
   hyperparameters and decided if we want to keep or add features. A real test set
   is an unseen data set we **only use to calculate performance metrics**.
   Realistically, we test in prod.

We keep the validation set unbalanced so that it is representative of
what the model will see in production so that the metrics we calculate to
check performance and generalisation are representative of what we might
see in real life.

The number of alerts in out training and validation sets are shown in the
table below. As you can see the training set is *slightly* unbalanced
with 300 more garbage, pm and galactic alerts than good alerts.
That's because I wanted to keep as large a training set as possible
so I balanced based on the number of galactic alerts. The slight imbalance
did not affect the model's performance in early tests (but we did
try training on the unbalanced training set and it was a disaster).

.. list-table:: Numbers
   :widths: 25 30 30
   :header-rows: 1

   * - Label
     - Training
     - Validation
   * - Garbage
     - 2200
     - 4619
   * - PM
     - 2200
     - 797
   * - Galactic
     - 2210
     - 357
   * - Good
     - 1908
     - 348


The Features
------------------



Training
---------------
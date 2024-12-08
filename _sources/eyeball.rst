Eyeballer Cheat Sheet
===================

.. import::
   You should already be familiar with eyeballing either because you read Michael's`Eyeballing Handbook<https://www.overleaf.com/project/653678f3e33892fbb51fe7b8>`_ or because you were trained by one of the experienced eyeballers.

Policies overview
-------------------
* **First eyeballer**:
    - **Fast Track list**: eyeball all ranks
    - **Standard list**: eyeball ranks >4
    - If you're not sure: **snooze** by putting in **Possible list**.

* **Second eyeballer**:
   - Check the **good** list for anything interesting to put in **follow-up**

st3ph3n-bot
-----------------
As an eyeballer the main bot you will encounter is your virtual eyeballer counterpart: ``st3ph3n``.
It's role is to **rank the alerts from 0 to 10**, with higher ranks being more likely to be extra-galactic transients.
It automatically garbages alerts with low scores (for more detail see [REF]) so you can focus on the most promising alerts.

.. important::
   **Make sure you are in the #vra channel and receiving alerts**

The slackbot triggers at the end ATLAS ingest is complete and send a message to the ``#vra`` channel on the
QUB slack. In each `st3ph3n` alert you will see two lines:

* 1) How many Fast Track (<100 Mpc) objects have rank >4 and how many other (low rank) alerts there are.You should **eyeball ALL ranks in the Fast Track list**.

* 2) How many alerts in the standard eyeball list with ranks >4.

.. warning::
   The number of alerts to be eyeballed is **usually over estimated**. It's a bug we have to fix.

TIps
---------

* 1) **Start with the Fast Track list**. Also note that you need to eyeball **all** ranks (even the lower ones) in the Fast Track list.

* 2) Go back to slack and **click on the eyeball link** provided by ``st3ph3n``. This will take you to the curated eyeball list (ordered and cropped down to rank 4).

* 3) Scroll down to the first alerts that or **not** rank 10 and eyeball these. They are the most promising which haven't yet been pinched by another team.

* 4) Finally clean up the rank 10 alerts.


.. warning::
   A rank of **10** means that the alert has been **cross-matched to TNS**. It does not necessarily mean it is real.


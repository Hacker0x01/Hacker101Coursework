Note
====

The code in this repo is from the old Hacker101 coursework, deprecated in favor of the [Hacker101 CTF](https://ctf.hacker101.com/).  It is split into two parts: one that runs and depends on Google App Engine and one that can be run anywhere you have Python and a MySQL database.

Google App Engine
=================

The GAE levels live under the `gae` directory and should be deployable like any Python application on Google App Engine.

Plain Python
============

Simply run `pip install -r requirements.txt` then change db.py to point to your MySQL instance.  At that point, you should be able to run `python main.py` and have a running instance.

There are several secret levels (that is, were never used in Hacker101); figuring out access is left as an exercise to the hacker.

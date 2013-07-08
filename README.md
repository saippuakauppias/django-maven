django-maven
============

Capture exceptions in django management commands into Sentry by Raven.

Problem And Solution
--------------------

Many management commands running in cron and by default errors and exceptions not wrote in logs.
Or some people redirect all stdout in file (`command >> file.txt`) with log rotation or not.

This package make possible **capture exceptions** (not all stdout/stderr) in your Sentry project.

Installation
------------

1. Install package:

    $ pip install django-maven

2. Add `django_maven` in `INSTALLED_APPS`.

3. Use it! ;)

Example Of Usage
----------------

It's simple!

Add `maven` command by first argument for manage.py in your management command string.

For example, this is command without `django-maven`:

    $ python manage.py dumpdata --exclude=app -n -a

And command with `django-maven`:

    $ python manage.py maven dumpdata --exclude=app -n -a

If command (`dumpdata`) raising exception you see their in your Sentry.

The name
--------

*django-maven* is django management raven.

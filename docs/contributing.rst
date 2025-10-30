************
Contributing
************

Feel free to create a new Pull request if you want to propose a new feature
or fix a bug.  If you need development support or want to discuss
with other developers, join us in the channel #sorl-thumbnail at freenode.net

   irc://irc.freenode.net/#sorl-thumbnail

Running testsuite
=================

For occasional developers we recommend using `GitHub Actions`_ to run testsuite,
for those who want to run tests locally, read on.

Since sorl-thumbnail supports a variety of image backends, python and
Django versions, we provide an easy way to test locally across all of them.
We use `Docker`_ for consistent test environments and `tox`_ for managing
python virtual environments.

Prerequisites
-------------

* `Install Docker`_ and Docker Compose
* ``cd`` in your source directory

Running tests
-------------

Build the Docker image (first time only)::

    docker compose build

Run all tests (all tox environments)::

    docker compose run --rm test

Run tests for a specific configuration using the ``-e`` option with tox::

    docker compose run --rm test sh -c "redis-server --daemonize yes && tox -e py312-django51-pil"

The format is: ``py<version>-django<version>-<backend>``

For example:
- ``py312`` = Python 3.12
- ``django51`` = Django 5.1
- ``pil`` = Pillow image library backend

For a full list of tox environments, see ``tox.ini``

Running specific tests
----------------------

To run specific tests, pass Django test labels after ``--``. Django uses dotted module names,
not file paths::

    # Run a specific test module
    docker compose run --rm test sh -c "redis-server --daemonize yes && tox -e py312-django51-pil -- tests.thumbnail_tests.test_engines"

Running CI target tests
-----------------------

To replicate GitHub Actions CI tests, use the ``ci`` service with the TARGET
environment variable. Available targets: ``pil``, ``imagemagick``, ``graphicsmagick``,
``redis``, ``wand``, ``dbm``, and ``qa`` (for quality assurance checks).

Run a specific CI target::

    TARGET=pil docker compose run --rm ci
    TARGET=imagemagick docker compose run --rm ci
    TARGET=graphicsmagick docker compose run --rm ci
    TARGET=redis docker compose run --rm ci
    TARGET=wand docker compose run --rm ci
    TARGET=dbm docker compose run --rm ci
    TARGET=qa docker compose run --rm ci

Run all CI targets in sequence::

    for target in pil imagemagick graphicsmagick redis wand dbm qa; do
      echo "Testing $target..."
      TARGET=$target docker compose run --rm ci
    done

.. _GitHub Actions: https://github.com/jazzband/sorl-thumbnail/actions
.. _Docker: https://www.docker.com/
.. _tox: https://tox.wiki/
.. _Install Docker: https://docs.docker.com/get-docker/

Sending pull requests
=====================

1. Fork the repo::

    git@github.com:jazzband/sorl-thumbnail.git

2. Create a branch for your specific changes::

    $ git checkout master
    $ git pull
    $ git checkout -b feature/foobar

   To simplify things, please, make one branch per issue (pull request).
   It's also important to make sure your branch is up-to-date with upstream master,
   so that maintainers can merge changes easily.

3. Commit changes. Please update docs, if relevant.

4. Don't forget to run tests to check than nothing breaks.

5. Ideally, write your own tests for new feature/bug fix.

6. Submit a `pull request`_.

.. _pull request: https://help.github.com/articles/using-pull-requests

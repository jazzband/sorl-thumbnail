************
Contributing
************

Feel free to create a new Pull request if you want to propose a new feature
or fix a bug.  If you need development support or want to discuss
with other developers, join us in the channel #sorl-thumnbnail at freenode.net

   irc://irc.freenode.net/#sorl-thumbnail

Running testsuit
================

For occasional developers we recommend using `Travis CI`_ to run testsuit,
for those who want to run tests locally, read on.

Since sorl-thumbnail supports a variety of image backends, python and
Django versions, we provide an easy way to test locally across all of them.
We use `Vagrant`_ for simple interaction with virtual machines and
`tox`_ for managing python virtual environments.

Some dependencies like pgmagick takes a lot of time to compiling. To speed up your
vagrant box you can edit `Vagrant file`_ with mem and cpu or simply install `vagrant-faster`_.
The resulting .tox folder containing all virtualenvs requires ~

* `Install Vagrant`_
* ``cd`` in your source directory
* Run ``vagrant up`` to prepare VM. It will download Ubuntu image and install all necessary dependencies.
* Run ``vagrant ssh`` to log in the VM
* Launch all tests via ``tox`` (will take some time to build envs first time)

To run only tests against only one configuration use ``-e`` option::

    tox -e py34-django16-pil

Py34 stands for python version, 1.6 is Django version and the latter is image library.
For full list of tox environments, see ``tox.ini``

You can get away without using Vagrant if you install all packages locally yourself,
however, this is not recommended.

.. _Travis CI: https://travis-ci.org/mariocesar/sorl-thumbnail
.. _Vagrant: http://www.vagrantup.com/
.. _tox: https://testrun.org/tox/latest/
.. _Install Vagrant: http://docs.vagrantup.com/v2/installation/index.html
.. _Vagrant file: https://docs.vagrantup.com/v2/virtualbox/configuration.html
.. _vagrant-faster: https://github.com/rdsubhas/vagrant-faster

Sending pull requests
=====================

1. Fork the repo::

    git@github.com:mariocesar/sorl-thumbnail.git

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

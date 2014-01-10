# coding: utf-8
import os
from contextlib import contextmanager
from subprocess import check_output


@contextmanager
def same_open_fd_count(testcase):
    num_opened_fd_before = get_open_fds_count()
    yield
    num_opened_fd_after = get_open_fds_count()
    testcase.assertEqual(
        num_opened_fd_before, num_opened_fd_after,
        'Open descriptors count changed, was %s, now %s' % (num_opened_fd_before, num_opened_fd_after)
    )


def get_open_fds_count():
    """Return the number of open file descriptors for current process

        .. warning: will only work on UNIX-like os-es.
    """
    pid = os.getpid()
    procs = check_output(["lsof", '-w', '-Ff', "-p", str(pid)])
    nprocs = len([s for s in procs.decode('utf-8').split('\n') if s and s[0] == 'f' and s[1:].isdigit()])
    return nprocs

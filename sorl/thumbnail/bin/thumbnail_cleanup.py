#!/usr/bin/env python
"""
Tries to delete thumbnails not in use.
"""
# This module is only being kept around for backwards compatibility, so in that
# vein, it also imports the two original methods in case someone's code tries
# to import them.
from sorl.thumbnail.management.commands.thumbnail_cleanup import get_thumbnail_path, clean_up


if __name__ == "__main__":
    from django.core.management import call_command
    call_command('thumbnail_cleanup')

import re
import os

from django.conf import settings

re_thumbnail_file = re.compile(r'(?P<source_filename>.+)_(?P<x>\d+)x(?P<y>\d+)(?:_(?P<options>\w+))?_q(?P<quality>\d+).jpg$')

def all_thumbnails(path, recursive=True):
    """
    Return a dictionary referencing all files which match the thumbnail format.
    
    Each key is a source image filename, relative to path.
    Each value is a list of dictionaries as explained in `thumbnails_for_file`.
    """
    thumbnail_files = {}
    if not path.endswith('/'):
        path = '%s/' % path
    len_path = len(path)
    if recursive:
        all = os.walk(path)
    else:
        all = [(path, [], [f for f in os.listdir(path) if os.path.isfile(f)])]
    for dir, subdirs, files in all:
        rel_dir = dir[len_path:]
        for file in files:
            thumb = re_thumbnail_file.match(file)
            if not thumb:
                continue
            d = thumb.groupdict()
            d['options'] = d['options'] and d['options'].split('_') or []
            filename = os.path.join(rel_dir, d.pop('source_filename'))
            thumbnail_file = thumbnail_files.setdefault(filename, [])
            d['filename'] = os.path.join(dir, file)
            thumbnail_file.append(d)
    return thumbnail_files

def thumbnails_for_file(relative_source_path, root=None, thumbs_dir='thumbs'):
    """
    Return a list of dictionaries, one for each thumbnail belonging to the
    source image.

    The following list explains each key of the dictionary:

      `filename`  -- absolute thumbnail path 
      `x` and `y` -- the size of the thumbnail
      `options`   -- list of options for this thumbnail
      `quality`   -- quality setting for this thumbnail
    """
    if root is None:
        root = settings.MEDIA_ROOT
    basename = thumbnail_basename(relative_source_path)
    source_dir = os.path.dirname(relative_source_path)
    thumbs_path = os.path.join(root, thumbs_dir, source_dir)
    files = all_thumbnails(thumbs_path, recursive=False)
    return files.get(basename, [])

def delete_thumbnails(relative_source_path, root=None, thumbs_dir='thumbs'):
    """
    Delete all thumbnails for a source image.
    """
    thumbs = thumbnails_for_file(relative_source_path, root, thumbs_dir)
    return _delete_using_thumbs_list(thumbs)

def _delete_using_thumbs_list(thumbs):
    for thumb_dict in thumbs:
        os.remove(thumb_dict['filename'])
    return len(thumbs)

def delete_all_thumbnails(path, recursive=True):
    """
    Delete all files within a path which match the thumbnails pattern.
    
    By default, matching files from all sub-directories are also removed. To
    only remove from the path directory, set recursive=False.
    """
    total = 0
    for thumbs in all_thumbnails(path, recursive=recursive).values():
        total += _delete_using_thumbs_list(thumbs)
    return total

def thumbnail_basename(path):
    base, ext = os.path.splitext(path)
    if ext.lower() == '.jpg':
        return base
    return path

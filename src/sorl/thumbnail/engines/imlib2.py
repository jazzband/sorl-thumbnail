"""
This thing is broken, tests fail, strange errors, Most likely I will never
fix this.
"""
#
#import os
#import tempfile
#from cStringIO import StringIO
#from kaa import imlib2
#from sorl.thumbnail.engines.base import EngineBase
#
#
#class Engine(EngineBase):
#    def get_image(self, source):
#        return imlib2.open_from_memory(source.read())
#
#    def get_image_size(self, image):
#        return image.size
#
#    def _colorspace(self, image, colorspace):
#        return image
#
#    def _scale(self, image, width, height):
#        return image.scale((width, height))
#
#    def _crop(self, image, width, height, x_offset, y_offset):
#        return image.crop((x_offset, y_offset), (width, height))
#
#    def _get_raw_data(self, image, format_, quality):
#        tmp = tempfile.mkstemp()[1]
#        image.save(tmp, format=format_.lower())
#        with open(tmp) as fp:
#            data = fp.read()
#        os.remove(tmp)
#        return data
#

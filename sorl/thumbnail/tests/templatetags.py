import unittest
import os
import time
from PIL import Image
from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError
from sorl.thumbnail.tests.classes import BaseTest, RELATIVE_PIC_NAME


class ThumbnailTagTest(BaseTest):
    def render_template(self, source):
        context = Context({
            'source': RELATIVE_PIC_NAME,
            'invalid_source': 'not%s' % RELATIVE_PIC_NAME})
        source = '{% load thumbnail %}' + source
        return Template(source).render(context)

    def testTagInvalid(self):
        basename = RELATIVE_PIC_NAME.replace('.', '_')

        # No args, or wrong number of args
        src = '{% thumbnail %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        src = '{% thumbnail source %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        src = '{% thumbnail source 80x80 Xas variable %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        src = '{% thumbnail source 80x80 as variable X %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid size
        src = '{% thumbnail source 240xABC %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid option
        src = '{% thumbnail source 240xABC invalid %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid quality
        src = '{% thumbnail source 240xABC,quality=a %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid source with THUMBNAIL_DEBUG = False
        src = '{% thumbnail invalid_source 80x80 %}'
        self.assertEqual(self.render_template(src), '')
        # ...and with THUMBNAIL_DEBUG = True
        self.change_settings.change({'DEBUG': True})
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

    def testTag(self):
        expected_base = RELATIVE_PIC_NAME.replace('.', '_')

        # Basic
        output = self.render_template('src="'
            '{% thumbnail source 240x240 %}"')
        expected = '%s_240x240_q85.jpg' % expected_base
        expected_fn = os.path.join(settings.MEDIA_ROOT, expected)
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.verify_thumbnail((240, 180), expected_filename=expected_fn)
        self.assertEqual(output, 'src="%s"' % expected_url)

        # Variable does not exist
        output = self.render_template('{% thumbnail no_variable 80x80 %}')
        self.assertEqual(output, '')

        # On context
        output = self.render_template('height:'
            '{% thumbnail source 240x240 as thumb %}{{ thumb.height }}')
        self.assertEqual(output, 'height:180')

        # On context, variable does not exist
        output = self.render_template(
            '{% thumbnail no_variable 80x80 as thumb %}{{ thumb }}')
        self.assertEqual(output, '')

        # With options and quality
        output = self.render_template('src="'
            '{% thumbnail source 240x240 sharpen,crop,quality=95 %}"')
        # Note that the order of opts comes from VALID_OPTIONS to ensure a
        # consistent filename.
        expected = '%s_240x240_crop_sharpen_q95.jpg' % expected_base
        expected_fn = os.path.join(settings.MEDIA_ROOT, expected)
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.verify_thumbnail((240, 240), expected_filename=expected_fn)
        self.assertEqual(output, 'src="%s"' % expected_url)

        # With option and quality on context (also using its unicode method to
        # display the url)
        output = self.render_template(
            '{% thumbnail source 240x240 sharpen,crop,quality=95 as thumb %}'
            'width:{{ thumb.width }}, url:{{ thumb }}')
        self.assertEqual(output, 'width:240, url:%s' % expected_url)

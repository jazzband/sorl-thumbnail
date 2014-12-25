# -*- coding: utf-8 -*-
import os
import re
from subprocess import Popen, PIPE
from PIL import Image

from django.template.loader import render_to_string
from django.test import Client, TestCase
import pytest

from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine
from .models import Item
from .utils import BaseTestCase, override_custom_settings, DATA_DIR


pytestmark = pytest.mark.django_db


class TemplateTestCaseA(BaseTestCase):
    def test_model(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail1.html', {'item': item, }).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="200" height="100">')
        val = render_to_string('thumbnail2.html', {'item': item, }).strip()
        self.assertEqual(val, '<img style="margin:0px 50px 0px 50px" width="100" height="100">')

    def test_nested(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail6.html', {'item': item, }).strip()
        self.assertEqual(val, (
            '<a href="/media/test/cache/fc/f6/fcf65c09cc4bb8671147de41997422bf.jpg">'
            '<img src="/media/test/cache/67/6b/676b2331a071478b0cb280d0edba7818.jpg" '
            'width="400" height="400"></a>'
        ))

    def test_serialization_options(self):
        item = Item.objects.get(image='500x500.jpg')

        for j in range(0, 20):
            # we could be lucky...
            val0 = render_to_string('thumbnail7.html', {
                'item': item,
            }).strip()
            val1 = render_to_string('thumbnail7a.html', {
                'item': item,
            }).strip()
            self.assertEqual(val0, val1)

    def test_options(self):
        item = Item.objects.get(image='500x500.jpg')
        options = {
            'crop': "center",
            'upscale': True,
            'quality': 77,
        }
        val0 = render_to_string('thumbnail8.html', {'item': item, 'options': options, }).strip()
        val1 = render_to_string('thumbnail8a.html', {'item': item, }).strip()
        self.assertEqual(val0, val1)

    def test_progressive(self):
        im = Item.objects.get(image='500x500.jpg').image
        th = self.BACKEND.get_thumbnail(im, '100x100', progressive=True)
        path = os.path.join(settings.MEDIA_ROOT, th.name)
        p = Popen(['identify', '-verbose', path], stdout=PIPE)
        p.wait()
        m = re.search('Interlace: JPEG', str(p.stdout.read()))
        self.assertEqual(bool(m), True)

    def test_nonprogressive(self):
        im = Item.objects.get(image='500x500.jpg').image
        th = self.BACKEND.get_thumbnail(im, '100x100', progressive=False)
        path = os.path.join(settings.MEDIA_ROOT, th.name)
        p = Popen(['identify', '-verbose', path], stdout=PIPE)
        p.wait()
        m = re.search('Interlace: None', str(p.stdout.read()))
        self.assertEqual(bool(m), True)

    def test_orientation(self):
        ref = Image.open(os.path.join(DATA_DIR, '1_topleft.jpg'))
        top = ref.getpixel((14, 7))
        left = ref.getpixel((7, 14))
        engine = PILEngine()

        def epsilon(x, y):
            if isinstance(x, (tuple, list)):
                x = sum(x) / len(x)
            if isinstance(y, (tuple, list)):
                y = sum(y) / len(y)
            return abs(x - y)

        data_images = (
            '1_topleft.jpg',
            '2_topright.jpg',
            '3_bottomright.jpg',
            '4_bottomleft.jpg',
            '5_lefttop.jpg',
            '6_righttop.jpg',
            '7_rightbottom.jpg',
            '8_leftbottom.jpg'
        )

        for name in data_images:
            th = self.BACKEND.get_thumbnail('data/%s' % name, '30x30')
            im = engine.get_image(th)

            self.assertLess(epsilon(top, im.getpixel((14, 7))), 10)
            self.assertLess(epsilon(left, im.getpixel((7, 14))), 10)
            exif = im._getexif()

            if exif:
                self.assertEqual(exif.get(0x0112), 1)


class TemplateTestCaseB(BaseTestCase):
    def test_url(self):
        val = render_to_string('thumbnail3.html', {}).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="20" height="20">')

    def test_portrait(self):
        val = render_to_string('thumbnail4.html', {
            'source': 'http://dummyimage.com/120x100/',
            'dims': 'x66',
        }).strip()
        self.assertEqual(val,
                         '<img src="/media/test/cache/7b/cd/7bcd20922c6750649f431df7c3cdbc5e.jpg" '
                         'width="79" height="66" class="landscape">')

    def test_empty(self):
        val = render_to_string('thumbnail5.html', {}).strip()
        self.assertEqual(val, '<p>empty</p>')


class TemplateTestCaseClient(TestCase):
    def test_empty_error(self):
        with override_custom_settings(settings, THUMBNAIL_DEBUG=False):
            from django.core.mail import outbox

            client = Client()
            response = client.get('/thumbnail9.html')
            self.assertEqual(response.content.strip(), b'<p>empty</p>')
            self.assertEqual(outbox[0].subject, '[sorl-thumbnail] ERROR: /thumbnail9.html')

            end = outbox[0].body.split('\n\n')[-2].split(':')[1].strip()

            self.assertEqual(end, '[Errno 2] No such file or directory')


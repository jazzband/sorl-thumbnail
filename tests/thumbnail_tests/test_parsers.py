# -*- coding: utf-8 -*-
import unittest

from sorl.thumbnail.helpers import ThumbnailError
from sorl.thumbnail.parsers import parse_crop, parse_geometry


class CropParserTestCase(unittest.TestCase):
    def test_alias_crop(self):
        crop = parse_crop('center', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 50))
        crop = parse_crop('right', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 50))

    def test_percent_crop(self):
        crop = parse_crop('50% 0%', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 0))
        crop = parse_crop('10% 80%', (500, 500), (400, 400))
        self.assertEqual(crop, (10, 80))

    def test_px_crop(self):
        crop = parse_crop('200px 33px', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 33))

    def test_bad_crop(self):
        self.assertRaises(ThumbnailError, parse_crop, '-200px', (500, 500), (400, 400))


class GeometryParserTestCase(unittest.TestCase):
    def test_geometry(self):
        g = parse_geometry('222x30')
        self.assertEqual(g, (222, 30))
        g = parse_geometry('222')
        self.assertEqual(g, (222, None))
        g = parse_geometry('x999')
        self.assertEqual(g, (None, 999))


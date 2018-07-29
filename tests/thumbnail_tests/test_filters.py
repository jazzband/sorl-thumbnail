# -*- coding: utf-8 -*-
import pytest
from django.template.loader import render_to_string

from tests.thumbnail_tests.utils import BaseTestCase


pytestmark = pytest.mark.django_db


class FilterTestCase(BaseTestCase):
    def test_html_filter(self):
        text = '<img alt="A image!" src="http://dummyimage.com/800x800" />'
        val = render_to_string('htmlfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '<img alt="A image!" '
            'src="/media/test/cache/0a/7b/0a7b030a1b690d12157b081444f6dd4d.jpg" />',
            val
        )

    def test_html_filter_local_url(self):
        text = '<img alt="A image!" src="/media/500x500.jpg" />'
        val = render_to_string('htmlfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '<img alt="A image!" '
            'src="/media/test/cache/6c/e5/6ce5cdfef5c75d469f7018d9eeda3acd.jpg" />',
            val
        )

    def test_markdown_filter(self):
        text = '![A image!](http://dummyimage.com/800x800)'
        val = render_to_string('markdownfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '![A image!](/media/test/cache/0a/7b/0a7b030a1b690d12157b081444f6dd4d.jpg)',
            val
        )

    def test_markdown_filter_local_url(self):
        text = '![A image!](/media/500x500.jpg)'
        val = render_to_string('markdownfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '![A image!](/media/test/cache/6c/e5/6ce5cdfef5c75d469f7018d9eeda3acd.jpg)',
            val
        )

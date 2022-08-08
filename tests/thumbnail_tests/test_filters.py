import pytest
from django.template.loader import render_to_string

from tests.thumbnail_tests.utils import BaseTestCase


pytestmark = pytest.mark.django_db


class FilterTestCase(BaseTestCase):
    def test_html_filter(self):
        text = '<img alt="A image!" src="https://dummyimage.com/800x800" />'
        val = render_to_string('htmlfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '<img alt="A image!" '
            'src="/media/test/cache/91/87/9187bfc1d52b271db9730ee0377547b9.jpg" />',
            val
        )

    def test_html_filter_local_url(self):
        text = '<img alt="A image!" src="/media/500x500.jpg" />'
        val = render_to_string('htmlfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '<img alt="A image!" '
            'src="/media/test/cache/c7/f2/c7f2880b48e9f07d46a05472c22f0fde.jpg" />',
            val
        )

    def test_markdown_filter(self):
        text = '![A image!](https://dummyimage.com/800x800)'
        val = render_to_string('markdownfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '![A image!](/media/test/cache/91/87/9187bfc1d52b271db9730ee0377547b9.jpg)',
            val
        )

    def test_markdown_filter_local_url(self):
        text = '![A image!](/media/500x500.jpg)'
        val = render_to_string('markdownfilter.html', {'text': text, }).strip()

        self.assertEqual(
            '![A image!](/media/test/cache/c7/f2/c7f2880b48e9f07d46a05472c22f0fde.jpg)',
            val
        )

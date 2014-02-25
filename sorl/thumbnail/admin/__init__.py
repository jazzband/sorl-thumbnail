try:
    from django.forms import ClearableFileInput
except ImportError:
    from .compat import AdminImageMixin # flake8: noqa
else:
    from .current import AdminImageMixin # flake8: noqa

AdminInlineImageMixin = AdminImageMixin # backwards compatibility


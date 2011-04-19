try:
    from django.forms import ClearableFileInput
except ImportError:
    from .compat import AdminImageMixin
else:
    from .current import AdminImageMixin

AdminInlineImageMixin = AdminImageMixin # backwards compatibility


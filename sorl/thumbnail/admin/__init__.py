try:
    from django.forms import ClearableFileInput
except ImportError:
    from .compat import AdminImageMixin, AdminInlineImageMixin
else:
    from .current import AdminImageMixin
    from .current import AdminImageMixin as AdminInlineImageMixin

